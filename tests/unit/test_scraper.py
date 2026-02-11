"""Unit tests for GoogleFlightsScraper class."""

from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
from google_flights_scraper import GoogleFlightsScraper

pytestmark = pytest.mark.unit

# Get today's date
today = datetime.today()
# Create Dates
start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

class TestInit:
    """Tests for initialization."""

    @patch('pandas.read_csv')
    def test_init_sets_browser_instances_to_none(self, mock_read_csv):
        """Test that browser instances are initially None."""
        scraper = GoogleFlightsScraper()

        assert scraper.playwright is None
        assert scraper.browser is None
        assert scraper.context is None
        assert scraper.page is None


class TestPageProperty:
    """Tests for _page property error handling."""

    @patch('pandas.read_csv')
    def test_page_property_raises_when_not_initialized(self, mock_read_csv):
        """Test that accessing _page before initialization raises error."""
        scraper = GoogleFlightsScraper()

        with pytest.raises(RuntimeError, match="Browser not initialized"):
            _ = scraper._page


class TestCalcPriceRel:
    """Tests for _calc_price_rel calculation logic."""

    @patch('pandas.read_csv')
    def test_calculates_price_relativity_correctly(self, mock_read_csv):
        """Test correct calculation of price relativity."""
        scraper = GoogleFlightsScraper()

        assert scraper._calc_price_rel(200, 50) == 0.2
        assert scraper._calc_price_rel(300, 100) == 0.25
        assert scraper._calc_price_rel(200, 0) == 0.0

    @patch('pandas.read_csv')
    def test_returns_none_when_inputs_none(self, mock_read_csv):
        """Test that None returned when inputs are None."""
        scraper = GoogleFlightsScraper()

        assert scraper._calc_price_rel(200, None) is None


class TestExportData:
    """Tests for export logic (file I/O)."""

    @patch('pandas.read_csv')
    def test_exports_json_with_indentation(self, mock_read_csv):
        """Test JSON export with correct formatting."""
        scraper = GoogleFlightsScraper()
        result = {"price": 250, "status": "success"}

        with patch('builtins.open', mock_open()) as mock_file:
            scraper._export_data(result, "output.json")

            mock_file.assert_called_once_with("output.json", "w")
            handle = mock_file()
            assert handle.write.called

    @patch('pandas.read_csv')
    @patch('pandas.json_normalize')
    def test_exports_csv_with_underscore_separator(self, mock_normalize, mock_read_csv):
        """Test CSV export uses underscore separator and no index."""
        scraper = GoogleFlightsScraper()
        result = {"price": 250, "nested": {"value": 100}}

        mock_df = MagicMock()
        mock_normalize.return_value = mock_df

        scraper._export_data(result, "output.csv")

        mock_normalize.assert_called_once_with(result, sep="_")
        mock_df.to_csv.assert_called_once_with("output.csv", index=False)


class TestCleanupLogic:
    """Tests for browser cleanup logic."""

    @pytest.mark.asyncio
    @patch('pandas.read_csv')
    @patch('google_flights_scraper.scraper.setup_browser', new_callable=AsyncMock)
    async def test_cleanup_happens_even_on_exception(self, mock_setup, mock_read_csv):
        """Test that browser cleanup happens even when scraping fails."""
        scraper = GoogleFlightsScraper()

        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        # All cleanup methods must be AsyncMock
        mock_playwright.stop = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_context.close = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.goto = AsyncMock()

        mock_setup.return_value = (mock_playwright, mock_browser, mock_context, mock_page)

        with patch.object(scraper, '_validate_inputs'), \
             patch.object(scraper, '_check_for_captcha', new_callable=AsyncMock), \
             patch('google_flights_scraper.scraper.asyncio.sleep', new_callable=AsyncMock), \
             patch.object(scraper, '_fill_search_form', new_callable=AsyncMock) as mock_fill:

            mock_fill.side_effect = Exception("Form error")

            result = await scraper.scrape_flight(
                "LAX", "USA", "SFO", "USA",
                start, end, "Economy"
            )

            mock_page.close.assert_called_once()
            mock_context.close.assert_called_once()
            mock_browser.close.assert_called_once()
            mock_playwright.stop.assert_called_once()

            assert "Error:" in result["status"]


class TestConditionalLogic:
    """Tests for conditional execution logic."""

    @pytest.mark.asyncio
    @patch('pandas.read_csv')
    @patch('google_flights_scraper.scraper.setup_browser', new_callable=AsyncMock)
    async def test_price_relativity_only_extracted_on_success(self, mock_setup, mock_read_csv):
        """Test that price relativity only extracted when status is 'Ran successfully.'"""
        scraper = GoogleFlightsScraper()

        mock_playwright = MagicMock()
        mock_playwright.stop = AsyncMock()
        mock_browser = MagicMock()
        mock_browser.close = AsyncMock()
        mock_context = MagicMock()
        mock_context.close = AsyncMock()
        mock_page = MagicMock()
        mock_page.close = AsyncMock()
        mock_page.goto = AsyncMock()

        mock_setup.return_value = (mock_playwright, mock_browser, mock_context, mock_page)

        with patch.object(scraper, '_validate_inputs'), \
             patch.object(scraper, '_check_for_captcha', new_callable=AsyncMock), \
             patch('google_flights_scraper.scraper.asyncio.sleep', new_callable=AsyncMock), \
             patch.object(scraper, '_fill_search_form', new_callable=AsyncMock), \
             patch.object(scraper, '_select_best_flights', new_callable=AsyncMock) as mock_select, \
             patch('google_flights_scraper.scraper.extract_price_relativity', new_callable=AsyncMock) as mock_extract:

            mock_select.return_value = ({}, "Error: No flights")

            await scraper.scrape_flight(
                "LAX", "USA", "SFO", "USA",
                start, end, "Economy"
            )

            mock_extract.assert_not_called()

    @pytest.mark.asyncio
    @patch('pandas.read_csv')
    @patch('google_flights_scraper.scraper.setup_browser', new_callable=AsyncMock)
    async def test_export_only_called_when_path_provided(self, mock_setup, mock_read_csv):
        """Test that export only happens when export_path is provided."""
        scraper = GoogleFlightsScraper()

        mock_playwright = MagicMock()
        mock_playwright.stop = AsyncMock()
        mock_browser = MagicMock()
        mock_browser.close = AsyncMock()
        mock_context = MagicMock()
        mock_context.close = AsyncMock()
        mock_page = MagicMock()
        mock_page.close = AsyncMock()
        mock_page.goto = AsyncMock()

        mock_setup.return_value = (mock_playwright, mock_browser, mock_context, mock_page)

        with patch.object(scraper, '_validate_inputs'), \
             patch.object(scraper, '_check_for_captcha', new_callable=AsyncMock), \
             patch('google_flights_scraper.scraper.asyncio.sleep', new_callable=AsyncMock), \
             patch.object(scraper, '_fill_search_form', new_callable=AsyncMock), \
             patch.object(scraper, '_select_best_flights', new_callable=AsyncMock) as mock_select, \
             patch.object(scraper, '_export_data') as mock_export:

            mock_select.return_value = ({}, "Ran successfully.")

            await scraper.scrape_flight(
                "LAX", "USA", "SFO", "USA",
                start, end, "Economy",
                export_path=None
            )

            mock_export.assert_not_called()


class TestCaptchaDetectedError:
    """Tests for CaptchaDetectedError exception and _check_for_captcha method."""

    def test_captcha_detected_error_is_importable(self):
        """Test that CaptchaDetectedError can be imported and is an Exception."""
        from google_flights_scraper.scraper import CaptchaDetectedError
        assert issubclass(CaptchaDetectedError, Exception)

    @pytest.mark.asyncio
    @patch('pandas.read_csv')
    async def test_check_for_captcha_raises_on_sorry_url(self, mock_read_csv):
        """Test that _check_for_captcha raises on /sorry/ URL pattern."""
        from google_flights_scraper.scraper import CaptchaDetectedError
        scraper = GoogleFlightsScraper()

        mock_page = MagicMock()
        mock_page.url = "https://www.google.com/sorry/index?hl=en"
        mock_page.title = AsyncMock(return_value="Google")
        scraper.page = mock_page

        with pytest.raises(CaptchaDetectedError, match="bot-detection URL pattern"):
            await scraper._check_for_captcha()

    @pytest.mark.asyncio
    @patch('pandas.read_csv')
    async def test_check_for_captcha_raises_on_unusual_traffic_title(self, mock_read_csv):
        """Test that _check_for_captcha raises when title contains 'unusual traffic'."""
        from google_flights_scraper.scraper import CaptchaDetectedError
        scraper = GoogleFlightsScraper()

        mock_page = MagicMock()
        mock_page.url = "https://www.google.com/travel/flights"
        mock_page.title = AsyncMock(return_value="Unusual Traffic Detected - Google")
        mock_page.locator.return_value.count = AsyncMock(return_value=0)
        scraper.page = mock_page

        with pytest.raises(CaptchaDetectedError, match="unusual traffic"):
            await scraper._check_for_captcha()

    @pytest.mark.asyncio
    @patch('pandas.read_csv')
    async def test_check_for_captcha_raises_on_recaptcha_element(self, mock_read_csv):
        """Test that _check_for_captcha raises when reCAPTCHA widget is present."""
        from google_flights_scraper.scraper import CaptchaDetectedError
        scraper = GoogleFlightsScraper()

        mock_page = MagicMock()
        mock_page.url = "https://www.google.com/travel/flights"
        mock_page.title = AsyncMock(return_value="Google Flights")
        mock_page.locator.return_value.count = AsyncMock(return_value=1)
        scraper.page = mock_page

        with pytest.raises(CaptchaDetectedError, match="reCAPTCHA widget"):
            await scraper._check_for_captcha()

    @pytest.mark.asyncio
    @patch('pandas.read_csv')
    async def test_check_for_captcha_passes_when_no_signals(self, mock_read_csv):
        """Test that _check_for_captcha does not raise when page is clean."""
        scraper = GoogleFlightsScraper()

        mock_page = MagicMock()
        mock_page.url = "https://www.google.com/travel/flights"
        mock_page.title = AsyncMock(return_value="Google Flights")
        mock_page.locator.return_value.count = AsyncMock(return_value=0)
        scraper.page = mock_page

        # Should not raise
        await scraper._check_for_captcha()

    @pytest.mark.asyncio
    @patch('pandas.read_csv')
    @patch('google_flights_scraper.scraper.setup_browser', new_callable=AsyncMock)
    async def test_captcha_error_propagates_out_of_scrape_flight(
        self, mock_setup, mock_read_csv
    ):
        """Test that CaptchaDetectedError re-raises out of scrape_flight."""
        from google_flights_scraper.scraper import CaptchaDetectedError
        scraper = GoogleFlightsScraper()

        mock_playwright = MagicMock()
        mock_playwright.stop = AsyncMock()
        mock_browser = MagicMock()
        mock_browser.close = AsyncMock()
        mock_context = MagicMock()
        mock_context.close = AsyncMock()
        mock_page = MagicMock()
        mock_page.close = AsyncMock()
        mock_page.goto = AsyncMock()

        mock_setup.return_value = (mock_playwright, mock_browser, mock_context, mock_page)

        with patch.object(scraper, '_validate_inputs'), \
             patch('google_flights_scraper.scraper.asyncio.sleep', new_callable=AsyncMock), \
             patch.object(
                 scraper, '_check_for_captcha',
                 new_callable=AsyncMock,
                 side_effect=CaptchaDetectedError("CAPTCHA detected"),
             ):
            with pytest.raises(CaptchaDetectedError):
                await scraper.scrape_flight(
                    "LAX", "USA", "SFO", "USA",
                    start, end, "Economy"
                )

    @pytest.mark.asyncio
    @patch('pandas.read_csv')
    @patch('google_flights_scraper.scraper.setup_browser', new_callable=AsyncMock)
    async def test_cleanup_happens_on_captcha_error(self, mock_setup, mock_read_csv):
        """Test that browser is cleaned up even when CaptchaDetectedError is raised."""
        from google_flights_scraper.scraper import CaptchaDetectedError
        scraper = GoogleFlightsScraper()

        mock_playwright = MagicMock()
        mock_playwright.stop = AsyncMock()
        mock_browser = MagicMock()
        mock_browser.close = AsyncMock()
        mock_context = MagicMock()
        mock_context.close = AsyncMock()
        mock_page = MagicMock()
        mock_page.close = AsyncMock()
        mock_page.goto = AsyncMock()

        mock_setup.return_value = (mock_playwright, mock_browser, mock_context, mock_page)

        with patch.object(scraper, '_validate_inputs'), \
             patch('google_flights_scraper.scraper.asyncio.sleep', new_callable=AsyncMock), \
             patch.object(
                 scraper, '_check_for_captcha',
                 new_callable=AsyncMock,
                 side_effect=CaptchaDetectedError("CAPTCHA detected"),
             ):
            with pytest.raises(CaptchaDetectedError):
                await scraper.scrape_flight(
                    "LAX", "USA", "SFO", "USA",
                    start, end, "Economy"
                )

        mock_page.close.assert_called_once()
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()

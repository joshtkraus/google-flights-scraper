"""Essential unit tests for GoogleFlightsScraper class - pure logic only."""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from google_flights_scraper import GoogleFlightsScraper


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

        # $50 saved on $200 ticket = 50/(200+50) = 0.2
        assert scraper._calc_price_rel(200, 50) == 0.2

        # $100 saved on $300 ticket = 100/(300+100) = 0.25
        assert scraper._calc_price_rel(300, 100) == 0.25

        # Edge case: 0 difference
        assert scraper._calc_price_rel(200, 0) == 0.0

    @patch('pandas.read_csv')
    def test_returns_none_when_inputs_none(self, mock_read_csv):
        """Test that None returned when inputs are None."""
        scraper = GoogleFlightsScraper()

        assert scraper._calc_price_rel(200, None) is None
        assert scraper._calc_price_rel(None, 50) is None
        assert scraper._calc_price_rel(None, None) is None


class TestExportData:
    """Tests for export logic (file I/O)."""

    @patch('pandas.read_csv')
    def test_exports_json_with_indentation(self, mock_read_csv):
        """Test JSON export with correct formatting."""
        scraper = GoogleFlightsScraper()
        result = {"price": 250, "status": "success"}

        with patch('builtins.open', mock_open()) as mock_file:
            scraper._export_data(result, "output.json")

            # Verify file opened for writing
            mock_file.assert_called_once_with("output.json", "w")

            # Verify content written
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

        # Verify json_normalize called with underscore separator
        mock_normalize.assert_called_once_with(result, sep="_")

        # Verify to_csv called without index
        mock_df.to_csv.assert_called_once_with("output.csv", index=False)


class TestCleanupLogic:
    """Tests for browser cleanup logic."""

    @patch('pandas.read_csv')
    @patch('google_flights_scraper.scraper.setup_browser')
    def test_cleanup_happens_even_on_exception(self, mock_setup, mock_read_csv):
        """Test that browser cleanup happens even when scraping fails."""
        scraper = GoogleFlightsScraper()

        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_setup.return_value = (mock_playwright, mock_browser, mock_context, mock_page)

        with patch.object(scraper, '_validate_inputs'), \
            patch.object(scraper, '_fill_search_form') as mock_fill:

            # Exception happens AFTER browser setup
            mock_fill.side_effect = Exception("Form error")

            result = scraper.scrape_flight(
                "LAX", "USA", "SFO", "USA",
                "03/15/2026", "03/22/2026", "Economy"
            )

            # Now cleanup should be called
            mock_page.close.assert_called_once()
            mock_context.close.assert_called_once()
            mock_browser.close.assert_called_once()
            mock_playwright.stop.assert_called_once()

            assert "Error:" in result["status"]


class TestConditionalLogic:
    """Tests for conditional execution logic."""

    @patch('pandas.read_csv')
    @patch('google_flights_scraper.scraper.setup_browser')
    def test_price_relativity_only_extracted_on_success(self, mock_setup, mock_read_csv):
        """Test that price relativity only extracted when status is 'Ran successfully.'"""
        scraper = GoogleFlightsScraper()

        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_setup.return_value = (mock_playwright, mock_browser, mock_context, mock_page)

        with patch.object(scraper, '_validate_inputs'), \
             patch.object(scraper, '_fill_search_form'), \
             patch.object(scraper, '_select_best_flights') as mock_select, \
             patch('google_flights_scraper.scraper.extract_price_relativity') as mock_extract:

            # Test failure case
            mock_select.return_value = ({}, "Error: No flights")

            scraper.scrape_flight(
                "LAX", "USA", "SFO", "USA",
                "03/15/2026", "03/22/2026", "Economy"
            )

            # Verify extract_price_relativity NOT called
            mock_extract.assert_not_called()

    @patch('pandas.read_csv')
    @patch('google_flights_scraper.scraper.setup_browser')
    def test_export_only_called_when_path_provided(self, mock_setup, mock_read_csv):
        """Test that export only happens when export_path is provided."""
        scraper = GoogleFlightsScraper()

        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_setup.return_value = (mock_playwright, mock_browser, mock_context, mock_page)

        with patch.object(scraper, '_validate_inputs'), \
             patch.object(scraper, '_fill_search_form'), \
             patch.object(scraper, '_select_best_flights') as mock_select, \
             patch.object(scraper, '_export_data') as mock_export:

            mock_select.return_value = ({}, "Ran successfully.")

            # Without export_path
            scraper.scrape_flight(
                "LAX", "USA", "SFO", "USA",
                "03/15/2026", "03/22/2026", "Economy",
                export_path=None
            )

            # Verify export NOT called
            mock_export.assert_not_called()

"""Unit tests for setup_browser function."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from google_flights_scraper.config_browser import setup_browser, DEFAULT_TIMEOUT

pytestmark = pytest.mark.unit


class TestSetupBrowser:
    """Tests for setup_browser function."""

    @pytest.fixture(autouse=True)
    def mock_stealth(self):
        """Patch Stealth for all tests in this class to prevent real application."""
        with patch('google_flights_scraper.config_browser.Stealth') as mock:
            mock_instance = MagicMock()
            mock_instance.apply_stealth_async = AsyncMock()
            mock.return_value = mock_instance
            yield mock

    @pytest.mark.asyncio
    @patch('google_flights_scraper.config_browser.async_playwright')
    async def test_returns_correct_objects(self, mock_async_playwright):
        """Test that setup_browser returns all 4 browser objects."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.route = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        playwright, browser, context, page = await setup_browser()

        assert playwright is mock_playwright
        assert browser is mock_browser
        assert context is mock_context
        assert page is mock_page

    @pytest.mark.asyncio
    @patch('google_flights_scraper.config_browser.async_playwright')
    async def test_chromium_launch_configuration(self, mock_async_playwright):
        """Test that Chromium is launched with correct headless mode and all args."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.route = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        await setup_browser()

        call_kwargs = mock_playwright.chromium.launch.call_args.kwargs
        assert call_kwargs['headless'] is False

        expected_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-gpu',
            '--start-maximized',
        ]
        for arg in expected_args:
            assert arg in call_kwargs['args']

    @pytest.mark.asyncio
    @patch('google_flights_scraper.config_browser.async_playwright')
    async def test_browser_context_configuration(self, mock_async_playwright):
        """Test that browser context is created with correct fingerprinting kwargs."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.route = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        await setup_browser()

        mock_browser.new_context.assert_called_once()
        _, kwargs = mock_browser.new_context.call_args

        # Viewport is a dict with width/height — no longer no_viewport=True
        assert "viewport" in kwargs
        assert "width" in kwargs["viewport"]
        assert "height" in kwargs["viewport"]

        # Device scale factor is set and positive
        assert "device_scale_factor" in kwargs
        assert kwargs["device_scale_factor"] > 0

        # User agent is populated
        assert "user_agent" in kwargs
        assert kwargs["user_agent"]

        # Locale is fixed as en-US
        assert kwargs["locale"] == "en-US"

        # Timezone is one of the known US timezones
        assert "timezone_id" in kwargs
        assert (
            kwargs["timezone_id"].startswith("America/")
            or kwargs["timezone_id"].startswith("Pacific/")
        )

    @pytest.mark.asyncio
    @patch('google_flights_scraper.config_browser.async_playwright')
    async def test_resource_blocking_routes(self, mock_async_playwright):
        """Test that all 3 resource blocking routes are configured."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.route = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        await setup_browser()

        assert mock_context.route.call_count == 3

        patterns = [call[0][0] for call in mock_context.route.call_args_list]
        assert any('png,jpg,jpeg,gif,svg,woff,woff2,mp4,webm' in p for p in patterns)
        assert any('analytics.google.com' in p for p in patterns)
        assert any('googletagmanager.com' in p for p in patterns)

    @pytest.mark.asyncio
    @patch('google_flights_scraper.config_browser.async_playwright')
    async def test_page_timeout_configuration(self, mock_async_playwright):
        """Test that page default timeout is set to DEFAULT_TIMEOUT."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.route = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        await setup_browser()

        mock_page.set_default_timeout.assert_called_once_with(DEFAULT_TIMEOUT)

    @pytest.mark.asyncio
    @patch('google_flights_scraper.config_browser.async_playwright')
    async def test_stealth_applied_to_page(self, mock_async_playwright, mock_stealth):
        """Test that stealth is applied to the page after creation."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.route = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        await setup_browser()

        mock_stealth.return_value.apply_stealth_async.assert_called_once_with(mock_page)


class TestHelperFunctions:
    """Tests for viewport, timezone, and user agent helper functions."""

    def test_get_random_viewport_profile_returns_valid_profile(self):
        """Test that get_random_viewport_profile returns a profile from VIEWPORT_PROFILES."""
        from google_flights_scraper.config_browser import (
            get_random_viewport_profile,
            VIEWPORT_PROFILES,
        )
        profile = get_random_viewport_profile()

        assert "width" in profile
        assert "height" in profile
        assert "device_scale_factor" in profile
        assert profile in VIEWPORT_PROFILES

    def test_get_random_viewport_profile_returns_copy(self):
        """Test that get_random_viewport_profile returns a copy, not the original dict."""
        from google_flights_scraper.config_browser import (
            get_random_viewport_profile,
            VIEWPORT_PROFILES,
        )
        profile = get_random_viewport_profile()
        profile["width"] = 9999

        # Mutation should not affect the source list
        assert all(p["width"] != 9999 for p in VIEWPORT_PROFILES)

    def test_get_random_timezone_returns_valid_timezone(self):
        """Test that get_random_timezone returns a timezone from US_TIMEZONES."""
        from google_flights_scraper.config_browser import get_random_timezone, US_TIMEZONES

        tz = get_random_timezone()
        assert tz in US_TIMEZONES

    def test_get_random_user_agent_returns_string(self):
        """Test that get_random_user_agent returns a non-empty string."""
        from google_flights_scraper.config_browser import get_random_user_agent

        ua = get_random_user_agent()
        assert isinstance(ua, str)
        assert len(ua) > 0

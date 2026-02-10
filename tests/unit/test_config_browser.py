"""Unit tests for setup_browser function."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from google_flights_scraper.config_browser import setup_browser, DEFAULT_TIMEOUT

pytestmark = pytest.mark.unit

class TestSetupBrowser:
    """Tests for setup_browser function."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.config_browser.async_playwright')
    async def test_returns_correct_objects(self, mock_async_playwright):
        """Test that setup_browser returns all 4 browser objects."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        # async_playwright() returns an async context manager - mock the chain
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
        assert call_kwargs['headless'] is True

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
        """Test that browser context is created with no_viewport=True."""
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
        assert kwargs["no_viewport"] is True
        assert "user_agent" in kwargs
        assert kwargs["user_agent"]

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

"""Unit tests for setup_browser function in config_browser.py."""

import pytest
from unittest.mock import MagicMock, patch
from google_flights_scraper.config_browser import setup_browser, DEFAULT_TIMEOUT


class TestSetupBrowser:
    """Tests for setup_browser function."""

    @patch('google_flights_scraper.config_browser.sync_playwright')
    def test_returns_correct_objects(self, mock_sync_playwright):
        """Test that setup_browser returns all 4 browser objects."""
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        # Execute
        playwright, browser, context, page = setup_browser()

        # Verify correct objects returned
        assert playwright is mock_playwright
        assert browser is mock_browser
        assert context is mock_context
        assert page is mock_page

    @patch('google_flights_scraper.config_browser.sync_playwright')
    def test_chromium_launch_configuration(self, mock_sync_playwright):
        """Test that Chromium is launched with correct headless mode and all args."""
        mock_playwright = MagicMock()
        mock_sync_playwright.return_value.start.return_value = mock_playwright

        # Execute
        setup_browser()

        # Verify launch configuration
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

    @patch('google_flights_scraper.config_browser.sync_playwright')
    def test_browser_context_configuration(self, mock_sync_playwright):
        """Test that browser context is created with no_viewport=True."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser

        # Execute
        setup_browser()

        # Verify context configuration
        mock_browser.new_context.assert_called_once_with(no_viewport=True)

    @patch('google_flights_scraper.config_browser.sync_playwright')
    def test_resource_blocking_routes(self, mock_sync_playwright):
        """Test that all 3 resource blocking routes are configured."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context

        # Execute
        setup_browser()

        # Verify 3 routes configured
        assert mock_context.route.call_count == 3

        # Get all route patterns
        route_calls = mock_context.route.call_args_list
        patterns = [call_obj[0][0] for call_obj in route_calls]

        # Verify expected patterns exist
        assert any('png,jpg,jpeg,gif,svg,woff,woff2,mp4,webm' in p for p in patterns)
        assert any('analytics.google.com' in p for p in patterns)
        assert any('googletagmanager.com' in p for p in patterns)

    @patch('google_flights_scraper.config_browser.sync_playwright')
    def test_route_handlers_abort_requests(self, mock_sync_playwright):
        """Test that route handlers call route.abort()."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context

        # Execute
        setup_browser()

        # Get the handler functions and test them
        route_calls = mock_context.route.call_args_list

        for call_obj in route_calls:
            handler = call_obj[0][1]
            mock_route = MagicMock()
            handler(mock_route)
            mock_route.abort.assert_called_once()

    @patch('google_flights_scraper.config_browser.sync_playwright')
    def test_page_timeout_configuration(self, mock_sync_playwright):
        """Test that page default timeout is set to DEFAULT_TIMEOUT."""
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        # Execute
        setup_browser()

        # Verify timeout set
        mock_page.set_default_timeout.assert_called_once_with(DEFAULT_TIMEOUT)

"""Unit tests for interaction functions in interactions.py."""

import pytest
import time
from unittest.mock import MagicMock, patch
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from google_flights_scraper.interactions import (
    enter_departure_airport,
    enter_arrival_airport,
    enter_airports,
    enter_departure_date,
    enter_return_date,
    enter_dates,
    select_seat_class,
    press_search_button,
    wait_until_stable,
    find_and_select_best_flight,
)


class TestEnterDepartureAirport:
    """Tests for enter_departure_airport function."""

    def test_enters_departure_airport_successfully(self):
        """Test successful departure airport entry."""
        mock_page = MagicMock()

        # Just let MagicMock handle the chain automatically
        enter_departure_airport(mock_page, "LAX")

        # Verify page.locator was called with correct selectors
        mock_page.locator.assert_any_call("input[aria-label='Where from?']")
        mock_page.locator.assert_any_call("input[aria-label*='Where else?']")

    def test_raises_exception_on_timeout(self):
        """Test that timeout raises exception with context."""
        mock_page = MagicMock()
        mock_from_input = MagicMock()
        mock_from_input.wait_for.side_effect = PlaywrightTimeoutError("timeout")
        mock_page.locator.return_value = mock_from_input

        with pytest.raises(Exception, match="Error entering departure airport"):
            enter_departure_airport(mock_page, "LAX")


class TestEnterArrivalAirport:
    """Tests for enter_arrival_airport function."""

    def test_enters_arrival_airport_successfully(self):
        """Test successful arrival airport entry."""
        mock_page = MagicMock()

        # Just let MagicMock handle the chain automatically
        enter_arrival_airport(mock_page, "SFO")

        # Verify page.locator was called with correct selectors
        mock_page.locator.assert_any_call("input[aria-label='Where to? ']")
        mock_page.locator.assert_any_call("input[aria-label*='Where to?']")


class TestEnterAirports:
    """Tests for enter_airports function."""

    @patch('google_flights_scraper.interactions.enter_departure_airport')
    @patch('google_flights_scraper.interactions.enter_arrival_airport')
    def test_calls_both_airport_functions(self, mock_arrival, mock_departure):
        """Test that both airport entry functions are called."""
        mock_page = MagicMock()

        enter_airports(mock_page, "LAX", "SFO")

        mock_departure.assert_called_once_with(mock_page, "LAX")
        mock_arrival.assert_called_once_with(mock_page, "SFO")


class TestEnterDepartureDate:
    """Tests for enter_departure_date function."""

    def test_enters_departure_date_successfully(self):
        """Test successful departure date entry."""
        mock_page = MagicMock()
        mock_dep_input = MagicMock()
        mock_dep_popup = MagicMock()

        # Mock the locator chain
        mock_page.locator.return_value.first = mock_dep_input
        mock_page.locator.return_value.nth.return_value = mock_dep_popup

        enter_departure_date(mock_page, "03/15/2026")

        # Verify interactions
        mock_dep_input.click.assert_called_once()
        mock_dep_popup.fill.assert_called_once_with("03/15/2026")


class TestEnterReturnDate:
    """Tests for enter_return_date function."""

    def test_enters_return_date_successfully(self):
        """Test successful return date entry."""
        mock_page = MagicMock()
        mock_ret_popup = MagicMock()

        mock_page.locator.return_value.nth.return_value = mock_ret_popup

        enter_return_date(mock_page, "03/22/2026")

        # Verify interactions
        mock_ret_popup.fill.assert_called_once_with("03/22/2026")
        assert mock_ret_popup.press.call_count == 2  # Enter pressed twice


class TestEnterDates:
    """Tests for enter_dates function."""

    @patch('google_flights_scraper.interactions.enter_departure_date')
    @patch('google_flights_scraper.interactions.enter_return_date')
    def test_calls_both_date_functions(self, mock_return, mock_departure):
        """Test that both date entry functions are called."""
        mock_page = MagicMock()

        enter_dates(mock_page, "03/15/2026", "03/22/2026")

        mock_departure.assert_called_once_with(mock_page, "03/15/2026")
        mock_return.assert_called_once_with(mock_page, "03/22/2026")


class TestSelectSeatClass:
    """Tests for select_seat_class function."""

    @patch('google_flights_scraper.interactions.SEAT_CLASS_OPTION_MAPPING', {
        True: {'economy (include basic)': 0, 'premium economy': 1},
        False: {'economy': 0, 'business': 1}
    })
    def test_selects_seat_class_domestic(self):
        """Test seat class selection for domestic flight."""
        mock_page = MagicMock()
        mock_dropdown = MagicMock()
        mock_listbox = MagicMock()
        mock_options = MagicMock()

        mock_page.locator.side_effect = lambda selector: {
            "div[role='combobox']:has(span[aria-label='Change seating class.'])": mock_dropdown,
            "ul[role='listbox']": mock_listbox,
        }.get(selector, MagicMock())

        mock_listbox.nth.return_value = mock_listbox
        mock_listbox.locator.return_value = mock_options

        select_seat_class(mock_page, "Economy (include Basic)", is_domestic_us=True)

        # Verify dropdown clicked
        mock_dropdown.click.assert_called_once()

        # Verify correct option selected (index 0)
        mock_options.nth.assert_called_with(0)

    @patch('google_flights_scraper.interactions.SEAT_CLASS_OPTION_MAPPING', {
        True: {'economy (include basic)': 0},
        False: {'economy': 0, 'business': 1}
    })
    def test_selects_seat_class_international(self):
        """Test seat class selection for international flight."""
        mock_page = MagicMock()
        mock_dropdown = MagicMock()
        mock_listbox = MagicMock()
        mock_options = MagicMock()

        mock_page.locator.side_effect = lambda selector: {
            "div[role='combobox']:has(span[aria-label='Change seating class.'])": mock_dropdown,
            "ul[role='listbox']": mock_listbox,
        }.get(selector, MagicMock())

        mock_listbox.nth.return_value = mock_listbox
        mock_listbox.locator.return_value = mock_options

        select_seat_class(mock_page, "Business", is_domestic_us=False)

        # Verify correct option selected (index 1)
        mock_options.nth.assert_called_with(1)


class TestPressSearchButton:
    """Tests for press_search_button function."""

    def test_clicks_search_button_successfully(self):
        """Test successful search button click."""
        mock_page = MagicMock()
        mock_button = MagicMock()

        mock_page.locator.return_value = mock_button

        press_search_button(mock_page)

        mock_button.wait_for.assert_called_once_with(state="visible")
        mock_button.click.assert_called_once()

    def test_raises_exception_on_timeout(self):
        """Test that timeout raises exception."""
        mock_page = MagicMock()
        mock_button = MagicMock()
        mock_button.wait_for.side_effect = PlaywrightTimeoutError("timeout")
        mock_page.locator.return_value = mock_button

        with pytest.raises(Exception, match="Error pressing search button"):
            press_search_button(mock_page)


class TestWaitUntilStable:
    """Tests for wait_until_stable function."""

    def test_waits_until_class_stable(self):
        """Test that function waits until class attribute stabilizes."""
        mock_page = MagicMock()
        mock_element = MagicMock()

        # Simulate class changing then stabilizing
        mock_element.count.return_value = 1
        mock_element.get_attribute.side_effect = [
            "class1",  # First read
            "class1",  # Same
            "class1",  # Same
            "class2",  # Changed
            "class2",  # Same
            "class2",  # Same (stable)
        ]

        mock_page.locator.return_value.nth.return_value = mock_element

        # Should complete without timeout
        wait_until_stable(mock_page, "div", stable_duration=0.2, timeout=5000)

    def test_raises_timeout_if_not_stable(self):
        """Test that TimeoutError raised if element never stabilizes."""
        mock_page = MagicMock()
        mock_element = MagicMock()

        # Simulate class constantly changing
        mock_element.count.return_value = 1
        call_count = [0]

        def changing_class(*args):
            call_count[0] += 1
            return f"class{call_count[0]}"

        mock_element.get_attribute.side_effect = changing_class
        mock_page.locator.return_value.nth.return_value = mock_element

        with pytest.raises(TimeoutError, match="did not stabilize"):
            wait_until_stable(mock_page, "div", stable_duration=0.2, timeout=1)

    def test_waits_for_element_to_appear(self):
        """Test that function waits for element to appear."""
        mock_page = MagicMock()
        mock_element = MagicMock()

        # Simulate element not existing, then appearing
        count_calls = [0]

        def element_appears():
            count_calls[0] += 1
            return 0 if count_calls[0] < 3 else 1

        mock_element.count.side_effect = element_appears
        mock_element.get_attribute.return_value = "stable-class"
        mock_page.locator.return_value.nth.return_value = mock_element

        # Should wait for element then stabilize
        wait_until_stable(mock_page, "div", stable_duration=0.2, timeout=5000)


class TestFindAndSelectBestFlight:
    """Tests for find_and_select_best_flight function."""

    @patch('google_flights_scraper.interactions.wait_until_stable')
    def test_finds_best_flight_successfully(self, mock_wait):
        """Test successful best flight selection."""
        mock_page = MagicMock()
        mock_list = MagicMock()
        mock_flight = MagicMock()

        # Mock the locator chain: ul[role='list'].nth(1).locator("li").nth(0)
        mock_page.locator.return_value.nth.return_value = mock_list
        mock_list.locator.return_value.nth.return_value = mock_flight

        result = find_and_select_best_flight(mock_page, timeout=10)

        # Verify wait_until_stable was called
        mock_wait.assert_called_once_with(
            mock_page,
            "div[role='progressbar']",
            stable_duration=2.0,
            timeout=10
        )

        # Verify best flight was found
        assert result is mock_flight

    @patch('google_flights_scraper.interactions.wait_until_stable')
    def test_returns_none_on_timeout(self, mock_wait):
        """Test that None is returned when flight not found."""
        mock_page = MagicMock()
        mock_page.locator.side_effect = PlaywrightTimeoutError("timeout")

        result = find_and_select_best_flight(mock_page, timeout=10)

        assert result is None

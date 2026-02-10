"""Unit tests for interaction functions."""

from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
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

pytestmark = pytest.mark.unit

# Get today's date
today = datetime.today()

class TestEnterDepartureAirport:
    """Tests for enter_departure_airport function."""

    @pytest.mark.asyncio
    async def test_enters_departure_airport_successfully(self):
        """Test successful departure airport entry."""
        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.clear = AsyncMock()
        mock_locator.fill = AsyncMock()
        mock_locator.press = AsyncMock()
        mock_locator.nth.return_value = mock_locator
        mock_page.locator.return_value = mock_locator

        await enter_departure_airport(mock_page, "LAX")

        mock_page.locator.assert_any_call("input[aria-label='Where from?']")
        mock_page.locator.assert_any_call("input[aria-label*='Where else?']")

    @pytest.mark.asyncio
    async def test_raises_exception_on_timeout(self):
        """Test that timeout raises exception with context."""
        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock(side_effect=PlaywrightTimeoutError("timeout"))
        mock_page.locator.return_value = mock_locator

        with pytest.raises(Exception, match="Error entering departure airport"):
            await enter_departure_airport(mock_page, "LAX")


class TestEnterArrivalAirport:
    """Tests for enter_arrival_airport function."""

    @pytest.mark.asyncio
    async def test_enters_arrival_airport_successfully(self):
        """Test successful arrival airport entry."""
        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.clear = AsyncMock()
        mock_locator.fill = AsyncMock()
        mock_locator.press = AsyncMock()
        mock_locator.nth.return_value = mock_locator
        mock_page.locator.return_value = mock_locator

        await enter_arrival_airport(mock_page, "SFO")

        mock_page.locator.assert_any_call("input[aria-label='Where to? ']")
        mock_page.locator.assert_any_call("input[aria-label*='Where to?']")


class TestEnterAirports:
    """Tests for enter_airports function."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.interactions.enter_departure_airport', new_callable=AsyncMock)
    @patch('google_flights_scraper.interactions.enter_arrival_airport', new_callable=AsyncMock)
    async def test_calls_both_airport_functions(self, mock_arrival, mock_departure):
        """Test that both airport entry functions are called."""
        mock_page = MagicMock()

        await enter_airports(mock_page, "LAX", "SFO")

        mock_departure.assert_called_once_with(mock_page, "LAX")
        mock_arrival.assert_called_once_with(mock_page, "SFO")


class TestEnterDepartureDate:
    """Tests for enter_departure_date function."""

    @pytest.mark.asyncio
    async def test_enters_departure_date_successfully(self):
        """Test successful departure date entry."""
        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.fill = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.nth.return_value = mock_locator
        mock_page.locator.return_value = mock_locator

        # Create Dates
        start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")

        await enter_departure_date(mock_page, start)

        mock_locator.fill.assert_called_once_with(start)


class TestEnterReturnDate:
    """Tests for enter_return_date function."""

    @pytest.mark.asyncio
    async def test_enters_return_date_successfully(self):
        """Test successful return date entry."""
        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock()
        mock_locator.fill = AsyncMock()
        mock_locator.press = AsyncMock()
        mock_locator.nth.return_value = mock_locator
        mock_page.locator.return_value = mock_locator

        # Create Dates
        end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

        await enter_return_date(mock_page, end)

        mock_locator.fill.assert_called_once_with(end)
        assert mock_locator.press.call_count == 2  # Enter pressed twice


class TestEnterDates:
    """Tests for enter_dates function."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.interactions.enter_departure_date', new_callable=AsyncMock)
    @patch('google_flights_scraper.interactions.enter_return_date', new_callable=AsyncMock)
    async def test_calls_both_date_functions(self, mock_return, mock_departure):
        """Test that both date entry functions are called."""
        mock_page = MagicMock()

        # Create Dates
        start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
        end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

        await enter_dates(mock_page, start, end)

        mock_departure.assert_called_once_with(mock_page, start)
        mock_return.assert_called_once_with(mock_page, end)


class TestSelectSeatClass:
    """Tests for select_seat_class function."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.interactions.SEAT_CLASS_OPTION_MAPPING', {
        True: {'economy (include basic)': 0, 'premium economy': 1},
        False: {'economy': 0, 'business': 1}
    })
    async def test_selects_seat_class_domestic(self):
        """Test seat class selection for domestic flight."""
        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.nth.return_value = mock_locator
        mock_locator.locator.return_value = mock_locator
        mock_page.locator.return_value = mock_locator

        await select_seat_class(mock_page, "Economy (include Basic)", is_domestic_us=True)

        # Verify dropdown clicked
        mock_locator.click.assert_called()
        # Verify correct option selected (index 0)
        mock_locator.nth.assert_any_call(0)

    @pytest.mark.asyncio
    @patch('google_flights_scraper.interactions.SEAT_CLASS_OPTION_MAPPING', {
        True: {'economy (include basic)': 0},
        False: {'economy': 0, 'business': 1}
    })
    async def test_selects_seat_class_international(self):
        """Test seat class selection for international flight."""
        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.nth.return_value = mock_locator
        mock_locator.locator.return_value = mock_locator
        mock_page.locator.return_value = mock_locator

        await select_seat_class(mock_page, "Business", is_domestic_us=False)

        # Verify correct option selected (index 1)
        mock_locator.nth.assert_any_call(1)


class TestPressSearchButton:
    """Tests for press_search_button function."""

    @pytest.mark.asyncio
    async def test_clicks_search_button_successfully(self):
        """Test successful search button click."""
        mock_page = MagicMock()
        mock_button = MagicMock()
        mock_button.wait_for = AsyncMock()
        mock_button.click = AsyncMock()
        mock_page.locator.return_value = mock_button

        await press_search_button(mock_page)

        mock_button.wait_for.assert_called_once_with(state="visible")
        mock_button.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_exception_on_timeout(self):
        """Test that timeout raises exception."""
        mock_page = MagicMock()
        mock_button = MagicMock()
        mock_button.wait_for = AsyncMock(side_effect=PlaywrightTimeoutError("timeout"))
        mock_page.locator.return_value = mock_button

        with pytest.raises(Exception, match="Error pressing search button"):
            await press_search_button(mock_page)


class TestWaitUntilStable:
    """Tests for wait_until_stable function."""

    @pytest.mark.asyncio
    async def test_waits_until_class_stable(self):
        """Test that function waits until class attribute stabilizes."""
        mock_page = MagicMock()
        mock_element = MagicMock()

        mock_element.count = AsyncMock(return_value=1)
        mock_element.get_attribute = AsyncMock(side_effect=[
            "class1",  # First read
            "class1",  # Same
            "class1",  # Same (stable after duration)
        ])
        mock_page.locator.return_value.nth.return_value = mock_element

        await wait_until_stable(mock_page, "div", stable_duration=0.2, timeout=5000)

    @pytest.mark.asyncio
    async def test_raises_timeout_if_not_stable(self):
        """Test that TimeoutError raised if element never stabilizes."""
        mock_page = MagicMock()
        mock_element = MagicMock()

        mock_element.count = AsyncMock(return_value=1)
        call_count = [0]

        async def changing_class(*args):
            call_count[0] += 1
            return f"class{call_count[0]}"

        mock_element.get_attribute = changing_class
        mock_page.locator.return_value.nth.return_value = mock_element

        with pytest.raises(TimeoutError, match="did not stabilize within 1000ms"):
            await wait_until_stable(mock_page, "div", stable_duration=0.2, timeout=1000)

    @pytest.mark.asyncio
    async def test_waits_for_element_to_appear(self):
        """Test that function waits for element to appear."""
        mock_page = MagicMock()
        mock_element = MagicMock()

        count_calls = [0]

        async def element_appears():
            count_calls[0] += 1
            return 0 if count_calls[0] < 3 else 1

        mock_element.count = element_appears
        mock_element.get_attribute = AsyncMock(return_value="stable-class")
        mock_page.locator.return_value.nth.return_value = mock_element

        await wait_until_stable(mock_page, "div", stable_duration=0.2, timeout=5000)


class TestFindAndSelectBestFlight:
    """Tests for find_and_select_best_flight function."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.interactions.wait_until_stable', new_callable=AsyncMock)
    async def test_finds_best_flight_successfully(self, mock_wait):
        """Test successful best flight selection."""
        mock_page = MagicMock()
        mock_list = MagicMock()
        mock_flight = MagicMock()

        mock_page.locator.return_value.nth.return_value = mock_list
        mock_list.locator.return_value.nth.return_value = mock_flight

        result = await find_and_select_best_flight(mock_page, timeout=10000)

        mock_wait.assert_called_once_with(
            mock_page,
            "div[role='progressbar']",
            stable_duration=2.0,
            timeout=10000
        )
        assert result is mock_flight

    @pytest.mark.asyncio
    @patch('google_flights_scraper.interactions.wait_until_stable', new_callable=AsyncMock)
    async def test_returns_none_on_timeout(self, mock_wait):
        """Test that None is returned when flight not found."""
        mock_page = MagicMock()
        mock_page.locator.side_effect = PlaywrightTimeoutError("timeout")

        result = await find_and_select_best_flight(mock_page, timeout=10000)

        assert result is None

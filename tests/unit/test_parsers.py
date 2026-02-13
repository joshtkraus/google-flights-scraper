"""Unit tests for parser functions."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from google_flights_scraper.parsers import (
    create_empty_flight_info,
    extract_airline,
    extract_departure_info,
    extract_arrival_info,
    extract_num_stops,
    extract_layover_info,
    total_layover_duration,
    extract_duration,
    extract_baggage_info,
    extract_flight_details,
    extract_final_price,
    parse_price_classification,
    parse_price_difference,
    extract_price_relativity,
)

pytestmark = pytest.mark.unit

class TestCreateEmptyFlightInfo:
    """Tests for create_empty_flight_info function."""

    def test_returns_correct_structure(self):
        """Test that all fields exist with correct initial values."""
        result = create_empty_flight_info()

        assert result["airline"] is None
        assert result["num_stops"] is None
        assert result["connection_airports"] == []
        assert result["layover_durations"] == []


class TestExtractAirline:
    """Tests for extract_airline function."""

    def test_extract_airline_success_and_failure(self):
        """Test airline extraction with valid and invalid inputs."""
        assert extract_airline("Depart flight with United.") == "United"
        assert extract_airline("Depart flight with American Airlines.") == "American Airlines"
        assert extract_airline("Invalid text") is None
        assert extract_airline("") is None


class TestExtractDepartureInfo:
    """Tests for extract_departure_info function."""

    def test_extract_departure_info(self):
        """Test departure info extraction."""
        desc = "Leaves Los Angeles International Airport at 10:30 AM on Monday, March 15"
        airport, time, date = extract_departure_info(desc)

        assert airport == "Los Angeles International Airport"
        assert time == "10:30 AM"
        assert date == "Monday, March 15"

        assert extract_departure_info("Invalid") == (None, None, None)


class TestExtractArrivalInfo:
    """Tests for extract_arrival_info function."""

    def test_extract_arrival_info(self):
        """Test arrival info extraction."""
        desc = "arrives at San Francisco International Airport at 2:30 PM on Monday, March 15"
        airport, time, date = extract_arrival_info(desc)

        assert airport == "San Francisco International Airport"
        assert time == "2:30 PM"
        assert date == "Monday, March 15"

        assert extract_arrival_info("Invalid") == (None, None, None)


class TestExtractNumStops:
    """Tests for extract_num_stops function."""

    def test_extract_num_stops(self):
        """Test stop counting for various cases."""
        assert extract_num_stops("Nonstop flight") == 0
        assert extract_num_stops("1 stop flight") == 1
        assert extract_num_stops("2 stop flight") == 2
        assert extract_num_stops("No info") is None


class TestExtractLayoverInfo:
    """Tests for extract_layover_info function."""

    def test_single_layover(self):
        """Test single layover extraction."""
        desc = "Layover (1 of 1) is a 2 hr 30 min layover at John F. Kennedy International Airport."
        airports, durations = extract_layover_info(desc)

        assert airports == ["John F Kennedy International Airport"]
        assert durations == ["2 hr 30 min"]

        total_layover_minutes = total_layover_duration(durations)
        assert total_layover_minutes == 150

    def test_multiple_layovers(self):
        """Test multiple layovers extraction."""
        desc = (
            "Layover (1 of 2) is a 2 hr layover at Atlanta. "
            "Layover (2 of 2) is a 1 hr 30 min layover in Denver."
        )
        airports, durations = extract_layover_info(desc)

        assert airports == ["Atlanta", "Denver"]
        assert durations == ["2 hr", "1 hr 30 min"]

        total_layover_minutes = total_layover_duration(durations)
        assert total_layover_minutes == 210

    def test_no_layover(self):
        """Test that no layover returns empty lists."""
        airports, durations = extract_layover_info("Nonstop")

        assert (airports, durations) == ([], [])

        total_layover_minutes = total_layover_duration(durations)
        assert total_layover_minutes == 0


class TestExtractDuration:
    """Tests for extract_duration function."""

    def test_extract_duration_variations(self):
        """Test duration extraction for all format variations."""
        assert extract_duration("Total duration 5 hr 30 min") == (330, "5 hr 30 min")
        assert extract_duration("Total duration 2 hr") == (120, "2 hr")
        assert extract_duration("Total duration 45 min") == (45, "45 min")
        assert extract_duration("No duration") == (None, None)


class TestExtractBaggageInfo:
    """Tests for extract_baggage_info function."""

    def test_extract_baggage_info(self):
        """Test baggage extraction for various cases."""
        assert extract_baggage_info("1 carry-on bag and 2 checked bags") == (1, 2)
        assert extract_baggage_info("1 carry-on bag") == (1, None)
        assert extract_baggage_info("2 checked bags") == (None, 2)
        assert extract_baggage_info("No baggage") == (None, None)


class TestExtractFlightDetails:
    """Tests for extract_flight_details function."""

    @pytest.mark.asyncio
    async def test_extract_complete_flight(self):
        """Test extraction of complete flight information."""
        mock_element = MagicMock()
        mock_desc_locator = MagicMock()

        flight_desc = (
            "Depart flight with United. "
            "Leaves Los Angeles International Airport at 10:30 AM on Saturday, June 15 and "
            "arrives at San Francisco International Airport at 12:00 PM on Saturday, June 15. "
            "Nonstop flight. "
            "Total duration 1 hr 30 min. "
            "1 carry-on bag."
        )

        mock_element.locator.return_value = mock_desc_locator
        mock_desc_locator.get_attribute = AsyncMock(return_value=flight_desc)

        result = await extract_flight_details(mock_element)

        assert result["airline"] == "United"
        assert result["departure_airport"] == "Los Angeles International Airport"
        assert result["num_stops"] == 0
        assert result["duration_minutes"] == 90
        assert result["carry_on_bags"] == 1

    @pytest.mark.asyncio
    async def test_handles_missing_data(self):
        """Test that missing aria-label returns empty flight info."""
        mock_element = MagicMock()
        mock_desc_locator = MagicMock()

        mock_element.locator.return_value = mock_desc_locator
        mock_desc_locator.get_attribute = AsyncMock(return_value=None)

        result = await extract_flight_details(mock_element)

        assert result["airline"] is None
        assert result["num_stops"] is None

    @pytest.mark.asyncio
    async def test_cleans_unicode_characters(self):
        """Test that unicode characters are properly cleaned."""
        mock_element = MagicMock()
        mock_desc_locator = MagicMock()

        flight_desc = "Depart\u202fflight\xa0with United."
        mock_element.locator.return_value = mock_desc_locator
        mock_desc_locator.get_attribute = AsyncMock(return_value=flight_desc)

        result = await extract_flight_details(mock_element)

        assert result["airline"] == "United"


class TestExtractFinalPrice:
    """Tests for extract_final_price function."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.parsers.wait_until_stable', new_callable=AsyncMock)
    async def test_extract_price_successfully(self, mock_wait):
        """Test successful price extraction."""
        mock_page = MagicMock()
        mock_page.mouse.wheel = AsyncMock()
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="250 US dollars")
        mock_page.locator.return_value.first = mock_element

        result = await extract_final_price(mock_page, timeout=10000)

        mock_element.wait_for.assert_called_once_with(state="visible", timeout=10000)
        assert result == 250

    @pytest.mark.asyncio
    @patch('google_flights_scraper.parsers.wait_until_stable', new_callable=AsyncMock)
    async def test_extract_price_with_comma(self, mock_wait):
        """Test price extraction with comma separator."""
        mock_page = MagicMock()
        mock_page.mouse.wheel = AsyncMock()
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="1,250 US dollars")
        mock_page.locator.return_value.first = mock_element

        result = await extract_final_price(mock_page, timeout=10000)

        assert result == 1250

    @pytest.mark.asyncio
    @patch('google_flights_scraper.parsers.wait_until_stable', new_callable=AsyncMock)
    async def test_extract_price_returns_none_on_timeout(self, mock_wait):
        """Test that None returned when price element not found."""
        mock_page = MagicMock()
        mock_page.mouse.wheel = AsyncMock()
        mock_page.mouse.wheel = AsyncMock()
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock(side_effect=PlaywrightTimeoutError("timeout"))
        mock_page.locator.return_value.first = mock_element

        result = await extract_final_price(mock_page, timeout=10000)

        assert result is None

    @pytest.mark.asyncio
    @patch('google_flights_scraper.parsers.wait_until_stable', new_callable=AsyncMock)
    async def test_extract_price_returns_none_when_regex_fails(self, mock_wait):
        """Test that None returned when aria-label doesn't match regex."""
        mock_page = MagicMock()
        mock_page.mouse.wheel = AsyncMock()
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="Invalid format")
        mock_page.locator.return_value.first = mock_element

        result = await extract_final_price(mock_page, timeout=10000)

        assert result is None


class TestParsePriceClassification:
    """Tests for parse_price_classification function."""

    def test_parse_classification(self):
        """Test parsing all classification types."""
        assert parse_price_classification("$200 is low for Economy") == "low"
        assert parse_price_classification("$500 is high for Business") == "high"
        assert parse_price_classification("$300 is typical") == "typical"
        assert parse_price_classification("$200 is LOW") == "low"
        assert parse_price_classification("") is None
        assert parse_price_classification("No classification") is None


class TestParsePriceDifference:
    """Tests for parse_price_difference function."""

    def test_parse_price_difference(self):
        """Test parsing price differences."""
        assert parse_price_difference("$50 cheaper than usual") == 50
        assert parse_price_difference("$1,200 cheaper") == 1200
        assert parse_price_difference("$200 is low") == 0
        assert parse_price_difference("$500 is high") == 0
        assert parse_price_difference("$300 is typical") == 0
        assert parse_price_difference("") is None

class TestExtractPriceRelativity:
    """Tests for extract_price_relativity function."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.parsers.wait_until_stable', new_callable=AsyncMock)
    async def test_extract_price_relativity_low_with_savings(self, mock_wait):
        """Test extraction of low price with savings."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.inner_text = AsyncMock(
            return_value="$200 is low for Economy. $50 cheaper than usual."
        )
        mock_page.locator.return_value.first = mock_element

        classification, amount = await extract_price_relativity(mock_page, timeout=10000)

        assert classification == "low"
        assert amount == 50

    @pytest.mark.asyncio
    @patch('google_flights_scraper.parsers.wait_until_stable', new_callable=AsyncMock)
    async def test_extract_price_relativity_high(self, mock_wait):
        """Test extraction of high price."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock()
        mock_element.inner_text = AsyncMock(return_value="$500 is high for Economy.")
        mock_page.locator.return_value.first = mock_element

        classification, amount = await extract_price_relativity(mock_page, timeout=10000)

        assert classification == "high"
        assert amount == 0

    @pytest.mark.asyncio
    @patch('google_flights_scraper.parsers.wait_until_stable', new_callable=AsyncMock)
    async def test_extract_price_relativity_returns_none_on_timeout(self, mock_wait):
        """Test that (None, None) returned when element not found."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_element.wait_for = AsyncMock(side_effect=PlaywrightTimeoutError("timeout"))
        mock_page.locator.return_value.first = mock_element

        classification, amount = await extract_price_relativity(mock_page, timeout=10000)

        assert classification is None
        assert amount is None

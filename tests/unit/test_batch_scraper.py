"""Essential unit tests for batch_scraper.py - pure logic only."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import pandas as pd
from google_flights_scraper.batch_scraper import (
    scrape_multiple_destinations,
    scrape_date_range,
    _flatten_result,
)


class TestFlattenResult:
    """Tests for _flatten_result helper function."""

    def test_flattens_complete_result(self):
        """Test flattening of complete result structure."""
        result = {
            "inputs": {
                "departure_airport": "LAX",
                "arrival_airport": "SFO",
            },
            "departure_flight": {
                "airline": "United",
                "num_stops": 0,
            },
            "return_flight": {
                "airline": "Delta",
                "num_stops": 1,
            },
            "price": 250,
            "price_classification": "low",
            "price_difference": 50,
            "price_relativity": 0.2,
            "status": "Ran successfully.",
            "url": "https://example.com",
        }

        flat = _flatten_result(result)

        # Check inputs flattened
        assert flat["departure_airport"] == "LAX"
        assert flat["arrival_airport"] == "SFO"

        # Check departure flight prefixed
        assert flat["departure_airline"] == "United"
        assert flat["departure_num_stops"] == 0

        # Check return flight prefixed
        assert flat["return_airline"] == "Delta"
        assert flat["return_num_stops"] == 1

        # Check price info
        assert flat["price"] == 250
        assert flat["price_classification"] == "low"
        assert flat["status"] == "Ran successfully."

    def test_handles_missing_sections(self):
        """Test that missing sections don't cause errors."""
        result = {
            "price": 300,
            "status": "Success",
        }

        flat = _flatten_result(result)

        # Should still work
        assert flat["price"] == 300
        assert flat["status"] == "Success"

    def test_preserves_lists_in_flight_info(self):
        """Test that list values are preserved (not flattened further)."""
        result = {
            "departure_flight": {
                "connection_airports": ["DFW", "ORD"],
                "layover_durations": ["2 hr", "1 hr 30 min"],
            },
            "return_flight": {},
        }

        flat = _flatten_result(result)

        # Lists should be preserved
        assert flat["departure_connection_airports"] == ["DFW", "ORD"]
        assert flat["departure_layover_durations"] == ["2 hr", "1 hr 30 min"]


class TestMultipleDestinationsValidation:
    """Tests for input validation in scrape_multiple_destinations."""

    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    def test_raises_error_when_arrival_codes_and_countries_length_mismatch(self, mock_scraper):
        """Test that ValueError raised when array lengths don't match."""
        with pytest.raises(ValueError, match="arrival_codes and arrival_countries must have same length"):
            scrape_multiple_destinations(
                "LAX", "USA",
                ["SFO", "SEA"],  # 2 items
                ["USA"],  # 1 item - mismatch!
                "03/15/2026", "03/22/2026",
                ["Economy", "Economy"],
            )

    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    def test_raises_error_when_arrival_codes_and_seat_classes_length_mismatch(self, mock_scraper):
        """Test that ValueError raised when seat classes length doesn't match."""
        with pytest.raises(ValueError, match="arrival_codes and seat_classes must have same length"):
            scrape_multiple_destinations(
                "LAX", "USA",
                ["SFO", "SEA"],  # 2 items
                ["USA", "USA"],  # 2 items
                "03/15/2026", "03/22/2026",
                ["Economy"],  # 1 item - mismatch!
            )


class TestMultipleDestinationsLogic:
    """Tests for scrape_multiple_destinations logic."""

    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    @patch('google_flights_scraper.batch_scraper.time.sleep')
    def test_applies_delay_between_searches(self, mock_sleep, mock_scraper_class):
        """Test that delay is applied between searches but not after last."""
        mock_scraper = MagicMock()
        mock_scraper.scrape_flight.return_value = {
            "inputs": {"departure_airport": "LAX"},
            "price": 200,
            "status": "Success",
        }
        mock_scraper_class.return_value = mock_scraper

        scrape_multiple_destinations(
            "LAX", "USA",
            ["SFO", "SEA", "PDX"],
            ["USA", "USA", "USA"],
            "03/15/2026", "03/22/2026",
            ["Economy", "Economy", "Economy"],
            delay_seconds=2.0
        )

        # Should sleep 2 times (after first and second, not after last)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(2.0)

    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    def test_sorts_by_price_relativity_descending(self, mock_scraper_class):
        """Test that results are sorted by price_relativity descending."""
        mock_scraper = MagicMock()

        # Return results with different price relativity
        mock_scraper.scrape_flight.side_effect = [
            {"inputs": {}, "price": 200, "price_relativity": 0.1, "status": "Success"},
            {"inputs": {}, "price": 150, "price_relativity": 0.3, "status": "Success"},
            {"inputs": {}, "price": 250, "price_relativity": 0.2, "status": "Success"},
        ]
        mock_scraper_class.return_value = mock_scraper

        df = scrape_multiple_destinations(
            "LAX", "USA",
            ["SFO", "SEA", "PDX"],
            ["USA", "USA", "USA"],
            "03/15/2026", "03/22/2026",
            ["Economy", "Economy", "Economy"],
            delay_seconds=0
        )

        # Should be sorted: 0.3, 0.2, 0.1
        assert df["price_relativity"].tolist() == [0.3, 0.2, 0.1]


class TestDateRangeGeneration:
    """Tests for date range generation logic."""

    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    @patch('google_flights_scraper.batch_scraper.time.sleep')
    def test_includes_trip_length_in_results(self, mock_sleep, mock_scraper_class):
        """Test that trip_length_days is added to flattened results."""
        mock_scraper = MagicMock()
        mock_scraper.scrape_flight.return_value = {
            "inputs": {},
            "price": 200,
            "status": "Success",
        }
        mock_scraper_class.return_value = mock_scraper

        df = scrape_date_range(
            "LAX", "USA", "SFO", "USA",
            "03/15/2026", "03/17/2026",
            min_trip_length=2, max_trip_length=2,
            seat_class="Economy",
            delay_seconds=0
        )

        # Should have trip_length_days column
        assert "trip_length_days" in df.columns


class TestErrorHandling:
    """Tests for error handling in batch functions."""

    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    def test_continues_after_error(self, mock_scraper_class, capsys):
        """Test that batch continues after individual scrape errors."""
        mock_scraper = MagicMock()

        # First succeeds, second fails, third succeeds
        mock_scraper.scrape_flight.side_effect = [
            {"inputs": {}, "price": 200, "status": "Success"},
            Exception("Network error"),
            {"inputs": {}, "price": 250, "status": "Success"},
        ]
        mock_scraper_class.return_value = mock_scraper

        df = scrape_multiple_destinations(
            "LAX", "USA",
            ["SFO", "SEA", "PDX"],
            ["USA", "USA", "USA"],
            "03/15/2026", "03/22/2026",
            ["Economy", "Economy", "Economy"],
            delay_seconds=0
        )

        # Should have 3 results (including failed one)
        assert len(df) == 3

        # Error printed to stderr
        captured = capsys.readouterr()
        assert "Error:" in captured.err


class TestCSVOutput:
    """Tests for CSV output functionality."""

    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    @patch('pandas.DataFrame.to_csv')
    def test_saves_csv_only_when_path_provided(self, mock_to_csv, mock_scraper_class):
        """Test that CSV saved when path provided, not saved when None."""
        mock_scraper = MagicMock()
        mock_scraper.scrape_flight.return_value = {
            "inputs": {},
            "price": 200,
        }
        mock_scraper_class.return_value = mock_scraper

        # With path - should save
        scrape_multiple_destinations(
            "LAX", "USA", ["SFO"], ["USA"],
            "03/15/2026", "03/22/2026", ["Economy"],
            output_path="results.csv", delay_seconds=0
        )
        mock_to_csv.assert_called_once_with("results.csv", index=False)

        # Without path - should not save
        mock_to_csv.reset_mock()
        scrape_multiple_destinations(
            "LAX", "USA", ["SFO"], ["USA"],
            "03/15/2026", "03/22/2026", ["Economy"],
            output_path=None, delay_seconds=0
        )
        mock_to_csv.assert_not_called()

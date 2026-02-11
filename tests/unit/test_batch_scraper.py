"""Essential unit tests for batch_scraper."""

from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import pandas as pd
from google_flights_scraper.batch_scraper import (
    scrape_multiple,
    _flatten_result,
)

pytestmark = pytest.mark.unit

# Get today's date
today = datetime.today()
# Create Dates
start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

class TestFlattenResult:
    """Tests for _flatten_result helper function - sync, no changes needed."""

    def test_flattens_complete_result(self):
        """Test flattening of complete result structure."""
        result = {
            "inputs": {"departure_airport": "LAX", "arrival_airport": "SFO"},
            "departure_flight": {"airline": "United", "num_stops": 0},
            "return_flight": {"airline": "Delta", "num_stops": 1},
            "price": 250,
            "price_classification": "low",
            "price_difference": 50,
            "price_relativity": 0.2,
            "status": "Ran successfully.",
            "url": "https://example.com",
        }

        flat = _flatten_result(result)

        assert flat["departure_airport"] == "LAX"
        assert flat["arrival_airport"] == "SFO"
        assert flat["departure_airline"] == "United"
        assert flat["departure_num_stops"] == 0
        assert flat["return_airline"] == "Delta"
        assert flat["return_num_stops"] == 1
        assert flat["price"] == 250
        assert flat["price_classification"] == "low"
        assert flat["status"] == "Ran successfully."

    def test_handles_missing_sections(self):
        """Test that missing sections don't cause errors."""
        result = {"price": 300, "status": "Success"}
        flat = _flatten_result(result)
        assert flat["price"] == 300
        assert flat["status"] == "Success"

    def test_preserves_lists_in_flight_info(self):
        """Test that list values are preserved."""
        result = {
            "departure_flight": {
                "connection_airports": ["DFW", "ORD"],
                "layover_durations": ["2 hr", "1 hr 30 min"],
            },
            "return_flight": {},
        }
        flat = _flatten_result(result)
        assert flat["departure_connection_airports"] == ["DFW", "ORD"]
        assert flat["departure_layover_durations"] == ["2 hr", "1 hr 30 min"]


class TestMultipleValidation:
    """Tests for input validation in scrape_multiple."""

    @pytest.mark.asyncio
    async def test_raises_error_when_arrival_codes_and_countries_length_mismatch(self):
        """Test that ValueError raised when array lengths don't match."""
        with pytest.raises(ValueError, match="arrival_codes and arrival_countries must have same length"):
            await scrape_multiple(
                "LAX", "USA",
                ["SFO", "SEA"],
                ["USA"],
                [start, start], [end, end],
                ["Economy", "Economy"],
            )

    @pytest.mark.asyncio
    async def test_raises_error_when_arrival_codes_and_seat_classes_length_mismatch(self):
        """Test that ValueError raised when seat classes length doesn't match."""
        with pytest.raises(ValueError, match="arrival_codes and seat_classes must have same length"):
            await scrape_multiple(
                "LAX", "USA",
                ["SFO", "SEA"],
                ["USA", "USA"],
                [start, start], [end, end],
                ["Economy"],
            )

    @pytest.mark.asyncio
    async def test_raises_error_when_start_dates_length_mismatch(self):
        """Test that ValueError raised when start_dates length doesn't match."""
        with pytest.raises(ValueError, match="arrival_codes and start_dates must have same length"):
            await scrape_multiple(
                "LAX", "USA",
                ["SFO", "SEA"],
                ["USA", "USA"],
                [start],
                [end, end],
                ["Economy", "Economy"],
            )

    @pytest.mark.asyncio
    async def test_raises_error_when_end_dates_length_mismatch(self):
        """Test that ValueError raised when end_dates length doesn't match."""
        with pytest.raises(ValueError, match="arrival_codes and end_dates must have same length"):
            await scrape_multiple(
                "LAX", "USA",
                ["SFO", "SEA"],
                ["USA", "USA"],
                [start, start],
                [end],
                ["Economy", "Economy"],
            )


class TestMultipleLogic:
    """Tests for scrape_multiple logic."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    @patch('google_flights_scraper.batch_scraper.asyncio.sleep', new_callable=AsyncMock)
    async def test_applies_delay_between_searches(self, mock_sleep, mock_scraper_class):
        """Test that delay is applied between searches but not after last."""
        mock_scraper = MagicMock()
        mock_scraper.scrape_flight = AsyncMock(return_value={
            "inputs": {"departure_airport": "LAX"},
            "price": 200,
            "status": "Success",
        })
        mock_scraper_class.return_value = mock_scraper

        await scrape_multiple(
            "LAX", "USA",
            ["SFO", "SEA", "PDX"],
            ["USA", "USA", "USA"],
            [start, start, start],
            [end, end, end],
            ["Economy", "Economy", "Economy"],
            delay_seconds=2.0,
            n_jobs=1,
        )

        # Should sleep 2 times (between first-second and second-third, not after last)
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    async def test_sorts_by_price_relativity_descending(self, mock_scraper_class):
        """Test that results are sorted by price_relativity descending."""
        mock_scraper = MagicMock()
        mock_scraper.scrape_flight = AsyncMock(side_effect=[
            {"inputs": {}, "price": 200, "price_relativity": 0.1, "status": "Success"},
            {"inputs": {}, "price": 150, "price_relativity": 0.3, "status": "Success"},
            {"inputs": {}, "price": 250, "price_relativity": 0.2, "status": "Success"},
        ])
        mock_scraper_class.return_value = mock_scraper

        df = await scrape_multiple(
            "LAX", "USA",
            ["SFO", "SEA", "PDX"],
            ["USA", "USA", "USA"],
            [start, start, start],
            [end, end, end],
            ["Economy", "Economy", "Economy"],
            delay_seconds=0,
            n_jobs=1,
        )

        assert df["price_relativity"].tolist() == [0.3, 0.2, 0.1]

    @pytest.mark.asyncio
    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    async def test_n_jobs_runs_concurrently(self, mock_scraper_class):
        """Test that n_jobs > 1 uses concurrent execution."""
        mock_scraper = MagicMock()
        mock_scraper.scrape_flight = AsyncMock(return_value={
            "inputs": {}, "price": 200, "status": "Success",
        })
        mock_scraper_class.return_value = mock_scraper

        df = await scrape_multiple(
            "LAX", "USA",
            ["SFO", "SEA", "PDX"],
            ["USA", "USA", "USA"],
            [start, start, start],
            [end, end, end],
            ["Economy", "Economy", "Economy"],
            n_jobs=3,
        )

        # All 3 should complete
        assert len(df) == 3
        assert mock_scraper.scrape_flight.call_count == 3


class TestErrorHandling:
    """Tests for error handling in batch functions."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    async def test_continues_after_error(self, mock_scraper_class, capsys):
        """Test that batch continues after individual scrape errors."""
        mock_scraper = MagicMock()
        mock_scraper.scrape_flight = AsyncMock(side_effect=[
            {"inputs": {}, "price": 200, "status": "Success"},
            Exception("Network error"),
            {"inputs": {}, "price": 250, "status": "Success"},
        ])
        mock_scraper_class.return_value = mock_scraper

        df = await scrape_multiple(
            "LAX", "USA",
            ["SFO", "SEA", "PDX"],
            ["USA", "USA", "USA"],
            [start, start, start],
            [end, end, end],
            ["Economy", "Economy", "Economy"],
            delay_seconds=0,
            n_jobs=1,
        )

        assert len(df) == 3

        captured = capsys.readouterr()
        assert "Error:" in captured.err


class TestCSVOutput:
    """Tests for CSV output functionality."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    @patch('pandas.DataFrame.to_csv')
    async def test_saves_csv_only_when_path_provided(self, mock_to_csv, mock_scraper_class):
        """Test that CSV saved when path provided, not saved when None."""
        mock_scraper = MagicMock()
        mock_scraper.scrape_flight = AsyncMock(return_value={
            "inputs": {}, "price": 200,
        })
        mock_scraper_class.return_value = mock_scraper

        # With path - should save
        await scrape_multiple(
            "LAX", "USA", ["SFO"], ["USA"],
            [start], [end], ["Economy"],
            output_path="results.csv", delay_seconds=0,
        )
        mock_to_csv.assert_called_once_with("results.csv", index=False)

        # Without path - should not save
        mock_to_csv.reset_mock()
        await scrape_multiple(
            "LAX", "USA", ["SFO"], ["USA"],
            [start], [end], ["Economy"],
            output_path=None, delay_seconds=0,
        )
        mock_to_csv.assert_not_called()


class TestCaptchaCancellation:
    """Tests for CAPTCHA detection and batch cancellation behaviour."""

    @pytest.mark.asyncio
    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    async def test_captcha_cancels_remaining_sequential_tasks(self, mock_scraper_class):
        """Test that after a CAPTCHA error, remaining queued tasks are cancelled."""
        from google_flights_scraper.scraper import CaptchaDetectedError

        mock_scraper = MagicMock()
        mock_scraper.scrape_flight = AsyncMock(side_effect=[
            {"inputs": {}, "price": 200, "status": "Success"},
            CaptchaDetectedError("CAPTCHA detected"),
            {"inputs": {}, "price": 250, "status": "Success"},  # should not run
        ])
        mock_scraper_class.return_value = mock_scraper

        df = await scrape_multiple(
            "LAX", "USA",
            ["SFO", "SEA", "PDX"],
            ["USA", "USA", "USA"],
            [start, start, start],
            [end, end, end],
            ["Economy", "Economy", "Economy"],
            delay_seconds=0,
            n_jobs=1,
        )

        assert len(df) == 3

        statuses = df["status"].tolist()
        # One task hits CAPTCHA
        assert any("CAPTCHA detected" in str(s) for s in statuses)
        # Third task is cancelled, not run
        assert any("Cancelled" in str(s) for s in statuses)
        # Third scrape_flight should never have been called
        assert mock_scraper.scrape_flight.call_count == 2

    @pytest.mark.asyncio
    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    async def test_captcha_task_gets_error_status(self, mock_scraper_class):
        """Test that the task hitting CAPTCHA gets 'Error: CAPTCHA detected' status."""
        from google_flights_scraper.scraper import CaptchaDetectedError

        mock_scraper = MagicMock()
        mock_scraper.scrape_flight = AsyncMock(side_effect=[
            CaptchaDetectedError("CAPTCHA detected"),
        ])
        mock_scraper_class.return_value = mock_scraper

        df = await scrape_multiple(
            "LAX", "USA",
            ["SFO"],
            ["USA"],
            [start],
            [end],
            ["Economy"],
            delay_seconds=0,
            n_jobs=1,
        )

        assert df.iloc[0]["status"] == "Error: CAPTCHA detected"

    @pytest.mark.asyncio
    @patch('google_flights_scraper.batch_scraper.GoogleFlightsScraper')
    async def test_cancelled_tasks_get_cancelled_status(self, mock_scraper_class):
        """Test that tasks skipped due to CAPTCHA get 'Cancelled:...' status."""
        from google_flights_scraper.scraper import CaptchaDetectedError

        mock_scraper = MagicMock()
        mock_scraper.scrape_flight = AsyncMock(side_effect=[
            CaptchaDetectedError("CAPTCHA detected"),
            {"inputs": {}, "price": 250, "status": "Success"},  # should not run
            {"inputs": {}, "price": 300, "status": "Success"},  # should not run
        ])
        mock_scraper_class.return_value = mock_scraper

        df = await scrape_multiple(
            "LAX", "USA",
            ["SFO", "SEA", "PDX"],
            ["USA", "USA", "USA"],
            [start, start, start],
            [end, end, end],
            ["Economy", "Economy", "Economy"],
            delay_seconds=0,
            n_jobs=1,
        )

        cancelled = df[df["status"].str.startswith("Cancelled", na=False)]
        assert len(cancelled) == 2
        assert all("CAPTCHA" in s for s in cancelled["status"])

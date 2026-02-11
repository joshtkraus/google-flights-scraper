"""Essential unit tests for jupyter_helper."""

from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock, patch
from google_flights_scraper.jupyter_helper import (
    _run_script,
    scrape_flight,
    scrape_multiple,
)

pytestmark = pytest.mark.unit

# Get today's date
today = datetime.today()
# Create Dates
start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

class TestRunScript:
    """Tests for _run_script subprocess execution - unchanged (still sync)."""

    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_executes_script_and_parses_json(self, mock_unlink, mock_tempfile, mock_run):
        """Test that script is executed and JSON is parsed."""
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.py'
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"price": 250, "status": "success"}'
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        result = _run_script('print("test")', parse_as_json=True)

        assert result == {"price": 250, "status": "success"}
        mock_unlink.assert_called_once_with('/tmp/test.py')

    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_returns_raw_text_when_parse_as_json_false(self, mock_unlink, mock_tempfile, mock_run):
        """Test that raw stdout returned when parse_as_json is False."""
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.py'
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'plain text output'
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        result = _run_script('print("test")', parse_as_json=False)

        assert result == 'plain text output'

    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_raises_exception_on_nonzero_return_code(self, mock_unlink, mock_tempfile, mock_run):
        """Test that exception raised when subprocess fails."""
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.py'
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = 'Error message'
        mock_run.return_value = mock_result

        with pytest.raises(Exception, match="Script execution failed"):
            _run_script('invalid script')

    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_cleans_up_temp_file_even_on_error(self, mock_unlink, mock_tempfile, mock_run):
        """Test that temp file is cleaned up even when execution fails."""
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.py'
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        try:
            _run_script('bad script')
        except Exception:
            pass

        mock_unlink.assert_called_once_with('/tmp/test.py')


class TestScrapeFlightScriptGeneration:
    """Tests for scrape_flight script generation."""

    @patch('google_flights_scraper.jupyter_helper._run_script')
    def test_generates_correct_script_with_all_parameters(self, mock_run_script):
        """Test that generated script contains asyncio.run and all parameters."""
        mock_run_script.return_value = {"price": 250}

        scrape_flight(
            "LAX", "USA", "SFO", "USA",
            start, end, "Economy"
        )

        script = mock_run_script.call_args[0][0]

        # Verify async structure
        assert "asyncio.run(main())" in script
        assert "async def main()" in script
        assert "await scraper.scrape_flight(" in script

        # Verify parameters
        assert 'departure_code="LAX"' in script
        assert 'arrival_code="SFO"' in script
        assert "json.dumps(result" in script

    @patch('google_flights_scraper.jupyter_helper._run_script')
    def test_handles_export_path_correctly(self, mock_run_script):
        """Test that export_path is handled correctly (None vs string)."""
        mock_run_script.return_value = {"price": 250}

        # Test with None
        scrape_flight("LAX", "USA", "SFO", "USA", start, end, "Economy", export_path=None)
        script_none = mock_run_script.call_args[0][0]
        assert "export_path=None" in script_none

        # Test with value
        scrape_flight("LAX", "USA", "SFO", "USA", start, end, "Economy", export_path="out.json")
        script_value = mock_run_script.call_args[0][0]
        assert 'export_path="out.json"' in script_value


class TestScrapeMultipleScriptGeneration:
    """Tests for scrape_multiple script generation."""

    @patch('google_flights_scraper.jupyter_helper._run_script')
    @patch('pandas.DataFrame')
    def test_passes_list_parameters_correctly(self, mock_df, mock_run_script):
        """Test that list parameters are correctly formatted in script."""
        mock_run_script.return_value = [{"price": 200}]

        scrape_multiple(
            "LAX", "USA",
            ["SFO", "SEA"],
            ["USA", "USA"],
            [start, start],
            [end, end],
            ["Economy", "Economy"]
        )

        script = mock_run_script.call_args[0][0]

        # Verify async structure
        assert "asyncio.run(main())" in script
        assert "await scrape_multiple(" in script

        # Verify list parameters
        assert "['SFO', 'SEA']" in script
        assert "['USA', 'USA']" in script
        assert "['Economy', 'Economy']" in script

    @patch('google_flights_scraper.jupyter_helper._run_script')
    @patch('pandas.DataFrame')
    def test_passes_n_jobs_parameter(self, mock_df, mock_run_script):
        """Test that n_jobs is correctly passed to script."""
        mock_run_script.return_value = [{"price": 200}]

        scrape_multiple(
            "LAX", "USA", ["SFO"], ["USA"],
            [start], [end], ["Economy"],
            n_jobs=3
        )

        script = mock_run_script.call_args[0][0]
        assert "n_jobs=3" in script

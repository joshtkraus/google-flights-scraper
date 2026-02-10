"""Helper for running scraper from Jupyter notebooks."""

import json
import os
import subprocess
import tempfile


def _run_script(script: str, parse_as_json: bool = True):
    """Helper function to run a Python script in a subprocess.

    Args:
        script (str): Python script to execute
        parse_as_json (bool): Whether to parse stdout as JSON

    Returns:
        Parsed JSON object or raw stdout string

    Raises:
        Exception: If script execution fails
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        temp_file = f.name

    try:
        result = subprocess.run(
            ["python", temp_file], capture_output=False, stdout=subprocess.PIPE, text=True
        )

        if result.stderr:
            print(result.stderr)

        if result.returncode != 0:
            raise Exception("Script execution failed")

        return json.loads(result.stdout) if parse_as_json else result.stdout

    finally:
        os.unlink(temp_file)


def scrape_flight(
    departure_code: str,
    departure_country: str,
    arrival_code: str,
    arrival_country: str,
    start_date: str,
    end_date: str,
    seat_class: str,
    export_path: str | None = None,
):
    """Run flight scraper in subprocess to avoid asyncio conflicts with Jupyter.

    Args:
        departure_code (str): IATA code or city for departure airport
        departure_country (str): Country for departure airport
        arrival_code (str): IATA code or city for arrival airport
        arrival_country (str): Country for arrival airport
        start_date (str): Departure date in MM/DD/YYYY format
        end_date (str): Return date in MM/DD/YYYY format
        seat_class (str): Seat class (e.g., "Economy (include Basic)")
        export_path (str | None): Optional path to export results (.json or .csv)

    Returns:
        dict: Flight scraping results
    """
    script = f"""
import asyncio
import json
from google_flights_scraper import GoogleFlightsScraper

async def main():
    scraper = GoogleFlightsScraper()
    result = await scraper.scrape_flight(
        departure_code="{departure_code}",
        departure_country="{departure_country}",
        arrival_code="{arrival_code}",
        arrival_country="{arrival_country}",
        start_date="{start_date}",
        end_date="{end_date}",
        seat_class="{seat_class}",
        export_path={f'"{export_path}"' if export_path else "None"}
    )
    print(json.dumps(result, default=str))

asyncio.run(main())
"""
    return _run_script(script)


def scrape_multiple_destinations(
    departure_code: str,
    departure_country: str,
    arrival_codes: list[str],
    arrival_countries: list[str],
    start_date: str,
    end_date: str,
    seat_classes: list[str],
    output_path: str | None = None,
    delay_seconds: float = 3.0,
    n_jobs: int = 1,
):
    """Scrape multiple destinations in subprocess to avoid asyncio conflicts with Jupyter.

    Args:
        departure_code (str): IATA code or city for departure airport
        departure_country (str): Country for departure airport
        arrival_codes (list[str]): List of IATA codes or cities for arrival airports
        arrival_countries (list[str]): List of countries (same length as arrival_codes)
        start_date (str): Departure date in MM/DD/YYYY format
        end_date (str): Return date in MM/DD/YYYY format
        seat_classes (list[str]): List of seat classes (same length as arrival_codes)
        output_path (str | None): Optional path to save CSV output
        delay_seconds (float): Delay between searches in seconds when n_jobs=1
        n_jobs (int): Number of concurrent scrapes (default 1)

    Returns:
        DataFrame: Results for all destinations
    """
    script = f"""
import asyncio
import json
from google_flights_scraper.batch_scraper import scrape_multiple_destinations

async def main():
    arrival_codes = {arrival_codes}
    arrival_countries = {arrival_countries}
    seat_classes = {seat_classes}

    df = await scrape_multiple_destinations(
        departure_code="{departure_code}",
        departure_country="{departure_country}",
        arrival_codes=arrival_codes,
        arrival_countries=arrival_countries,
        start_date="{start_date}",
        end_date="{end_date}",
        seat_classes=seat_classes,
        output_path={f'"{output_path}"' if output_path else "None"},
        delay_seconds={delay_seconds},
        n_jobs={n_jobs}
    )
    print(df.to_json(orient='records'))

asyncio.run(main())
"""
    import pandas as pd

    data = _run_script(script)
    return pd.DataFrame(data)


def scrape_date_range(
    departure_code: str,
    departure_country: str,
    arrival_code: str,
    arrival_country: str,
    start_date_range: str,
    end_date_range: str,
    min_trip_length: int,
    max_trip_length: int,
    seat_class: str,
    output_path: str | None = None,
    delay_seconds: float = 3.0,
    n_jobs: int = 1,
):
    """Scrape date range in subprocess to avoid asyncio conflicts with Jupyter.

    Args:
        departure_code (str): IATA code or city for departure airport
        departure_country (str): Country for departure airport
        arrival_code (str): IATA code or city for arrival airport
        arrival_country (str): Country for arrival airport
        start_date_range (str): Earliest departure date in MM/DD/YYYY format
        end_date_range (str): Latest possible return date in MM/DD/YYYY format
        min_trip_length (int): Minimum trip length in days
        max_trip_length (int): Maximum trip length in days
        seat_class (str): Seat class
        output_path (str | None): Optional path to save CSV output
        delay_seconds (float): Delay between searches in seconds when n_jobs=1
        n_jobs (int): Number of concurrent scrapes (default 1)

    Returns:
        DataFrame: Results for all date combinations
    """
    script = f"""
import asyncio
import json
from google_flights_scraper.batch_scraper import scrape_date_range

async def main():
    df = await scrape_date_range(
        departure_code="{departure_code}",
        departure_country="{departure_country}",
        arrival_code="{arrival_code}",
        arrival_country="{arrival_country}",
        start_date_range="{start_date_range}",
        end_date_range="{end_date_range}",
        min_trip_length={min_trip_length},
        max_trip_length={max_trip_length},
        seat_class="{seat_class}",
        output_path={f'"{output_path}"' if output_path else "None"},
        delay_seconds={delay_seconds},
        n_jobs={n_jobs}
    )
    print(df.to_json(orient='records'))

asyncio.run(main())
"""
    import pandas as pd

    data = _run_script(script)
    return pd.DataFrame(data)

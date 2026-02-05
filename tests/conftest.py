"""Fixtures for integration tests."""

import pytest

from datetime import datetime, timedelta
from google_flights_scraper import GoogleFlightsScraper

# Get today's date
today = datetime.today()


@pytest.fixture(scope="session")
def domestic_economy_basic():
    """Domestic flight from LAX to New York with Basic Economy class."""
    # Create Dates
    start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    return scraper.scrape_flight(
        departure_code="LAX",
        departure_country="United States of America",
        arrival_code="New York",
        arrival_country="United States of America",
        start_date=start,
        end_date=end,
        seat_class="Economy (include Basic)",
    )

@pytest.fixture(scope="session")
def domestic_economy_non_basic():
    """Domestic flight from ATL to SEA with non-Basic Economy class."""
    # Create Dates
    start = (today + timedelta(weeks=3)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    return scraper.scrape_flight(
        departure_code="ATL",
        departure_country="United States of America",
        arrival_code="SEA",
        arrival_country="United States of America",
        start_date=start,
        end_date=end,
        seat_class="Economy (exclude Basic)",
    )

@pytest.fixture(scope="session")
def domestic_premium_economy():
    """Domestic flight from New York to Chicago with Premium Economy class."""
    # Create Dates
    start = (today + timedelta(weeks=6)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=7)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    return scraper.scrape_flight(
        departure_code="New York",
        departure_country="United States of America",
        arrival_code="Chicago",
        arrival_country="United States of America",
        start_date=start,
        end_date=end,
        seat_class="Premium economy",
    )

@pytest.fixture(scope="session")
def domestic_business():
    """Domestic flight from LAX to SFO with Business class."""
    # Create Dates
    start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    return scraper.scrape_flight(
        departure_code="LAX",
        departure_country="United States of America",
        arrival_code="SFO",
        arrival_country="United States of America",
        start_date=start,
        end_date=end,
        seat_class="Business",
    )

@pytest.fixture(scope="session")
def domestic_first():
    """Domestic flight from Chicago to LAX with First class."""
    # Create Dates
    start = (today + timedelta(weeks=7)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=8)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    return scraper.scrape_flight(
        departure_code="Chicago",
        departure_country="United States of America",
        arrival_code="LAX",
        arrival_country="United States of America",
        start_date=start,
        end_date=end,
        seat_class="First",
    )

@pytest.fixture(scope="session")
def int_economy():
    """International flight from New York to London with Basic Economy class."""
    # Create Dates
    start = (today + timedelta(weeks=7)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=8)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    return scraper.scrape_flight(
        departure_code="New York",
        departure_country="United States of America",
        arrival_code="London",
        arrival_country="United Kingdom",
        start_date=start,
        end_date=end,
        seat_class="Economy",
    )

@pytest.fixture(scope="session")
def int_premium_economy():
    """International flight from New York to CDG with Premium Economy class."""
    # Create Dates
    start = (today + timedelta(weeks=9)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=10)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    return scraper.scrape_flight(
        departure_code="New York",
        departure_country="United States of America",
        arrival_code="CDG",
        arrival_country="France",
        start_date=start,
        end_date=end,
        seat_class="Premium economy",
    )

@pytest.fixture(scope="session")
def int_business():
    """International flight from LAX to London with Business class."""
    # Create Dates
    start = (today + timedelta(weeks=10)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=12)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    return scraper.scrape_flight(
        departure_code="LAX",
        departure_country="United States of America",
        arrival_code="London",
        arrival_country="United Kingdom",
        start_date=start,
        end_date=end,
        seat_class="Business",
    )

@pytest.fixture(scope="session")
def int_first():
    """International flight from SFO to TPE with First class."""
    # Create Dates
    start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    return scraper.scrape_flight(
        departure_code="SFO",
        departure_country="United States of America",
        arrival_code="TPE",
        arrival_country="Taiwan",
        start_date=start,
        end_date=end,
        seat_class="First",
    )

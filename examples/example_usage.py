"""Example usage script for Google Flights Scraper."""

import json
from datetime import datetime, timedelta

from google_flights_scraper import GoogleFlightsScraper

# Get today's date
today = datetime.today()


def example_basic_search():
    """Example of a basic flight search from LAX to JFK in Economy class."""
    # Create Dates
    start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    result = scraper.scrape_flight(
        departure_code="LAX",
        arrival_code="JFK",
        start_date=start,
        end_date=end,
        seat_class="Economy (include Basic)",
    )

    print(json.dumps(result, indent=2))


def example_international_search():
    """Example of an international flight search from JFK to LHR in Premium Economy class."""
    # Create Dates
    start = (today + timedelta(weeks=8)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=10)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    result = scraper.scrape_flight(
        departure_code="JFK",
        arrival_code="LHR",
        start_date=start,
        end_date=end,
        seat_class="Premium economy",
    )

    print(json.dumps(result, indent=2))


def example_business_class():
    """Example of a business class flight search from SFO to MIA."""
    # Create Dates
    start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    result = scraper.scrape_flight(
        departure_code="SFO",
        arrival_code="MIA",
        start_date=start,
        end_date=end,
        seat_class="Business",
    )

    print(json.dumps(result, indent=2))


def example_save_to_file():
    """Example of saving flight search results to a JSON file."""
    # Create Dates
    start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    json_output = scraper.scrape_flight(
        departure_code="MIA",
        arrival_code="SEA",
        start_date=start,
        end_date=end,
        seat_class="Economy (include Basic)",
        export=True,
        export_type="json",
        export_path="examples/output/flight_results.json",
    )

    print(json_output)


def example_batch_processing():
    """Example of processing multiple flight routes in a batch."""
    # Create Dates
    start_1 = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
    end_1 = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

    start_2 = (today + timedelta(weeks=8)).strftime("%m/%d/%Y")
    end_2 = (today + timedelta(weeks=9)).strftime("%m/%d/%Y")

    start_3 = (today + timedelta(weeks=12)).strftime("%m/%d/%Y")
    end_3 = (today + timedelta(weeks=13)).strftime("%m/%d/%Y")

    routes = [
        ("LAX", "JFK", start_1, end_1, "Economy (include Basic)"),
        ("SFO", "BOS", start_2, end_2, "Business"),
        ("SEA", "ATL", start_3, end_3, "Premium economy"),
    ]

    all_results = []
    for i, (dep, arr, start, end, seat_class) in enumerate(routes, 1):
        print(f"\nProcessing route {i}/{len(routes)}: {dep} -> {arr}")
        scraper = GoogleFlightsScraper()
        result = scraper.scrape_flight(dep, arr, start, end, seat_class)
        all_results.append(result)
        print(f"Completed: {dep} to {arr}")

    # Save all results
    with open("examples/output/all_flights.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print(json.dumps(all_results, indent=2))


def example_custom_configuration():
    """Example of customizing scraper configuration."""
    # Create Dates
    start = (today + timedelta(weeks=4)).strftime("%m/%d/%Y")
    end = (today + timedelta(weeks=5)).strftime("%m/%d/%Y")

    scraper = GoogleFlightsScraper()

    # Increase wait time and retries for slower connections
    scraper.wait_time = 20

    result = scraper.scrape_flight(
        departure_code="LAX",
        arrival_code="HNL",
        start_date=start,
        end_date=end,
        seat_class="Economy (exclude Basic)",
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    # Basic search
    example_basic_search()

    # International flight
    example_international_search()

    # Business class
    example_business_class()

    # Save to file
    example_save_to_file()

    # Batch processing
    example_batch_processing()

    # Custom configuration
    example_custom_configuration()

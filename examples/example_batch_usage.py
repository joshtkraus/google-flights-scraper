"""Example usage of batch scraper functions."""

from google_flights_scraper.batch_scraper import (
    scrape_multiple_destinations,
    scrape_date_range,
)

from datetime import datetime, timedelta

# Get today's date
today = datetime.today()

# Example 1: Destination Search
# Search multiple destinations from RDU with fixed dates
city_search = {
    "SEA": {
        "country": "United States of America",
        "seat_class": "Economy (exclude Basic)"
    },
    "London": {
        "country": "United Kingdom",
        "seat_class": "Economy"
    },
    "Paris": {
        "country": "France",
        "seat_class": "Economy"
    },
    "SFO": {
        "country": "United States of America",
        "seat_class": "Economy (exclude Basic)"
    },
}

destination_codes = list(city_search.keys())
destination_countries = [city_search[code]["country"] for code in destination_codes]
seat_classes = [city_search[code]["seat_class"] for code in destination_codes]

# Create Dates
start = (today + timedelta(weeks=8)).strftime("%m/%d/%Y")
end = (today + timedelta(weeks=10)).strftime("%m/%d/%Y")

df_destinations = scrape_multiple_destinations(
    departure_code="RDU",
    departure_country="United States of America",
    arrival_codes=destination_codes,
    arrival_countries=destination_countries,
    start_date=start,
    end_date=end,
    seat_classes=seat_classes,
    output_path="examples/output/destination_search_results.csv",
    delay_seconds=3.0,
)


# Example 2: Date Range Search
# Search all date combinations for a specific route

# Create Dates
start = (today + timedelta(weeks=11)).strftime("%m/%d/%Y")
end = (today + timedelta(weeks=13)).strftime("%m/%d/%Y")

df_dates = scrape_date_range(
    departure_code="RDU",
    departure_country="United States of America",
    arrival_code="London",
    arrival_country="United Kingdom",
    start_date_range=start,
    end_date_range=end,
    min_trip_length=5,
    max_trip_length=7,
    seat_class="Economy",
    output_path="examples/output/date_range_results.csv",
    delay_seconds=3.0,
)


# Example 3: Weekend Getaway Search
# Search for weekend trips (Fri-Sun or Fri-Mon) over multiple weekends


# Create Dates
start = (today + timedelta(weeks=6)).strftime("%m/%d/%Y")
end = (today + timedelta(weeks=10)).strftime("%m/%d/%Y")

df_weekends = scrape_date_range(
    departure_code="RDU",
    departure_country="United States of America",
    arrival_code="New York",
    arrival_country="United States of America",
    start_date_range=start,
    end_date_range=end,
    min_trip_length=2,
    max_trip_length=3,
    seat_class="Economy (exclude Basic)",
    output_path="examples/output/weekend_getaways.csv",
    delay_seconds=3.0,
)

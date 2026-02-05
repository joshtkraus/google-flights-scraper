"""Batch scraping functions for Google Flights scraper."""

import time
from datetime import datetime, timedelta

import pandas as pd

from .scraper import GoogleFlightsScraper


def scrape_multiple_destinations(
    departure_code: str,
    departure_country: str,
    arrival_codes: list[str],
    arrival_countries: list[str],
    start_date: str,
    end_date: str,
    seat_classes: list[str],
    output_path: str,
    delay_seconds: float = 3.0,
):
    """Scrape multiple destinations with fixed dates.

    Args:
        departure_code (str): IATA code or city for departure airport
        departure_country (str): Country for departure airport
        arrival_codes (list[str]): List of IATA codes or cities for arrival airports
        arrival_countries (list[str]): List of countries (same length as arrival_codes)
        start_date (str): Departure date in MM/DD/YYYY format
        end_date (str): Return date in MM/DD/YYYY format
        seat_classes (list[str]): List of seat classes (same length as arrival_codes)
        output_path (str): Path to save CSV output
        delay_seconds (float): Delay between searches in seconds (default 3.0)

    Returns:
        DataFrame: Results for all destinations

    Raises:
        ValueError: If arrival_codes, arrival_countries, and seat_classes are not the same length
    """
    if len(arrival_codes) != len(arrival_countries):
        raise ValueError("arrival_codes and arrival_countries must have same length")

    if len(arrival_codes) != len(seat_classes):
        raise ValueError("arrival_codes and seat_classes must have same length")

    results = []
    total = len(arrival_codes)

    for i, (arrival_code, arrival_country, seat_class) in enumerate(
        zip(arrival_codes, arrival_countries, seat_classes, strict=True), 1
    ):
        print(f"[{i}/{total}] Searching {departure_code} → {arrival_code} ({seat_class})...")

        try:
            scraper = GoogleFlightsScraper()
            result = scraper.scrape_flight(
                departure_code=departure_code,
                departure_country=departure_country,
                arrival_code=arrival_code,
                arrival_country=arrival_country,
                start_date=start_date,
                end_date=end_date,
                seat_class=seat_class,
            )

            # Flatten the result dict for CSV
            flat_result = _flatten_result(result)
            results.append(flat_result)

        except Exception as e:
            print(f"  Error: {e}")
            # Add a failed result
            results.append({
                "departure_airport": departure_code,
                "departure_country": departure_country,
                "arrival_airport": arrival_code,
                "arrival_country": arrival_country,
                "departure_date": start_date,
                "return_date": end_date,
                "seat_class": seat_class,
                "status": f"Error: {str(e)}",
                "price": None,
            })

        # Delay before next search (except after last one)
        if i < total and delay_seconds > 0:
            time.sleep(delay_seconds)

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Sort by price_relativity (largest to smallest, NAs last)
    if "price_relativity" in df.columns:
        df = df.sort_values("price_relativity", ascending=False, na_position="last")

    # Save to CSV
    df.to_csv(output_path, index=False)
    successful = df["status"].str.contains("success", case=False, na=False).sum()
    print(f"Total searches: {total}, Successful: {successful}")

    return df


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
    output_path: str,
    delay_seconds: float = 3.0,
):
    """Scrape all date combinations within a date range.

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
        output_path (str): Path to save CSV output
        delay_seconds (float): Delay between searches in seconds (default 3.0)

    Returns:
        DataFrame: Results for all date combinations
    """
    # Parse dates
    start_range = datetime.strptime(start_date_range, "%m/%d/%Y")
    end_range = datetime.strptime(end_date_range, "%m/%d/%Y")

    # Generate all valid date combinations
    date_combinations = []
    current_departure = start_range

    while current_departure <= end_range:
        for trip_length in range(min_trip_length, max_trip_length + 1):
            return_date = current_departure + timedelta(days=trip_length)

            # Only include if return date is within range
            if return_date <= end_range:
                date_combinations.append({
                    "departure": current_departure.strftime("%m/%d/%Y"),
                    "return": return_date.strftime("%m/%d/%Y"),
                    "trip_length": trip_length,
                })

        current_departure += timedelta(days=1)

    results = []
    total = len(date_combinations)

    for i, combo in enumerate(date_combinations, 1):
        print(f"[{i}/{total}] Searching {combo['departure']} → {combo['return']}...")
        try:
            scraper = GoogleFlightsScraper()
            result = scraper.scrape_flight(
                departure_code=departure_code,
                departure_country=departure_country,
                arrival_code=arrival_code,
                arrival_country=arrival_country,
                start_date=str(combo["departure"]),
                end_date=str(combo["return"]),
                seat_class=seat_class,
            )

            # Flatten the result dict for CSV
            flat_result = _flatten_result(result)
            flat_result["trip_length_days"] = combo["trip_length"]
            results.append(flat_result)

        except Exception as e:
            print(f"  Error: {e}")
            # Add a failed result
            results.append({
                "departure_airport": departure_code,
                "departure_country": departure_country,
                "arrival_airport": arrival_code,
                "arrival_country": arrival_country,
                "departure_date": combo["departure"],
                "return_date": combo["return"],
                "trip_length_days": combo["trip_length"],
                "seat_class": seat_class,
                "status": f"Error: {str(e)}",
                "price": None,
            })

        # Delay before next search (except after last one)
        if i < total and delay_seconds > 0:
            time.sleep(delay_seconds)

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Sort by price_relativity (largest to smallest, NAs last)
    if "price_relativity" in df.columns:
        df = df.sort_values("price_relativity", ascending=False, na_position="last")

    # Save to CSV
    df.to_csv(output_path, index=False)
    successful = df["status"].str.contains("success", case=False, na=False).sum()
    print(f"Total searches: {total}, Successful: {successful}")

    return df


def _flatten_result(result: dict) -> dict:
    """Flatten nested result dictionary for CSV export.

    Args:
        result (dict): Result dictionary from scraper

    Returns:
        dict: Flattened dictionary
    """
    flat = {}

    # Add input info
    if "inputs" in result:
        for key, value in result["inputs"].items():
            flat[key] = value

    # Add departure flight info
    if "departure_flight" in result:
        for key, value in result["departure_flight"].items():
            flat[f"departure_{key}"] = value

    # Add return flight info
    if "return_flight" in result:
        for key, value in result["return_flight"].items():
            flat[f"return_{key}"] = value

    # Add price and status info
    flat["price"] = result.get("price")
    flat["price_classification"] = result.get("price_classification")
    flat["price_relativity"] = result.get("price_relativity")
    flat["status"] = result.get("status")

    return flat

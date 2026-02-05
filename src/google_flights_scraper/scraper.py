"""Main scraper orchestration class."""

import json
import os
import time
from pathlib import Path

import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait

from .config_browser import DEFAULT_WAIT_TIME, setup_chrome_driver
from .interactions import (
    enter_airports,
    enter_dates,
    find_and_select_best_flight,
    press_search_button,
    select_seat_class,
)
from .parsers import create_empty_flight_info, extract_flight_details, extract_price_relativity
from .validators import (
    is_domestic_us_flight,
    validate_airport_code,
    validate_dates,
    validate_export_params,
    validate_seat_class,
)


class GoogleFlightsScraper:
    """Web scraper for Google Flights."""

    def __init__(self):
        """Initialize the scraper with airport codes data."""
        package_dir = Path(__file__).parent.parent.parent
        csv_path = package_dir / "data" / "airport_codes.csv"
        self.airport_codes_df = pd.read_csv(csv_path)
        self.driver = setup_chrome_driver(headless=True)
        # Use longer timeouts in CI
        self.wait_time = 30 if os.getenv("CI") else DEFAULT_WAIT_TIME
        self.wait = WebDriverWait(self.driver, self.wait_time)

    def _create_result_structure(
        self,
        departure_code: str,
        departure_country: str,
        arrival_code: str,
        arrival_country: str,
        start_date: str,
        end_date: str,
        seat_class: str,
    ):
        """Create the initial result structure for storing flight data.

        Args:
            departure_code (str): IATA code or cirty for departure airport
            departure_country (str): Country of departure airport or city
            arrival_code (str): IATA code or city for arrival airport
            arrival_country (str): Country of arrival airport or city
            start_date (str): Departure date in MM/DD/YYYY format
            end_date (str): Return date in MM/DD/YYYY format
            seat_class (str): Seat class string

        Returns:
            dict: Empty result structure
        """
        return {
            "inputs": {
                "departure_airport": departure_code,
                "departure_country": departure_country,
                "arrival_airport": arrival_code,
                "arrival_country": arrival_country,
                "departure_date": start_date,
                "return_date": end_date,
                "seat_class": seat_class,
            },
            "departure_flight": create_empty_flight_info(),
            "return_flight": create_empty_flight_info(),
            "price": None,
            "price_classification": None,
            "price_relativity": None,
            "status": None,
        }

    def _validate_inputs(
        self,
        departure_code: str,
        departure_country: str,
        arrival_code: str,
        arrival_country: str,
        seat_class: str,
        start_date: str,
        end_date: str,
        export: bool,
        export_type: str | None,
        export_path: str | None,
    ):
        """Validate all input parameters.

        Args:
            departure_code (str): IATA code or city for departure airport
            departure_country (str): Country for departure airport
            arrival_code (str): IATA code or city for arrival airport
            arrival_country (str): Country for arrival airport
            seat_class (str): Seat class string
            start_date (str): Departure date in MM/DD/YYYY format
            end_date (str): Return date in MM/DD/YYYY format
            export (bool): Whether to export the result dictionary or not. Defaults to false
            export_type (str | None): Type of export, required if export is True
            export_path (str | None): Path to export, required if export is True

        Returns:
            bool: True if flight is domestic US
        """
        # Validate airport codes
        for code in [departure_code, arrival_code]:
            validate_airport_code(code, self.airport_codes_df)

        # Determine if domestic US flight
        is_domestic_us = is_domestic_us_flight(
            departure_country,
            arrival_country,
            self.airport_codes_df,
        )

        # Validate seat class
        validate_seat_class(seat_class, is_domestic_us)

        # Validate dates
        validate_dates(start_date, end_date)

        # Validate export params
        validate_export_params(export, export_type, export_path)

        return is_domestic_us

    def _fill_search_form(
        self,
        departure_code: str,
        arrival_code: str,
        start_date: str,
        end_date: str,
        seat_class: str,
        is_domestic_us: bool,
    ):
        """Fill out the Google Flights search form.

        Args:
            departure_code (str): IATA code for departure airport
            arrival_code (str): IATA code for arrival airport
            start_date (str): Departure date in MM/DD/YYYY format
            end_date (str): Return date in MM/DD/YYYY format
            seat_class (str): Seat class string
            is_domestic_us (bool): Whether flight is domestic US
        """
        # Enter airports
        enter_airports(self.wait, departure_code, arrival_code)

        # Enter dates
        enter_dates(self.wait, start_date, end_date)

        # Select seat class
        select_seat_class(self.wait, seat_class, is_domestic_us)

        # Click search button
        press_search_button(self.wait)

    def _select_best_flights(self, result: dict):
        """Select the best departure and return flights and extract details.

        Args:
            result (dict): Dictionary to populate with flight details

        Returns:
            tuple: (updated result dictionary, success status message)
        """
        # Find and select best departure flight
        best_departure = find_and_select_best_flight(
            self.wait,
            self.driver,
            self.wait_time,
        )
        if best_departure is None:
            return result, "No departure flights found."

        # Extract flight details
        result["departure_flight"], result["price"] = extract_flight_details(best_departure)

        # Select flight
        best_departure.click()

        # Find and select best return flight
        best_return = find_and_select_best_flight(
            self.wait,
            self.driver,
            self.wait_time,
        )
        if best_return is None:
            return result, "No return flights found."

        # Extract flight details
        result["return_flight"], result["price"] = extract_flight_details(best_return)

        # Select flight
        best_return.click()

        return result, "Ran successfully."

    def _export_data(self, result: dict, export_type: str | None, export_path: str | None):
        """Export dict to file in desired format.

        Args:
            result (dict): Resulting dictionary after scraping
            export_type (str | None): Type of export ('json', 'csv')
            export_path (str | None): Path to export file to
        """
        if (export_type == "json") and (export_path):
            json_output = json.dumps(result, indent=2)
            with open(export_path, "w") as f:
                f.write(json_output)

        if (export_type == "csv") and (export_path):
            df = pd.json_normalize(result, sep="_")
            df.to_csv(export_path, index=False)

    def scrape_flight(
        self,
        departure_code: str,
        departure_country: str,
        arrival_code: str,
        arrival_country: str,
        start_date: str,
        end_date: str,
        seat_class: str,
        export: bool = False,
        export_type: str | None = None,
        export_path: str | None = None,
    ):
        """Scrape Google Flights for specified route and parameters.

        Args:
            departure_code (str): IATA code or city for departure airport
            departure_country (str): Country for departure airport
            arrival_code (str): IATA code or city for arrival airport
            arrival_country (str): Country for arrival airport
            start_date (str): Departure date in MM/DD/YYYY format
            end_date (str): Return date in MM/DD/YYYY format
            seat_class (str): Seat class (e.g., "Economy (include Basic)", "Business", etc.)
            export (bool): Whether to export the result dictionary or not. Defaults to false
            export_type (str | None): Type of export, required if export is True
            export_path (str | None): Path to export, required if export is True

        Returns:
            dict: Complete flight information as dictionary
        """
        # Initialize result structure
        result = self._create_result_structure(
            departure_code,
            departure_country,
            arrival_code,
            arrival_country,
            start_date,
            end_date,
            seat_class,
        )

        try:
            # Validate inputs
            is_domestic_us = self._validate_inputs(
                departure_code,
                departure_country,
                arrival_code,
                arrival_country,
                seat_class,
                start_date,
                end_date,
                export,
                export_type,
                export_path,
            )

            # Navigate to Google Flights
            self.driver.get("https://www.google.com/travel/flights")

            # Fill search form
            self._fill_search_form(
                departure_code,
                arrival_code,
                start_date,
                end_date,
                seat_class,
                is_domestic_us,
            )

            # Select best flights and extract details
            result, status = self._select_best_flights(result)

            # Extract price relativity
            if status == "Ran successfully.":
                (result["price_classification"], result["price_relativity"]) = (
                    extract_price_relativity(self.wait, self.driver, self.wait_time)
                )

        except Exception as e:
            print(f"Error scraping flight: {e}")
            status = f"Error: {str(e)}"
        finally:
            # Close the driver
            self.driver.quit()
            time.sleep(1)

        # Update status
        result["status"] = status

        # Export
        if export:
            self._export_data(result, export_type, export_path)

        return result

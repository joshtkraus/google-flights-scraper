"""Main scraper orchestration class."""

import json
import time
from pathlib import Path
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait

from .config_browser import setup_chrome_driver, DEFAULT_WAIT_TIME
from .validators import validate_airport_code, is_domestic_us_flight, validate_seat_class
from .interactions import (
    enter_airports, enter_dates, select_seat_class, press_search_button,
    find_and_select_best_flight
)
from .parsers import extract_flight_details, extract_price_relativity, create_empty_flight_info


class GoogleFlightsScraper:
    """Web scraper for Google Flights."""

    def __init__(self):
        """Initialize the scraper with airport codes data."""
        package_dir = Path(__file__).parent.parent.parent
        csv_path = package_dir / 'data' / 'airport_codes.csv'
        self.airport_codes_df = pd.read_csv(csv_path)
        self.driver = setup_chrome_driver(headless=True)
        self.wait_time = DEFAULT_WAIT_TIME
        self.wait = WebDriverWait(self.driver, self.wait_time)

    def _create_result_structure(
            self,
            departure_code,
            arrival_code,
            start_date,
            end_date,
            seat_class,
        ):
        """Create the initial result structure for storing flight data.

        Args:
            departure_code: IATA code for departure airport
            arrival_code: IATA code for arrival airport
            start_date: Departure date in MM/DD/YYYY format
            end_date: Return date in MM/DD/YYYY format
            seat_class: Seat class string

        Returns:
            dict: Empty result structure
        """
        return {
            'inputs': {
                'departure_airport': departure_code,
                'arrival_airport': arrival_code,
                'departure_date': start_date,
                'return_date': end_date,
                'seat_class': seat_class,
            },
            'departure_flight': create_empty_flight_info(),
            'return_flight': create_empty_flight_info(),
            'price': 'NA',
            'price_classification': 'NA',
            'price_relativity': 'NA',
        }

    def _validate_inputs(self, departure_code, arrival_code, seat_class):
        """Validate all input parameters.

        Args:
            departure_code: IATA code for departure airport
            arrival_code: IATA code for arrival airport
            seat_class: Seat class string

        Returns:
            bool: True if flight is domestic US

        Raises:
            ValueError: If any validation fails
        """
        # Validate airport codes
        for code in [departure_code, arrival_code]:
            validate_airport_code(code, self.airport_codes_df)

        # Determine if domestic US flight
        is_domestic_us = is_domestic_us_flight(
            departure_code, arrival_code, self.airport_codes_df,
        )

        # Validate seat class
        validate_seat_class(seat_class, is_domestic_us)

        return is_domestic_us

    def _fill_search_form(
            self,
            departure_code,
            arrival_code,
            start_date,
            end_date,
            seat_class,
            is_domestic_us,
        ):
        """Fill out the Google Flights search form.

        Args:
            departure_code: IATA code for departure airport
            arrival_code: IATA code for arrival airport
            start_date: Departure date in MM/DD/YYYY format
            end_date: Return date in MM/DD/YYYY format
            seat_class: Seat class string
            is_domestic_us: Whether flight is domestic US
        """
        # Enter airports
        enter_airports(self.wait, departure_code, arrival_code)

        # Enter dates
        enter_dates(self.wait, start_date, end_date)

        # Select seat class
        select_seat_class(self.wait, seat_class, is_domestic_us)

        # Click search button
        press_search_button(self.wait)

    def _select_best_flights(self, result):
        """Select the best departure and return flights and extract details.

        Args:
            result: Dictionary to populate with flight details

        Returns:
            dict: Updated result dictionary with flight details
        """
        # Find and select best departure flight
        best_departure = find_and_select_best_flight(
            self.wait, self.driver, self.wait_time,
        )
        if best_departure is None:
            return result

        # Extract flight details
        result['departure_flight'], result['price'] = extract_flight_details(best_departure)

        # Select flight
        best_departure.click()

        # Find and select best return flight
        best_return = find_and_select_best_flight(
            self.wait, self.driver, self.wait_time,
        )
        if best_return is None:
            return result

        # Extract flight details
        result['return_flight'], result['price'] = extract_flight_details(best_return)

        # Select flight
        best_return.click()

        return result

    def scrape_flight(self, departure_code, arrival_code, start_date, end_date, seat_class):
        """Scrape Google Flights for specified route and parameters.

        Args:
            departure_code: IATA code for departure airport
            arrival_code: IATA code for arrival airport
            start_date: Departure date in MM/DD/YYYY format
            end_date: Return date in MM/DD/YYYY format
            seat_class: Seat class (e.g., "Economy (include Basic)", "Business", etc.)

        Returns:
            dict: Complete flight information as dictionary
        """
        # Initialize result structure
        result = self._create_result_structure(
            departure_code, arrival_code, start_date, end_date, seat_class,
        )

        try:
            # Validate inputs
            is_domestic_us = self._validate_inputs(
                departure_code, arrival_code, seat_class,
            )

            # Navigate to Google Flights
            self.driver.get('https://www.google.com/travel/flights')

            # Fill search form
            self._fill_search_form(
                departure_code, arrival_code, start_date, end_date,
                seat_class, is_domestic_us,
            )

            # Select best flights and extract details
            result = self._select_best_flights(result)

            # Extract price relativity
            result['price_classification'], result['price_relativity'] = \
                extract_price_relativity(self.wait, self.driver, self.wait_time)

        except Exception as e:
            print(f"Error scraping flight: {e}")
        finally:
            # Close the driver
            self.driver.quit()
            time.sleep(1)

        return result

    def scrape_to_json(
            self,
            departure_code,
            arrival_code,
            start_date,
            end_date,
            seat_class,
            output_file=None,
        ):
        """Scrape flight and return/save as JSON.

        Args:
            departure_code: IATA code for departure airport
            arrival_code: IATA code for arrival airport
            start_date: Departure date in MM/DD/YYYY format
            end_date: Return date in MM/DD/YYYY format
            seat_class: Seat class
            output_file: Optional file path to save JSON output

        Returns:
            str: JSON formatted string
        """
        result = self.scrape_flight(
            departure_code, arrival_code, start_date, end_date, seat_class,
        )
        json_output = json.dumps(result, indent=2)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_output)

        return json_output

"""Main scraper orchestration class."""

import asyncio
import json
import sys
from pathlib import Path

import pandas as pd
from playwright.async_api import Page

from .config_browser import DEFAULT_TIMEOUT, setup_browser
from .interactions import (
    enter_airports,
    enter_dates,
    find_and_select_best_flight,
    press_search_button,
    select_seat_class,
)
from .parsers import (
    create_empty_flight_info,
    extract_final_price,
    extract_flight_details,
    extract_price_relativity,
)
from .validators import (
    is_domestic_us_flight,
    validate_airport_code,
    validate_dates,
    validate_export_params,
    validate_seat_class,
)


class GoogleFlightsScraper:
    """Web scraper for Google Flights using Playwright."""

    def __init__(self):
        """Initialize the scraper with airport codes data."""
        package_dir = Path(__file__).parent.parent.parent
        csv_path = package_dir / "data" / "airport_codes.csv"
        self.airport_codes_df = pd.read_csv(csv_path)

        self.wait_time = DEFAULT_TIMEOUT

        # Playwright instances
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    @property
    def _page(self) -> Page:
        """Get page instance, raising error if not initialized.

        Raises:
            RuntimeError: If browser not initialized.
        """
        if self.page is None:
            raise RuntimeError("Browser not initialized. Call scrape_flight first.")
        return self.page

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
            departure_code (str): IATA code or city for departure airport
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
            "price_difference": None,
            "price_relativity": None,
            "status": None,
            "url": None,
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
            export_path (str | None): Path to export file

        Returns:
            bool: True if flight is domestic US
        """
        for code in [departure_code, arrival_code]:
            validate_airport_code(code, self.airport_codes_df)

        is_domestic_us = is_domestic_us_flight(
            departure_country,
            arrival_country,
            self.airport_codes_df,
        )

        validate_seat_class(seat_class, is_domestic_us)
        validate_dates(start_date, end_date)
        validate_export_params(export_path)

        return is_domestic_us

    async def _fill_search_form(
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
        await enter_airports(self._page, departure_code, arrival_code)
        await enter_dates(self._page, start_date, end_date)
        await select_seat_class(self._page, seat_class, is_domestic_us)
        await press_search_button(self._page)

    async def _find_flight_with_retry(
        self,
        result: dict,
        key: str,
        max_retries: int = 3,
        sleep_s: float = 0.5,
    ):
        """Find best flight element with retry and extract details.

        Args:
            result (dict): Dictionary to populate with flight details
            key (str): Dict key to add data to (departure_flight or return_flight)
            max_retries (int): Number of times to retry selecting element
            sleep_s (float): How long to sleep (seconds) in between each try

        Returns:
            str | None: Error message if failed, None if successful
        """
        for attempt in range(max_retries):
            try:
                flight = await find_and_select_best_flight(self._page, timeout=self.wait_time)

                if flight is None:
                    return f"No {key.replace('_', ' ')} found."

                result[key] = await extract_flight_details(flight)

                await flight.click()
                return None

            except Exception as e:
                if attempt == max_retries - 1:
                    return f"Error finding {key}: {str(e)}"
                await asyncio.sleep(sleep_s)

        return f"Failed to find {key} after {max_retries} retries."

    async def _select_best_flights(self, result: dict):
        """Select the best departure and return flights and extract details.

        Args:
            result (dict): Dictionary to populate with flight details

        Returns:
            tuple: (updated result dictionary, success status message)
        """
        err = await self._find_flight_with_retry(result, key="departure_flight")
        if err:
            return result, err

        err = await self._find_flight_with_retry(result, key="return_flight")
        if err:
            return result, err

        await asyncio.sleep(1)

        result["price"] = await extract_final_price(self._page, timeout=self.wait_time * 2)

        if result["price"] is None:
            return result, "Error: Price not found"

        result["url"] = self._page.url

        return result, "Ran successfully."

    def _calc_price_rel(self, price: int, price_difference: int | None):
        """Calculate price relativity (% discount).

        Args:
            price (int): Final flight price
            price_difference (int | None): How much cheaper flight is than usual

        Returns:
            float | None: Percentage discount or None
        """
        if price_difference is not None and price is not None:
            return round(float(price_difference / (price + price_difference)), 4)
        return None

    def _export_data(self, result: dict, export_path: str):
        """Export dict to file based on extension.

        Args:
            result (dict): Resulting dictionary after scraping
            export_path (str): Path to export file to
        """
        if export_path.endswith(".json"):
            with open(export_path, "w") as f:
                f.write(json.dumps(result, indent=2))
        elif export_path.endswith(".csv"):
            df = pd.json_normalize(result, sep="_")
            df.to_csv(export_path, index=False)

    async def scrape_flight(
        self,
        departure_code: str,
        departure_country: str,
        arrival_code: str,
        arrival_country: str,
        start_date: str,
        end_date: str,
        seat_class: str,
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
            export_path (str | None): Path to export file (.json or .csv)

        Returns:
            dict: Complete flight information as dictionary
        """
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
            is_domestic_us = self._validate_inputs(
                departure_code,
                departure_country,
                arrival_code,
                arrival_country,
                seat_class,
                start_date,
                end_date,
                export_path,
            )

            self.playwright, self.browser, self.context, self.page = await setup_browser()

            await self.page.goto("https://www.google.com/travel/flights")

            await self._fill_search_form(
                departure_code,
                arrival_code,
                start_date,
                end_date,
                seat_class,
                is_domestic_us,
            )

            result, status = await self._select_best_flights(result)

            if status == "Ran successfully.":
                (
                    result["price_classification"],
                    result["price_difference"],
                ) = await extract_price_relativity(self.page, timeout=2000)

            result["price_relativity"] = self._calc_price_rel(
                result["price"], result["price_difference"]
            )

        except Exception as e:
            print(f"Error scraping flight: {e}", file=sys.stderr)
            status = f"Error: {str(e)}"
        finally:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

        result["status"] = status

        if export_path:
            self._export_data(result, export_path)

        return result

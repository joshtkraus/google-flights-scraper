"""Validation functions for Google Flights scraper."""

from datetime import datetime

from pandas import DataFrame

from .config_browser import VALID_CLASSES_DOMESTIC_US, VALID_CLASSES_INTERNATIONAL


def validate_dates(start_date: str, end_date: str):
    """Validate that end_date is after start_date.

    Args:
        start_date (str): Departure date in MM/DD/YYYY format
        end_date (str): Return date in MM/DD/YYYY format

    Raises:
        ValueError: If dates are invalid or end_date is before start_date
    """
    try:
        start = datetime.strptime(start_date, "%m/%d/%Y")
        end = datetime.strptime(end_date, "%m/%d/%Y")
    except ValueError as e:
        raise ValueError("Invalid date format. Expected MM/DD/YYYY:") from e

    if end <= start:
        raise ValueError(f"Return date ({end_date}) must be after departure date ({start_date})")


def validate_export_params(export: bool = False, export_type: str = None, export_path: str = None):
    """Validate that required params are passed for export.

    Args:
        export (bool): Whether to export the result dictionary or not. Defaults to false
        export_type (str): Type of export, required if export is True
        export_path (str): Path to export, required if export is True

    Raises:
        ValueError: If required params are not passed
    """
    if export:
        missing = []
        if export_type is None:
            missing.append("export_type")
        if export_path is None:
            missing.append("export_path")
        if missing:
            raise ValueError(f"export is True, but {missing} not defined")

        if export_type not in ["json", "csv"]:
            raise ValueError(f"Unsupported export type {export_type}")


def validate_airport_code(airport_code: str, airport_codes_df: DataFrame):
    """Validate if airport code or city exists in dataset.

    Args:
        airport_code (str): IATA code or City to validate
        airport_codes_df (DataFrame): DataFrame containing airport codes and cities

    Raises:
        ValueError: If airport code or city is not found in dataset
    """
    # IATA Code
    if not airport_codes_df["IATA"].str.upper().isin([airport_code.upper()]).any():
        # Cities
        if not airport_codes_df["City"].str.upper().isin([airport_code.upper()]).any():
            raise ValueError(f"Invalid airport input: {airport_code}")


def is_domestic_us_flight(
    departure_country: str, arrival_country: str, airport_codes_df: DataFrame
):
    """Determine if flight is domestic US based on airport codes and cities.

    Args:
        departure_country (str): Country for departure airport
        arrival_country (str): Country for arrival airport
        airport_codes_df (DataFrame): DataFrame containing airport codes

    Returns:
        bool: True if both airports are in United States of America
    """
    usa = "United States of America"
    if (departure_country.upper() == usa.upper()) and (arrival_country.upper() == usa.upper()):
        return True
    return False


def validate_seat_class(seat_class: str, is_domestic_us: bool):
    """Validate seat class selection based on flight type.

    Args:
        seat_class (str): Seat class string
        is_domestic_us (bool): Whether flight is domestic US

    Raises:
        ValueError: If seat class is invalid for the flight type
    """
    # Validate based on flight type
    if is_domestic_us:
        if seat_class.lower() not in VALID_CLASSES_DOMESTIC_US:
            raise ValueError(f"Invalid seat class for domestic US flight: {seat_class}")
    else:
        if seat_class.lower() not in VALID_CLASSES_INTERNATIONAL:
            raise ValueError(f"Invalid seat class for international flight: {seat_class}")

"""Validation functions for Google Flights scraper."""

from pandas import DataFrame

from .config_browser import VALID_CLASSES_DOMESTIC_US, VALID_CLASSES_INTERNATIONAL


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
    """Validate if airport code exists in dataset.

    Args:
        airport_code (str): IATA code to validate
        airport_codes_df (DataFrame): DataFrame containing airport codes

    Raises:
        ValueError: If airport code is not found in dataset
    """
    if not airport_codes_df["IATA"].isin([airport_code]).any():
        raise ValueError(f"Invalid airport code: {airport_code}")


def is_domestic_us_flight(departure_code: str, arrival_code: str, airport_codes_df: DataFrame):
    """Determine if flight is domestic US based on airport codes.

    Args:
        departure_code (str): IATA code for departure airport
        arrival_code (str): IATA code for arrival airport
        airport_codes_df (DataFrame): DataFrame containing airport codes

    Returns:
        bool: True if both airports are in United States of America
    """
    # Get countries for both airports
    departure_country = airport_codes_df[airport_codes_df["IATA"] == departure_code][
        "Country"
    ].values
    arrival_country = airport_codes_df[airport_codes_df["IATA"] == arrival_code]["Country"].values

    # Check if both are in USA
    return (
        departure_country[0] == "United States of America"
        and arrival_country[0] == "United States of America"
    )


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
        if seat_class not in VALID_CLASSES_DOMESTIC_US:
            raise ValueError(f"Invalid seat class for domestic US flight: {seat_class}")
    else:
        if seat_class not in VALID_CLASSES_INTERNATIONAL:
            raise ValueError(f"Invalid seat class for international flight: {seat_class}")

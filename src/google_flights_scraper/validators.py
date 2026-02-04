"""Validation functions for Google Flights scraper."""

import pandas as pd
from .config_browser import VALID_CLASSES_DOMESTIC_US, VALID_CLASSES_INTERNATIONAL


def validate_airport_code(airport_code, airport_codes_df):
    """Validate if airport code exists in dataset.

    Args:
        airport_code: IATA code to validate
        airport_codes_df: DataFrame containing airport codes

    Raises:
        ValueError: If airport code is not found in dataset
    """
    if not airport_codes_df['IATA'].isin([airport_code]).any():
        raise ValueError(f"Invalid airport code: {airport_code}")


def is_domestic_us_flight(departure_code, arrival_code, airport_codes_df):
    """Determine if flight is domestic US based on airport codes.

    Args:
        departure_code: IATA code for departure airport
        arrival_code: IATA code for arrival airport
        airport_codes_df: DataFrame containing airport codes

    Returns:
        bool: True if both airports are in United States of America
    """
    # Get countries for both airports
    departure_country = airport_codes_df[
        airport_codes_df['IATA'] == departure_code
    ]['Country'].values
    arrival_country = airport_codes_df[
        airport_codes_df['IATA'] == arrival_code
    ]['Country'].values

    # Check if both are in USA
    return (departure_country[0] == 'United States of America' and 
            arrival_country[0] == 'United States of America')


def validate_seat_class(seat_class, is_domestic_us):
    """Validate seat class selection based on flight type.

    Args:
        seat_class: Seat class string
        is_domestic_us: Whether flight is domestic US

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

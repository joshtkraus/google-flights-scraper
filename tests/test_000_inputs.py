"""Unit tests for validator functions."""

import pytest
import pandas as pd
from pathlib import Path
from google_flights_scraper.validators import (
    validate_dates,
    validate_export_params,
    validate_airport_code,
    is_domestic_us_flight,
    validate_seat_class,
)


@pytest.fixture
def airport_df():
    """Load actual airport codes DataFrame for testing."""
    # From tests/ directory, go up one level to project root, then into data/
    test_dir = Path(__file__).parent
    csv_path = test_dir.parent / "data" / "airport_codes.csv"
    return pd.read_csv(csv_path)


# Date validation tests
def test_valid_dates():
    """Test that valid dates pass validation."""
    validate_dates("03/15/2026", "03/22/2026")  # Should not raise


def test_end_date_before_start_date():
    """Test that end date before start date raises ValueError."""
    with pytest.raises(ValueError):
        validate_dates("03/22/2026", "03/15/2026")


def test_same_dates():
    """Test that same start and end dates raise ValueError."""
    with pytest.raises(ValueError):
        validate_dates("03/15/2026", "03/15/2026")


def test_invalid_date_format_wrong_separator():
    """Test that wrong date separator raises ValueError."""
    with pytest.raises(ValueError):
        validate_dates("03-15-2026", "03-22-2026")


def test_invalid_date_format_wrong_order():
    """Test that wrong date order (YYYY/MM/DD) raises ValueError."""
    with pytest.raises(ValueError):
        validate_dates("2026/03/15", "2026/03/22")


def test_invalid_month():
    """Test that invalid month raises ValueError."""
    with pytest.raises(ValueError):
        validate_dates("13/15/2026", "13/22/2026")


def test_invalid_day():
    """Test that invalid day raises ValueError."""
    with pytest.raises(ValueError):
        validate_dates("03/32/2026", "03/40/2026")


def test_non_date_strings():
    """Test that non-date strings raise ValueError."""
    with pytest.raises(ValueError):
        validate_dates("not a date", "also not a date")


def test_empty_date_strings():
    """Test that empty strings raise ValueError."""
    with pytest.raises(ValueError):
        validate_dates("", "")


# Export parameter validation tests
def test_export_no_path():
    """Test that no export_path doesn't raise."""
    validate_export_params()  # Should not raise


def test_export_none_path():
    """Test that None export_path doesn't raise."""
    validate_export_params(export_path=None)  # Should not raise


def test_export_valid_json_path():
    """Test that valid json path passes."""
    validate_export_params(export_path="/tmp/output.json")  # Should not raise


def test_export_valid_csv_path():
    """Test that valid csv path passes."""
    validate_export_params(export_path="/tmp/output.csv")  # Should not raise


def test_export_invalid_extension():
    """Test that invalid file extension raises ValueError."""
    with pytest.raises(ValueError):
        validate_export_params(export_path="/tmp/output.xml")


def test_export_no_extension():
    """Test that path without extension raises ValueError."""
    with pytest.raises(ValueError):
        validate_export_params(export_path="/tmp/output")


def test_export_txt_extension():
    """Test that .txt extension raises ValueError."""
    with pytest.raises(ValueError):
        validate_export_params(export_path="/tmp/output.txt")


def test_export_uppercase_extension():
    """Test that uppercase extension (.CSV, .JSON) raises ValueError."""
    with pytest.raises(ValueError):
        validate_export_params(export_path="/tmp/output.CSV")


# Airport code validation tests
def test_valid_iata_code(airport_df):
    """Test that valid IATA codes pass validation."""
    validate_airport_code("JFK", airport_df)  # Should not raise
    validate_airport_code("LAX", airport_df)  # Should not raise


def test_valid_iata_code_lowercase(airport_df):
    """Test that lowercase IATA codes pass validation."""
    validate_airport_code("jfk", airport_df)  # Should not raise


def test_valid_city_name(airport_df):
    """Test that valid city names pass validation."""
    validate_airport_code("New York", airport_df)  # Should not raise
    validate_airport_code("London", airport_df)  # Should not raise


def test_valid_city_name_lowercase(airport_df):
    """Test that lowercase city names pass validation."""
    validate_airport_code("new york", airport_df)  # Should not raise


def test_invalid_iata_code(airport_df):
    """Test that invalid IATA code raises ValueError."""
    with pytest.raises(ValueError):
        validate_airport_code("XYZ", airport_df)


def test_invalid_city_name(airport_df):
    """Test that invalid city name raises ValueError."""
    with pytest.raises(ValueError):
        validate_airport_code("Atlantis", airport_df)


def test_empty_airport_string(airport_df):
    """Test that empty string raises ValueError."""
    with pytest.raises(ValueError):
        validate_airport_code("", airport_df)


# Domestic US flight detection tests
def test_domestic_us_flight(airport_df):
    """Test that US to US returns True."""
    assert is_domestic_us_flight(
        "United States of America",
        "United States of America",
        airport_df
    ) is True


def test_international_flight_us_to_uk(airport_df):
    """Test that US to UK returns False."""
    assert is_domestic_us_flight(
        "United States of America",
        "United Kingdom",
        airport_df
    ) is False


def test_international_flight_uk_to_us(airport_df):
    """Test that UK to US returns False."""
    assert is_domestic_us_flight(
        "United Kingdom",
        "United States of America",
        airport_df
    ) is False


def test_international_flight_uk_to_france(airport_df):
    """Test that UK to France returns False."""
    assert is_domestic_us_flight(
        "United Kingdom",
        "France",
        airport_df
    ) is False


def test_case_insensitive_country_match(airport_df):
    """Test that country matching is case insensitive."""
    assert is_domestic_us_flight(
        "united states of america",
        "UNITED STATES OF AMERICA",
        airport_df
    ) is True


# Seat class validation tests
def test_valid_domestic_economy_include_basic():
    """Test valid domestic seat class: Economy (include Basic)."""
    validate_seat_class("economy (include basic)", is_domestic_us=True)  # Should not raise


def test_valid_domestic_economy_exclude_basic():
    """Test valid domestic seat class: Economy (exclude Basic)."""
    validate_seat_class("economy (exclude basic)", is_domestic_us=True)  # Should not raise


def test_valid_domestic_premium_economy():
    """Test valid domestic seat class: Premium economy."""
    validate_seat_class("premium economy", is_domestic_us=True)  # Should not raise


def test_valid_domestic_business():
    """Test valid domestic seat class: Business."""
    validate_seat_class("business", is_domestic_us=True)  # Should not raise


def test_valid_domestic_first():
    """Test valid domestic seat class: First."""
    validate_seat_class("first", is_domestic_us=True)  # Should not raise


def test_valid_international_economy():
    """Test valid international seat class: Economy."""
    validate_seat_class("economy", is_domestic_us=False)  # Should not raise


def test_valid_international_premium_economy():
    """Test valid international seat class: Premium economy."""
    validate_seat_class("premium economy", is_domestic_us=False)  # Should not raise


def test_valid_international_business():
    """Test valid international seat class: Business."""
    validate_seat_class("business", is_domestic_us=False)  # Should not raise


def test_valid_international_first():
    """Test valid international seat class: First."""
    validate_seat_class("first", is_domestic_us=False)  # Should not raise


def test_invalid_domestic_plain_economy():
    """Test that plain 'Economy' is invalid for domestic US flights."""
    with pytest.raises(ValueError):
        validate_seat_class("economy", is_domestic_us=True)


def test_invalid_international_economy_with_basic():
    """Test that 'Economy (include Basic)' is invalid for international flights."""
    with pytest.raises(ValueError):
        validate_seat_class("economy (include basic)", is_domestic_us=False)


def test_invalid_seat_class_typo():
    """Test that misspelled seat class raises ValueError."""
    with pytest.raises(ValueError):
        validate_seat_class("bizness", is_domestic_us=True)


def test_invalid_seat_class_empty():
    """Test that empty seat class raises ValueError."""
    with pytest.raises(ValueError):
        validate_seat_class("", is_domestic_us=True)


def test_invalid_seat_class_random_string():
    """Test that random string raises ValueError."""
    with pytest.raises(ValueError):
        validate_seat_class("super deluxe class", is_domestic_us=False)

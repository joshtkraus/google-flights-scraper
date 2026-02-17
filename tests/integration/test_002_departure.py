"""Tests for Departure flight info."""

import pytest

pytestmark = pytest.mark.integration

# List of results
RESULTS = [
    "domestic_economy_basic",
    "domestic_economy_non_basic",
    "domestic_premium_economy",
    "domestic_business",
    "domestic_first",
    "int_economy",
    "int_premium_economy",
    "int_business",
    "int_first",
]

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_return(scraper_fixture, request):
    """Test that scraper returns departure info."""
    result = request.getfixturevalue(scraper_fixture)
    assert "departure_flight" in result.keys()
    departure_results = result["departure_flight"]
    assert isinstance(departure_results, dict)
    assert len(departure_results.keys()) > 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_airline(scraper_fixture, request):
    """Test that scraper returns departure airline."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "airline" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["airline"], str)
        assert departure_results["airline"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_airport(scraper_fixture, request):
    """Test that scraper returns departure airport."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "departure_airport" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["departure_airport"], str)
        assert len(departure_results["departure_airport"]) == 3

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_date(scraper_fixture, request):
    """Test that scraper returns departure date."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "departure_date" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["departure_date"], str)
        assert departure_results["departure_date"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_time(scraper_fixture, request):
    """Test that scraper returns departure time."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "departure_time" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["departure_time"], str)
        assert departure_results["departure_time"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_stops(scraper_fixture, request):
    """Test that scraper returns num of departure stops."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "num_stops" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["num_stops"], int)
        assert departure_results["num_stops"] >= 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_connection_airports(scraper_fixture, request):
    """Test that scraper returns departure connection airports."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "connection_airports" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["connection_airports"], list)
        if departure_results["num_stops"] == 0:
            assert len(departure_results["connection_airports"]) == 0
        else:
            assert len(departure_results["connection_airports"]) > 0
            for airport in departure_results["connection_airports"]:
                assert isinstance(airport, str)
                assert len(airport) == 3

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_layover_durations(scraper_fixture, request):
    """Test that scraper returns departure layover durations."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "layover_durations" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["layover_durations"], list)
        if departure_results["num_stops"] == 0:
            assert len(departure_results["layover_durations"]) == 0
        else:
            assert len(departure_results["layover_durations"]) > 0
            assert isinstance(departure_results["layover_durations"][0], str)
            assert departure_results["layover_durations"][0] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_layover_durations_total_duration(scraper_fixture, request):
    """Test that scraper returns departure layover duration different than total duration."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "layover_durations" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["layover_durations"], list)
        if departure_results["num_stops"] == 1:
            assert departure_results["layover_durations"][0] != departure_results["duration_str"]

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_layover_total_duration(scraper_fixture, request):
    """Test that scraper returns total departure layover duration."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "layover_total_minutes" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["layover_total_minutes"], int)
        if departure_results["num_stops"] == 0:
            assert departure_results["layover_total_minutes"] == 0
        else:
            assert departure_results["layover_total_minutes"] > 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_arrival_airport(scraper_fixture, request):
    """Test that scraper returns arrival airport."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "arrival_airport" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["arrival_airport"], str)
        assert len(departure_results["arrival_airport"]) == 3

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_arrival_date(scraper_fixture, request):
    """Test that scraper returns arrival date."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "arrival_date" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["arrival_date"], str)
        assert departure_results["arrival_date"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_arrival_time(scraper_fixture, request):
    """Test that scraper returns arrival time."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "arrival_time" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["arrival_time"], str)
        assert departure_results["arrival_time"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_duration_int(scraper_fixture, request):
    """Test that scraper returns departure duration."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "duration_minutes" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["duration_minutes"], int)
        assert departure_results["duration_minutes"] > 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_duration_str(scraper_fixture, request):
    """Test that scraper returns departure duration."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "duration_str" in departure_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(departure_results["duration_str"], str)
        assert departure_results["duration_str"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_carry_on_bags(scraper_fixture, request):
    """Test that scraper returns departure carry on bags."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "carry_on_bags" in departure_results.keys()
    # Sometimes this info isn't available
    if type(departure_results["carry_on_bags"]) is int:
        assert departure_results["carry_on_bags"] >= 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_checked_bags(scraper_fixture, request):
    """Test that scraper returns departure checked bags."""
    result = request.getfixturevalue(scraper_fixture)
    departure_results = result["departure_flight"]
    assert "checked_bags" in departure_results.keys()
    # Sometimes this info isn't available
    if type(departure_results["checked_bags"]) is int:
        assert departure_results["checked_bags"] >= 0

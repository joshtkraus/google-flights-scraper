"""Tests for Return flight info."""

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
    assert "return_flight" in result.keys()
    return_results = result["return_flight"]
    assert isinstance(return_results, dict)
    assert len(return_results.keys()) > 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_airline(scraper_fixture, request):
    """Test that scraper returns departure airline."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "airline" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["airline"], str)
        assert return_results["airline"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_airport(scraper_fixture, request):
    """Test that scraper returns departure airport."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "departure_airport" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["departure_airport"], str)
        assert return_results["departure_airport"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_date(scraper_fixture, request):
    """Test that scraper returns departure date."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "departure_date" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["departure_date"], str)
        assert return_results["departure_date"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_time(scraper_fixture, request):
    """Test that scraper returns departure time."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "departure_time" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["departure_time"], str)
        assert return_results["departure_time"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_stops(scraper_fixture, request):
    """Test that scraper returns num of departure stops."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "num_stops" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["num_stops"], int)
        assert return_results["num_stops"] >= 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_connection_airports(scraper_fixture, request):
    """Test that scraper returns departure connection airports."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "connection_airports" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["connection_airports"], list)
        if return_results["num_stops"] == 0:
            assert len(return_results["connection_airports"]) == 0
        else:
            assert len(return_results["connection_airports"]) > 0
            assert isinstance(return_results["connection_airports"][0], str)
            assert return_results["connection_airports"][0] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_layover_durations(scraper_fixture, request):
    """Test that scraper returns departure layover durations."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "layover_durations" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["layover_durations"], list)
        if return_results["num_stops"] == 0:
            assert len(return_results["layover_durations"]) == 0
        else:
            assert len(return_results["layover_durations"]) > 0
            assert isinstance(return_results["layover_durations"][0], str)
            assert return_results["layover_durations"][0] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_arrival_airport(scraper_fixture, request):
    """Test that scraper returns arrival airport."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "arrival_airport" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["arrival_airport"], str)
        assert return_results["arrival_airport"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_arrival_date(scraper_fixture, request):
    """Test that scraper returns arrival date."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "arrival_date" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["arrival_date"], str)
        assert return_results["arrival_date"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_arrival_time(scraper_fixture, request):
    """Test that scraper returns arrival time."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "arrival_time" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["arrival_time"], str)
        assert return_results["arrival_time"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_duration_int(scraper_fixture, request):
    """Test that scraper returns departure duration."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "duration_minutes" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["duration_minutes"], int)
        assert return_results["duration_minutes"] > 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_duration_str(scraper_fixture, request):
    """Test that scraper returns departure duration."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "duration_str" in return_results.keys()
    if result['status'] == "Ran successfully.":
        assert isinstance(return_results["duration_str"], str)
        assert return_results["duration_str"] != ""

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_carry_on_bags(scraper_fixture, request):
    """Test that scraper returns departure carry on bags."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "carry_on_bags" in return_results.keys()
    # Sometimes this info isn't available
    if type(return_results["carry_on_bags"]) is int:
        assert return_results["carry_on_bags"] >= 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_departure_checked_bags(scraper_fixture, request):
    """Test that scraper returns departure checked bags."""
    result = request.getfixturevalue(scraper_fixture)
    return_results = result["return_flight"]
    assert "checked_bags" in return_results.keys()
    # Sometimes this info isn't available
    if type(return_results["checked_bags"]) is int:
        assert return_results["checked_bags"] >= 0

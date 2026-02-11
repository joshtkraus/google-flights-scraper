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
def test_results_return(scraper_fixture, request):
    """Test that scraper returns non-empty dict."""
    result = request.getfixturevalue(scraper_fixture)
    assert isinstance(result, dict)
    assert len(result.keys()) > 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_results_url(scraper_fixture, request):
    """Test that scraper returns final url."""
    result = request.getfixturevalue(scraper_fixture)
    if result['status'] == "Ran successfully.":
        assert isinstance(result["url"], str)
        assert result["url"] != ""

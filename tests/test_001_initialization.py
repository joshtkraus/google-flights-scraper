"""Tests for Departure flight info."""

import pytest

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

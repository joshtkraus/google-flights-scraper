"""Tests for flight price info."""

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
def test_price(scraper_fixture, request):
    """Test that scraper returns price info."""
    result = request.getfixturevalue(scraper_fixture)
    assert "price" in result.keys()
    assert isinstance(result['price'], int)
    assert result['price'] > 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_price_classification(scraper_fixture, request):
    """Test that scraper returns price classification info."""
    result = request.getfixturevalue(scraper_fixture)
    assert "price_classification" in result.keys()
    # Sometimes this info doesn't exist
    if result["price_classification"] is not None:
        assert isinstance(result['price_classification'], str)
        assert result['price_classification'] in ["typical", "low", "high"]

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_price_difference(scraper_fixture, request):
    """Test that scraper returns price classification info."""
    result = request.getfixturevalue(scraper_fixture)
    assert "price_difference" in result.keys()
    # Sometimes this info doesn't exist
    if result["price_difference"] is not None:
        assert isinstance(result['price_difference'], int)
        assert result['price_difference'] >= 0

@pytest.mark.parametrize("scraper_fixture", RESULTS)
def test_price_relativity(scraper_fixture, request):
    """Test that scraper returns price relativity info."""
    result = request.getfixturevalue(scraper_fixture)
    assert "price_relativity" in result.keys()
    # Sometimes this info doesn't exist
    if result["price_relativity"] is not None:
        assert isinstance(result['price_relativity'], float)
        assert result['price_relativity'] >= 0

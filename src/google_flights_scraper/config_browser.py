"""Configuration constants and browser setup for Google Flights scraper."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Valid seat class options
VALID_CLASSES_DOMESTIC_US = [
    "economy (include basic)",
    "economy (exclude basic)",
    "premium economy",
    "business",
    "first",
]

VALID_CLASSES_INTERNATIONAL = [
    "economy",
    "premium economy",
    "business",
    "first",
]

# Seat class to option index mapping
SEAT_CLASS_OPTION_MAPPING = {
    True: {  # Domestic US
        "economy (include basic)": 3,
        "economy (exclude basic)": 4,
        "premium economy": 5,
        "business": 6,
        "first": 7,
    },
    False: {  # International
        "economy": 3,
        "premium economy": 4,
        "business": 5,
        "first": 6,
    },
}

# Default wait times
DEFAULT_WAIT_TIME = 10


def setup_chrome_driver(headless: bool = True):
    """Setup Chrome driver with appropriate options.

    Args:
        headless (bool): Whether to run Chrome in headless mode

    Returns:
        webdriver.Chrome: Configured Chrome driver instance
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "--user-agent="
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36",
    )
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-software-rasterizer")

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    return driver

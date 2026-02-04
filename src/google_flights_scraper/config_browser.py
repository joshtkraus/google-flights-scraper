"""Configuration constants and browser setup for Google Flights scraper."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Valid seat class options
VALID_CLASSES_DOMESTIC_US = [
    "Economy (include Basic)",
    "Economy (exclude Basic)",
    "Premium economy",
    "Business",
    "First",
]

VALID_CLASSES_INTERNATIONAL = [
    "Economy",
    "Premium economy",
    "Business",
    "First",
]

# Seat class to option index mapping
SEAT_CLASS_OPTION_MAPPING = {
    True: {  # Domestic US
        "Economy (include Basic)": 3,
        "Economy (exclude Basic)": 4,
        "Premium economy": 5,
        "Business": 6,
        "First": 7,
    },
    False: {  # International
        "Economy": 3,
        "Premium economy": 4,
        "Business": 5,
        "First": 6,
    },
}

# Default wait times
DEFAULT_WAIT_TIME = 10


def setup_chrome_driver(headless=True):
    """Setup Chrome driver with appropriate options.

    Args:
        headless: Whether to run Chrome in headless mode

    Returns:
        webdriver.Chrome: Configured Chrome driver instance
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-software-rasterizer")

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    return driver

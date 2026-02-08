"""Data extraction and parsing functions for Google Flights scraper."""

import re
import sys
import time

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from .interactions import wait_until_stable


def create_empty_flight_info():
    """Create an empty flight info dictionary structure.

    Returns:
        dict: Empty flight info structure with all fields set to None or empty lists
    """
    return {
        "airline": None,
        "departure_airport": None,
        "departure_date": None,
        "departure_time": None,
        "num_stops": None,
        "connection_airports": [],
        "layover_durations": [],
        "arrival_airport": None,
        "arrival_date": None,
        "arrival_time": None,
        "duration_minutes": None,
        "duration_str": None,
        "carry_on_bags": None,
        "checked_bags": None,
    }


def extract_airline(flight_description: str):
    """Extract airline from flight description.

    Args:
        flight_description (str): Flight description text

    Returns:
        str: Airline name or None
    """
    if m := re.search(r"flight with ([^.]+)", flight_description):
        return m.group(1).strip()
    return None


def extract_departure_info(flight_description: str):
    """Extract departure airport, time, and date from flight description.

    Args:
        flight_description (str): Flight description text

    Returns:
        tuple: (airport, time, date) or (None, None, None)
    """
    dep_pattern = (
        r"Leaves (.*?) at (\d{1,2}:\d{2}\s?[AP]M) "
        r"on ([A-Za-z]+, [A-Za-z]+ \d{1,2})"
    )
    if m := re.search(dep_pattern, flight_description):
        return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    return None, None, None


def extract_arrival_info(flight_description: str):
    """Extract arrival airport, time, and date from flight description.

    Args:
        flight_description (str): Flight description text

    Returns:
        tuple: (airport, time, date) or (None, None, None)
    """
    arr_pattern = (
        r"arrives at (.*?) at (\d{1,2}:\d{2}\s?[AP]M) "
        r"on ([A-Za-z]+, [A-Za-z]+ \d{1,2})"
    )
    if m := re.search(arr_pattern, flight_description):
        return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    return None, None, None


def extract_num_stops(flight_description: str):
    """Extract number of stops from flight description.

    Args:
        flight_description (str): Flight description text

    Returns:
        int: Number of stops or None
    """
    if "Nonstop" in flight_description:
        return 0
    elif m := re.search(r"(\d+) stop", flight_description):
        return int(m.group(1))
    return None


def extract_layover_info(flight_description: str):
    """Extract connection airports and layover durations from flight description.

    Args:
        flight_description (str): Flight description text

    Returns:
        tuple: (connection_airports, layover_durations) as lists
    """
    # Pattern for "layover at [airport name]" - handles hours only, minutes only, or both
    pattern_at = (
        r"Layover \(\d+ of \d+\) is a (\d+\s+(?:hr|min)(?:\s+\d+\s+min)?)"
        r"(?: overnight)? layover at ([^.]+?)(?:\sin\s[^.]+)?\.(?:\s|$)"
    )

    # Pattern for "layover in [city]" - handles hours only, minutes only, or both
    pattern_in = (
        r"Layover \(\d+ of \d+\) is a (\d+\s+(?:hr|min)(?:\s+\d+\s+min)?)"
        r"(?: overnight)? layover in ([^.]+?)\.(?:\s+Transfer)?"
    )

    # Try pattern with "at" first
    matches_at = re.findall(pattern_at, flight_description)
    matches_in = re.findall(pattern_in, flight_description)

    # pattern_at returns tuples of (duration, airport) due to 2 capturing groups
    # pattern_in returns tuples of (duration, location)
    all_matches = matches_at + matches_in
    if all_matches:
        layover_durations = [m[0].strip() for m in all_matches]
        connection_airports = [m[1].strip() for m in all_matches]
        return connection_airports, layover_durations
    return [], []


def extract_duration(flight_description: str):
    """Extract flight duration from flight description.

    Args:
        flight_description (str): Flight description text

    Returns:
        tuple: (duration_minutes, duration_str) or (None, None)
    """
    # Pattern with both hours and minutes
    if m := re.search(r"Total duration (\d+) hr (\d+) min", flight_description):
        hours = int(m.group(1))
        minutes = int(m.group(2))
        duration_minutes = hours * 60 + minutes
        duration_str = f"{hours} hr {minutes} min"
        return duration_minutes, duration_str

    # Pattern with only hours (no minutes)
    if m := re.search(r"Total duration (\d+) hr", flight_description):
        hours = int(m.group(1))
        duration_minutes = hours * 60
        duration_str = f"{hours} hr"
        return duration_minutes, duration_str

    # Pattern with only minutes (no hours)
    if m := re.search(r"Total duration (\d+) min", flight_description):
        minutes = int(m.group(1))
        duration_minutes = minutes
        duration_str = f"{minutes} min"
        return duration_minutes, duration_str

    return None, None


def extract_baggage_info(flight_description: str):
    """Extract carry-on and checked bag information from flight description.

    Args:
        flight_description (str): Flight description text

    Returns:
        tuple: (carry_on_bags, checked_bags) as integers or None
    """
    carry_on_bags = None
    checked_bags = None

    if m := re.search(r"(\d+) carry-on bag", flight_description):
        carry_on_bags = int(m.group(1))

    if m := re.search(r"(\d+) checked bags", flight_description):
        checked_bags = int(m.group(1))

    return carry_on_bags, checked_bags


def extract_flight_details(flight_element: Locator):
    """Extract all flight details from a flight element.

    Args:
        flight_element (Locator): Playwright Locator containing flight info

    Returns:
        dict: flight_info dictionary
    """
    # Initialize flight info structure
    flight_info = create_empty_flight_info()

    # Get flight description immediately and store as string
    flight_desc_locator = flight_element.locator("div[aria-label^='From ']")

    try:
        flight_description = flight_desc_locator.get_attribute("aria-label")
    except Exception:
        return flight_info

    if flight_description is None:
        return flight_info

    # Clean the string
    flight_description = flight_description.replace("\u202f", " ").replace("\xa0", " ")

    # Extract all information using helper functions
    flight_info["airline"] = extract_airline(flight_description)

    (
        flight_info["departure_airport"],
        flight_info["departure_time"],
        flight_info["departure_date"],
    ) = extract_departure_info(flight_description)

    flight_info["arrival_airport"], flight_info["arrival_time"], flight_info["arrival_date"] = (
        extract_arrival_info(flight_description)
    )

    flight_info["num_stops"] = extract_num_stops(flight_description)

    flight_info["connection_airports"], flight_info["layover_durations"] = extract_layover_info(
        flight_description
    )

    flight_info["duration_minutes"], flight_info["duration_str"] = extract_duration(
        flight_description
    )

    flight_info["carry_on_bags"], flight_info["checked_bags"] = extract_baggage_info(
        flight_description
    )
    return flight_info


def _extract_attribute_with_retry(
    page: Page,
    selector: str,
    attribute: str,
    max_retries: int = 3,
    sleep_s: float = 0.5,
):
    """Extract attribute from element with retry for handling dynamic content.

    Args:
        page (Page): Playwright Page instance
        selector (str): CSS selector to locate element
        attribute (str): Attribute name to extract
        max_retries (int): Number of retry attempts
        sleep_s (float): Sleep duration between retries

    Returns:
        str | None: Attribute value, or None if not found after retries
    """
    for attempt in range(max_retries):
        try:
            element = page.locator(selector)
            return element.first.get_attribute(attribute)

        except PlaywrightTimeoutError:
            if attempt == max_retries - 1:
                return None
            time.sleep(sleep_s)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error extracting attribute: {e}", file=sys.stderr)
                return None
            time.sleep(sleep_s)

    return None


def extract_final_price(page: Page, timeout: int):
    """Extract the final price from the booking page.

    Args:
        page (Page): Playwright Page instance
        timeout (int): Timeout for waiting operations

    Returns:
        int: Final price in US dollars, or None if not found
    """
    # Wait for page to fully load
    wait_until_stable(
        page,
        "div[role='progressbar']",
        stable_duration=2.0,
        timeout=timeout,
    )

    # Target the specific price element near "Lowest total price" text
    selector = "div:has-text('Lowest total price') + div span[aria-label*='US dollars']"

    # Get aria-label with retry
    aria_label = _extract_attribute_with_retry(page, selector, "aria-label")

    # Check if aria_label is not None before regex
    if aria_label and (m := re.search(r"(\d+(?:,\d{3})*) US dollars", aria_label)):
        return int(m.group(1).replace(",", ""))

    return None


def _extract_text_with_retry(
    page: Page,
    selector: str,
    max_retries: int = 3,
    sleep_s: float = 0.5,
):
    """Extract text from element with retry for handling dynamic content.

    Args:
        page (Page): Playwright Page instance
        selector (str): CSS selector to locate element
        max_retries (int): Number of retry attempts
        sleep_s (float): Sleep duration between retries

    Returns:
        str | None: Element text, or None if not found after retries
    """
    for attempt in range(max_retries):
        try:
            element = page.locator(selector)
            return element.first.inner_text()

        except PlaywrightTimeoutError:
            if attempt == max_retries - 1:
                return None
            time.sleep(sleep_s)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error extracting text: {e}", file=sys.stderr)
                return None
            time.sleep(sleep_s)

    return None


def extract_price_classification_text(page: Page, timeout: int):
    """Find and extract the price classification text from the page.

    Args:
        page (Page): Playwright Page instance
        timeout (int): Timeout for waiting operations

    Returns:
        str: Text containing price classification, or None if not found
    """
    # Wait for page to load
    wait_until_stable(
        page,
        "div[role='progressbar']",
        stable_duration=2.0,
        timeout=timeout,
    )

    # Look for div containing "low", "high", or "typical" in Price insights section
    selector = (
        "h3:has-text('Price insights') ~ * "
        "div:has-text(' is '):has-text(' for '):has(span:text-matches('low|high|typical', 'i'))"
    )

    return _extract_text_with_retry(page, selector)


def parse_price_classification(text: str):
    """Parse classification from price relativity text.

    Args:
        text (str): Text containing price classification

    Returns:
        str: 'low', 'high', 'typical', or None
    """
    if not text:
        return None

    text_lower = text.lower()

    if "low" in text_lower:
        return "low"
    elif "high" in text_lower:
        return "high"
    elif "typical" in text_lower:
        return "typical"

    return None


def parse_price_difference(text: str):
    """Parse price difference amount from price relativity text.

    Args:
        text (str): Text containing price difference

    Returns:
        int: Amount saved (for 'cheaper'), 0 (for 'high'/'typical'), or None
    """
    if not text:
        return None

    text_lower = text.lower()

    if "cheaper" in text_lower:
        # Extract dollar amount
        if m := re.search(r"\$(\d+(?:,\d{3})*)\s+cheaper", text):
            return int(m.group(1).replace(",", ""))
        return 0
    elif "low" in text_lower or "high" in text_lower or "typical" in text_lower:
        # For "high" or "typical", amount is 0
        return 0

    return None


def extract_price_relativity(page: Page, timeout: int):
    """Extract price relativity information from final page.

    Args:
        page (Page): Playwright Page instance
        timeout (int): Timeout for waiting operations

    Returns:
        tuple: (classification, amount) where classification is one of
               'typical', 'high', 'low', or None; amount is integer or None
    """
    # Extract the text from the page
    text = extract_price_classification_text(page, timeout)

    if not text:
        return None, None

    # Parse classification and amount
    classification = parse_price_classification(text)
    amount = parse_price_difference(text)

    return classification, amount

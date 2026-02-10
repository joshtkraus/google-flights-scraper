"""Page interaction functions for Google Flights scraper."""

import time

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from .config_browser import SEAT_CLASS_OPTION_MAPPING


def enter_departure_airport(page: Page, airport_code: str):
    """Enter departure airport code into input field.

    Args:
        page (Page): Playwright Page instance
        airport_code (str): IATA code for departure airport

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    try:
        from_input = page.locator("input[aria-label='Where from?']")
        from_input.wait_for(state="visible")
        from_input.click()
        time.sleep(1)

        from_popup = page.locator("input[aria-label*='Where else?']").nth(1)
        from_popup.wait_for(state="visible")
        from_popup.clear()
        from_popup.fill(airport_code)
        from_popup.press("ArrowDown")
        from_popup.press("Enter")
    except PlaywrightTimeoutError as e:
        raise Exception("Error entering departure airport:") from e


def enter_arrival_airport(page: Page, airport_code: str):
    """Enter arrival airport code into input field.

    Args:
        page (Page): Playwright Page instance
        airport_code (str): IATA code for arrival airport

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    try:
        to_input = page.locator("input[aria-label='Where to? ']")
        to_input.wait_for(state="visible")
        to_input.click()

        to_popup = page.locator("input[aria-label*='Where to?']").nth(1)
        to_popup.wait_for(state="visible")
        to_popup.clear()
        to_popup.fill(airport_code)
        to_popup.press("ArrowDown")
        to_popup.press("Enter")
    except PlaywrightTimeoutError as e:
        raise Exception("Error entering arrival airport:") from e


def enter_airports(page: Page, airport_code_from: str, airport_code_to: str):
    """Enter both departure and arrival airport codes.

    Args:
        page (Page): Playwright Page instance
        airport_code_from (str): IATA code for departure airport
        airport_code_to (str): IATA code for arrival airport
    """
    enter_departure_airport(page, airport_code_from)
    enter_arrival_airport(page, airport_code_to)


def enter_departure_date(page: Page, date_from: str):
    """Enter departure date into input field.

    Args:
        page (Page): Playwright Page instance
        date_from (str): Departure date in MM/DD/YYYY format

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    try:
        departure_input = page.locator("input[aria-label='Departure']").first
        departure_input.wait_for(state="visible")
        departure_input.click()
        time.sleep(1)

        departure_popup = page.locator("input[aria-label='Departure']").nth(1)
        departure_popup.wait_for(state="visible")
        departure_popup.fill(date_from)
    except PlaywrightTimeoutError as e:
        raise Exception("Error entering departure date:") from e


def enter_return_date(page: Page, date_to: str):
    """Enter return date into input field.

    Args:
        page (Page): Playwright Page instance
        date_to (str): Return date in MM/DD/YYYY format

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    try:
        return_popup = page.locator("input[aria-label='Return']").nth(1)
        return_popup.wait_for(state="visible")
        return_popup.fill(date_to)
        return_popup.press("Enter")
        return_popup.press("Enter")
    except PlaywrightTimeoutError as e:
        raise Exception("Error entering return date:") from e


def enter_dates(page: Page, date_from: str, date_to: str):
    """Enter both departure and return dates.

    Args:
        page (Page): Playwright Page instance
        date_from (str): Departure date in MM/DD/YYYY format
        date_to (str): Return date in MM/DD/YYYY format
    """
    enter_departure_date(page, date_from)
    enter_return_date(page, date_to)


def select_seat_class(page: Page, seat_class: str, is_domestic_us: bool):
    """Select seat class from dropdown.

    Args:
        page (Page): Playwright Page instance
        seat_class (str): Seat class to select
        is_domestic_us (bool): Whether flight is domestic US

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    try:
        class_dropdown = page.locator(
            "div[role='combobox']:has(span[aria-label='Change seating class.'])"
        )
        class_dropdown.wait_for(state="visible")
        class_dropdown.click()

        # Get all options
        listbox = page.locator("ul[role='listbox']").nth(1)
        listbox.wait_for(state="visible")

        # Selct correct option
        class_options = page.locator("ul[role='listbox']").nth(1).locator("li[role='option']")
        option_index = SEAT_CLASS_OPTION_MAPPING[is_domestic_us][seat_class.lower()]
        class_options.nth(option_index).wait_for(state="visible")
        class_options.nth(option_index).click()
    except PlaywrightTimeoutError as e:
        raise Exception("Error selecting seat class:") from e


def press_search_button(page: Page):
    """Press the search button to initiate flight search.

    Args:
        page (Page): Playwright Page instance

    Raises:
        Exception: If search button cannot be found or clicked
    """
    try:
        search_button = page.locator("button[aria-label='Search']")
        search_button.wait_for(state="visible")
        search_button.click()
    except PlaywrightTimeoutError as e:
        raise Exception("Error pressing search button:") from e


def wait_until_stable(
    page: Page, selector: str, stable_duration: float = 2.0, timeout: int = 10000
):
    """Wait until an element's class attribute stops changing.

    Args:
        page (Page): Playwright Page instance
        selector (str): CSS selector for the element
        stable_duration (float): How long (in seconds) the class must remain unchanged
        timeout (int): Maximum time to wait before raising TimeoutError

    Raises:
        TimeoutError: If element class does not stabilize within timeout
    """
    start_time = time.time()
    timeout_seconds = timeout / 1000
    previous_class = None
    first_read = True
    stable_since = None

    while True:
        if time.time() - start_time > timeout_seconds:
            raise TimeoutError(f"Element class did not stabilize within {timeout_seconds} seconds")

        try:
            element = page.locator(selector).nth(0)

            # Wait for element to exist
            if element.count() == 0:
                first_read = True
                previous_class = None
                stable_since = None
                time.sleep(0.1)
                continue

            current_class = element.get_attribute("class")

            # On first read, just store the class
            if first_read:
                previous_class = current_class
                stable_since = time.time()
                first_read = False
            elif current_class == previous_class:
                if stable_since is not None:
                    # Class hasn't changed, check if stable long enough
                    if time.time() - stable_since >= stable_duration:
                        time.sleep(1)
                        break
            else:
                # Class changed, reset the timer
                previous_class = current_class
                stable_since = time.time()

            time.sleep(0.1)  # Check every 100ms

        except Exception:
            # Element not found yet, keep waiting
            first_read = True
            previous_class = None
            stable_since = None
            time.sleep(0.1)


def find_and_select_best_flight(page: Page, timeout: int):
    """Find and return the best (first) flight option on the page.

    Args:
        page (Page): Playwright Page instance
        timeout (int): Timeout for waiting operations

    Returns:
        Locator: The best flight element locator, or None if not found
    """
    # Wait for page to fully load
    wait_until_stable(
        page,
        "div[role='progressbar']",
        stable_duration=2.0,
        timeout=timeout,
    )

    # Find best flight (first option)
    try:
        best_flight = page.locator("ul[role='list']").nth(1).locator("li").nth(0)
        return best_flight
    except PlaywrightTimeoutError:
        return None

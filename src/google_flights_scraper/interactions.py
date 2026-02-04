"""Page interaction functions for Google Flights scraper."""

import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .config_browser import SEAT_CLASS_OPTION_MAPPING


def enter_departure_airport(wait: WebDriverWait, airport_code: str):
    """Enter departure airport code into input field.

    Args:
        wait (WebDriverWait): WebDriverWait instance
        airport_code (str): IATA code for departure airport

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    try:
        from_input = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@aria-label='Where from?']"),
            )
        )
    except TimeoutException as e:
        raise Exception("Error entering departure airport:") from e

    from_input.click()
    time.sleep(1)
    from_popup = wait.until(
        EC.presence_of_all_elements_located((
            By.XPATH,
            "//input[contains(@aria-label,'Where else?')]",
        ))
    )[1]
    from_popup.clear()
    from_popup.send_keys(airport_code)
    from_popup.send_keys(Keys.DOWN)
    from_popup.send_keys(Keys.ENTER)


def enter_arrival_airport(wait: WebDriverWait, airport_code: str):
    """Enter arrival airport code into input field.

    Args:
        wait (WebDriverWait): WebDriverWait instance
        airport_code (str): IATA code for arrival airport

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    try:
        to_input = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@aria-label='Where to? ']"),
            )
        )
    except TimeoutException as e:
        raise Exception("Error entering arrival airport:") from e

    to_input.click()
    to_popup = wait.until(
        EC.presence_of_all_elements_located((
            By.XPATH,
            "//input[contains(@aria-label,'Where to?')]",
        ))
    )[1]
    to_popup.clear()
    to_popup.send_keys(airport_code)
    to_popup.send_keys(Keys.DOWN)
    to_popup.send_keys(Keys.ENTER)


def enter_airports(wait: WebDriverWait, airport_code_from: str, airport_code_to: str):
    """Enter both departure and arrival airport codes.

    Args:
        wait (WebDriverWait): WebDriverWait instance
        airport_code_from (str): IATA code for departure airport
        airport_code_to (str): IATA code for arrival airport
    """
    enter_departure_airport(wait, airport_code_from)
    enter_arrival_airport(wait, airport_code_to)


def enter_departure_date(wait: WebDriverWait, date_from: str):
    """Enter departure date into input field.

    Args:
        wait (WebDriverWait): WebDriverWait instance
        date_from (str): Departure date in MM/DD/YYYY format

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    try:
        departure_input = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@aria-label='Departure']"),
            )
        )
    except TimeoutException as e:
        raise Exception("Error entering departure date:") from e

    departure_input.click()
    time.sleep(1)

    try:
        departure_popup = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//input[@aria-label='Departure']"),
            )
        )[1]
    except TimeoutException as e:
        raise Exception("Error entering departure date:") from e

    departure_popup.send_keys(date_from)


def enter_return_date(wait: WebDriverWait, date_to: str):
    """Enter return date into input field.

    Args:
        wait (WebDriverWait): WebDriverWait instance
        date_to (str): Return date in MM/DD/YYYY format

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    try:
        return_popup = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//input[@aria-label='Return']"),
            )
        )[1]
    except TimeoutException as e:
        raise Exception("Error entering return date:") from e

    return_popup.send_keys(date_to)
    return_popup.send_keys(Keys.ENTER)
    return_popup.send_keys(Keys.ENTER)


def enter_dates(wait: WebDriverWait, date_from: str, date_to: str):
    """Enter both departure and return dates.

    Args:
        wait (WebDriverWait): WebDriverWait instance
        date_from (str): Departure date in MM/DD/YYYY format
        date_to (str): Return date in MM/DD/YYYY format
    """
    enter_departure_date(wait, date_from)
    enter_return_date(wait, date_to)


def select_seat_class(wait: WebDriverWait, seat_class: str, is_domestic_us: bool):
    """Select seat class from dropdown.

    Args:
        wait (WebDriverWait): WebDriverWait instance
        seat_class (str): Seat class to select
        is_domestic_us (bool): Whether flight is domestic US

    Raises:
        Exception: If elements cannot be found or interacted with
    """
    # Find and click dropdown
    try:
        class_dropdown = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@role='combobox' and .//span[@aria-label='Change seating class.']]",
                ),
            )
        )
    except TimeoutException as e:
        raise Exception("Error selecting seat class:") from e
    class_dropdown.click()

    # Get options and select
    try:
        class_options = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//li[@role='option']"),
            )
        )
    except TimeoutException as e:
        raise Exception("Error selecting seat class:") from e

    option_index = SEAT_CLASS_OPTION_MAPPING[is_domestic_us][seat_class]
    class_options[option_index].click()


def press_search_button(wait: WebDriverWait):
    """Press the search button to initiate flight search.

    Args:
        wait (WebDriverWait): WebDriverWait instance

    Raises:
        Exception: If search button cannot be found or clicked
    """
    try:
        search_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@aria-label="Search"]'),
            )
        )
    except TimeoutException as e:
        raise Exception("Error pressing search button:") from e
    search_button.click()


def wait_until_class_stable(
    driver: Chrome, locator: tuple, stable_duration: float = 1.0, timeout: int = 10
):
    """Wait until an element's class attribute stops changing.

    Args:
        driver (Chrome): Selenium WebDriver instance
        locator (tuple): Tuple of (By.*, 'selector') e.g., (By.ID, 'my-div')
        stable_duration (float): How long (in seconds) the class must remain unchanged
        timeout (int): Maximum time to wait before raising TimeoutException

    Raises:
        TimeoutException: If element class does not stabilize within timeout
    """
    start_time = time.time()
    previous_class = None
    first_read = True

    while True:
        if time.time() - start_time > timeout:
            raise TimeoutException(f"Element class did not stabilize within {timeout} seconds")

        try:
            element = driver.find_element(*locator)
            current_class = element.get_attribute("class")

            # On first read, just store the class
            if first_read:
                previous_class = current_class
                stable_since = time.time()
                first_read = False
            elif current_class == previous_class:
                # Class hasn't changed, check if stable long enough
                if time.time() - stable_since >= stable_duration:
                    break
            else:
                # Class changed, reset the timer
                previous_class = current_class
                stable_since = time.time()

            time.sleep(0.1)  # Check every 100ms

        except NoSuchElementException:
            # Element not found yet, keep waiting
            first_read = True
            previous_class = None
            stable_since = None
            time.sleep(0.1)


def find_and_select_best_flight(wait: WebDriverWait, driver: Chrome, timeout: int):
    """Find and click the best (first) flight option on the page.

    Args:
        wait (WebDriverWait): WebDriverWait instance
        driver (Chrome): Selenium WebDriver instance
        timeout (int): Timeout for waiting operations

    Returns:
        WebElement: The selected flight element, or None if not found
    """
    # Wait for page to fully load
    wait_until_class_stable(
        driver,
        (By.XPATH, "//div[@role='progressbar']"),
        stable_duration=1.0,
        timeout=timeout,
    )

    # Find best flight (first option)
    try:
        best_flight = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@aria-label='Select flight']/ancestor::li"),
            )
        )
    except TimeoutException:
        return None

    return best_flight

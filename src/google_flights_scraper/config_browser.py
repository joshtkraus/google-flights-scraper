"""Configuration constants and browser setup for Google Flights scraper."""

import random

from fake_useragent import UserAgent
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
from playwright_stealth import Stealth

# Initialise UA database
_ua = UserAgent(browsers=["Chrome"])

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
        "economy (include basic)": 0,
        "economy (exclude basic)": 1,
        "premium economy": 2,
        "business": 3,
        "first": 4,
    },
    False: {  # International
        "economy": 0,
        "premium economy": 1,
        "business": 2,
        "first": 3,
    },
}

# Realistic viewport + device scale factor pairs.
VIEWPORT_PROFILES = [
    # 1080p monitors
    {"width": 1920, "height": 1080, "device_scale_factor": 1.0},
    {"width": 1920, "height": 1080, "device_scale_factor": 1.0},
    # 1440p / QHD monitors
    {"width": 2560, "height": 1440, "device_scale_factor": 2.0},
    {"width": 2560, "height": 1440, "device_scale_factor": 2.0},
    # MacBook Pro retina
    {"width": 1440, "height": 900, "device_scale_factor": 2.0},
    # MacBook Air / older laptops
    {"width": 1280, "height": 800, "device_scale_factor": 2.0},
    # Common budget/older laptop resolution
    {"width": 1366, "height": 768, "device_scale_factor": 1.0},
    # 4K monitors
    {"width": 3840, "height": 2160, "device_scale_factor": 2.0},
]

# US timezones
US_TIMEZONES = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
]

# Default timeout (ms)
DEFAULT_TIMEOUT = 10000  # 10 seconds


def get_random_viewport_profile() -> dict:
    """Return a random realistic viewport profile.

    Returns:
        dict: A dict with width, height, and device_scale_factor keys
    """
    return random.choice(VIEWPORT_PROFILES).copy()


def get_random_timezone() -> str:
    """Return a random US timezone weighted by population.

    Returns:
        str: A timezone string compatible with Playwright's timezone_id
    """
    return random.choice(US_TIMEZONES)


def get_random_user_agent() -> str:
    """Return a random Chrome user agent string from the fake-useragent database.

    Returns:
        str: A randomly selected Chrome user agent string
    """
    return str(_ua.random)


async def setup_browser() -> tuple[Playwright, Browser, BrowserContext, Page]:
    """Setup Playwright browser with appropriate options and a randomized user agent.

    Returns:
        tuple: (playwright instance, browser, context, page)
    """
    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-gpu",
            "--start-maximized",
        ],
    )

    viewport_profile = get_random_viewport_profile()

    context = await browser.new_context(
        viewport={
            "width": viewport_profile["width"],
            "height": viewport_profile["height"],
        },
        device_scale_factor=viewport_profile["device_scale_factor"],
        user_agent=get_random_user_agent(),
        locale="en-US",
        timezone_id=get_random_timezone(),
    )

    # Block images, fonts, media to speed up
    await context.route(
        "**/*.{png,jpg,jpeg,gif,svg,woff,woff2,mp4,webm}", lambda route: route.abort()
    )
    # Block analytics
    await context.route("**/analytics.google.com/**", lambda route: route.abort())
    await context.route("**/googletagmanager.com/**", lambda route: route.abort())

    page = await context.new_page()
    await Stealth().apply_stealth_async(page)
    page.set_default_timeout(DEFAULT_TIMEOUT)

    return playwright, browser, context, page

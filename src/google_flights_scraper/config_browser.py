"""Configuration constants and browser setup for Google Flights scraper."""

import random

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

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

# Default timeout (ms)
DEFAULT_TIMEOUT = 10000  # 10 seconds

# Realistic Chrome user agents across Windows, macOS, Linux
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]


def get_random_user_agent() -> str:
    """Return a random user agent string from the pool.

    Returns:
        str: A randomly selected user agent string
    """
    return random.choice(USER_AGENTS)


async def setup_browser() -> tuple[Playwright, Browser, BrowserContext, Page]:
    """Setup Playwright browser with appropriate options and a randomized user agent.

    Returns:
        tuple: (playwright instance, browser, context, page)
    """
    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-gpu",
            "--start-maximized",
        ],
    )

    context = await browser.new_context(
        no_viewport=True,
        user_agent=get_random_user_agent(),
    )

    # Block images, fonts, media to speed up
    await context.route(
        "**/*.{png,jpg,jpeg,gif,svg,woff,woff2,mp4,webm}", lambda route: route.abort()
    )
    # Block analytics
    await context.route("**/analytics.google.com/**", lambda route: route.abort())
    await context.route("**/googletagmanager.com/**", lambda route: route.abort())

    page = await context.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)

    return playwright, browser, context, page

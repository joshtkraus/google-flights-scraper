"""Configuration constants and browser setup for Google Flights scraper."""

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

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


def setup_browser() -> tuple[Playwright, Browser, BrowserContext, Page]:
    """Setup Playwright browser with appropriate options.

    Returns:
        tuple: (playwright instance, browser, context, page)
    """
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-gpu",
            "--start-maximized",
        ],
    )

    context = browser.new_context(no_viewport=True)

    # Block images, fonts, media to speed up
    context.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,mp4,webm}", lambda route: route.abort())
    # Block analytics
    context.route("**/analytics.google.com/**", lambda route: route.abort())
    context.route("**/googletagmanager.com/**", lambda route: route.abort())

    page = context.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)

    return playwright, browser, context, page

"""
Constants and default values for SERP Agent
"""

# User Agent strings
DESKTOP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

MOBILE_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 12; Pixel 5) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
)

# Window sizes
DESKTOP_WINDOW_SIZE = {"width": 1366, "height": 820}
MOBILE_WINDOW_SIZE = {"width": 393, "height": 851}

# Mobile device metrics (Pixel 5)
MOBILE_DEVICE_METRICS = {
    "width": 393,
    "height": 851,
    "deviceScaleFactor": 2.75,
    "mobile": True
}

# Timeouts (in seconds)
DEFAULT_SERP_TIMEOUT = 12
DEFAULT_ELEMENT_WAIT = 10
DEFAULT_CHALLENGE_WAIT = 8
SHORT_WAIT = 1.5
NAVIGATION_WAIT = 1.0

# Scroll and pagination settings
DEFAULT_SCROLL_STEP_PX = 700
DEFAULT_MAX_SCROLL_STEPS = 10
DEFAULT_MAX_PAGES = 6

# Chrome arguments
CHROME_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--lang=es-ES,es",
    "--force-device-scale-factor=1",
]

# Cookie consent selectors (includes Spanish)
COOKIE_CONSENT_SELECTORS = [
    "//button//*[contains(text(),'Accept')]/ancestor::button",
    "//button[contains(., 'Accept')]",
    "//button[contains(., 'I agree')]",
    "//button[contains(., 'Aceptar')]",
    "//button[contains(., 'Aceptar todo')]",
    "//button[contains(., 'Aceptar todas')]",
    "//div[contains(@role,'button') and (contains(.,'Accept') or contains(.,'I agree') or contains(.,'Aceptar'))]"
]

IFRAME_CONSENT_SELECTORS = [
    "//button//*[contains(text(),'Accept')]/ancestor::button",
    "//button[contains(., 'Accept all')]",
    "//button[contains(., 'I agree')]",
    "//button[contains(., 'Aceptar todo')]",
    "//button[contains(., 'Aceptar todas')]",
    "//button[@aria-label='Accept all']",
    "//button[@aria-label='Aceptar todo']",
]

# More results control selectors (mobile)
MORE_RESULTS_SELECTORS = [
    (["xpath", "//*[@aria-label='More results']"]),
    (["xpath", "//*[self::a or self::button or @role='button'][.//span[normalize-space()='More results'] or contains(normalize-space(.),'More results')]"]),
    (["xpath", "//div[@role='button' and .//span[contains(.,'More results')]]"]),
    (["xpath", "//*[@role='button' and contains(.,'More') and contains(.,'result')]"]),
]

# Navigation selectors
NEXT_PAGE_SELECTORS = [
    (["css", "a#pnnext"]),
    (["css", "a[aria-label='Next']"]),
    (["xpath", "//a[.//span[normalize-space()='Next']]"]),
    (["xpath", "//a[contains(@aria-label,'Next')]"]),
]

# Default proxy settings
DEFAULT_PROXY_HOST = "gate.decodo.com"
DEFAULT_PROXY_PORT = "10001"

# History files to clean
HISTORY_FILES = [
    "History", "History-journal", "History-wal", "History-shm",
    "Archived History", "Archived History-journal", "Archived History-wal", "Archived History-shm",
    "History Provider Cache",
    "Visited Links",
    "Top Sites", "Top Sites-journal",
    "Shortcuts",
    "Network Action Predictor",
]

# Search engine URLs (Spanish)
GOOGLE_URL = "https://www.google.com.mx"  # Mexico Google for Spanish searches
BING_URL = "https://www.bing.com/?setlang=es"
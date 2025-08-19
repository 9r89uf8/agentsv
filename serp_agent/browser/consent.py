"""
Cookie consent and GDPR handling
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..config.constants import COOKIE_CONSENT_SELECTORS, IFRAME_CONSENT_SELECTORS
from ..logging.logger import log


def accept_cookies_if_present(driver):
    """
    Handle common consent flows, including consent iframes.
    
    Args:
        driver: WebDriver instance
    """
    time.sleep(0.6)
    
    # Try top-level consent buttons
    for sel in COOKIE_CONSENT_SELECTORS:
        try:
            btn = WebDriverWait(driver, 1.5).until(EC.element_to_be_clickable((By.XPATH, sel)))
            btn.click()
            time.sleep(0.4)
            log("Accepted cookies (top-level).")
            return
        except Exception:
            pass

    # Try consent buttons inside iframes
    try:
        iframes = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='consent'],iframe[src*='consent.google']")
        for fr in iframes:
            driver.switch_to.frame(fr)
            try:
                for ib in IFRAME_CONSENT_SELECTORS:
                    try:
                        btn = WebDriverWait(driver, 1.5).until(EC.element_to_be_clickable((By.XPATH, ib)))
                        btn.click()
                        time.sleep(0.4)
                        driver.switch_to.default_content()
                        log("Accepted cookies (iframe).")
                        return
                    except Exception:
                        continue
            finally:
                driver.switch_to.default_content()
    except Exception:
        pass
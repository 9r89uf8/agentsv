"""
SERP scanning and pagination strategies
"""
import time
from typing import Optional, Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from ..net.url_utils import extract_final_url, url_matches_domain
from ..browser.actions import click_safely, robust_tap, find_more_results_control
from ..browser.diagnostics import dump_serp_snapshot
from ..config.constants import NEXT_PAGE_SELECTORS
from ..logging.logger import log


def progressive_scroll_and_scan(
    driver,
    target_domain: str,
    seen_hrefs: Optional[Set[str]] = None,
    max_steps: int = 10,
    step_px: int = 700
) -> bool:
    """
    Scroll down the page in steps, scanning for matching anchors after each step.
    Adds staggered delays to look less bursty.
    
    Args:
        driver: WebDriver instance
        target_domain: Domain to search for
        seen_hrefs: Set of already seen URLs to avoid duplicates
        max_steps: Maximum number of scroll steps
        step_px: Pixels to scroll in each step
        
    Returns:
        True if target domain was found and clicked, False otherwise
    """
    if seen_hrefs is None:
        seen_hrefs = set()

    last_height = driver.execute_script("return document.body.scrollHeight") or 0

    for i in range(max_steps):
        anchors = driver.find_elements(By.XPATH, "//div[@id='search']//a[@href] | //div[@id='rso']//a[@href]")
        for a in anchors:
            try:
                href = a.get_attribute("href")
                if not href or href in seen_hrefs:
                    continue
                seen_hrefs.add(href)
                final_url = extract_final_url(href)
                if url_matches_domain(final_url, target_domain):
                    log(f"Found target on step {i+1}: {final_url}")
                    click_safely(driver, a)
                    return True
            except WebDriverException:
                continue

        driver.execute_script("window.scrollBy(0, arguments[0]);", step_px)
        time.sleep(0.6 + (0.4 * (i % 3)))  # staggered delay

        try:
            new_height = driver.execute_script("return document.body.scrollHeight") or last_height
            if new_height > last_height:
                last_height = new_height
        except Exception:
            pass

    # Final scan at bottom
    anchors = driver.find_elements(By.XPATH, "//div[@id='search']//a[@href] | //div[@id='rso']//a[@href]")
    for a in anchors:
        try:
            href = a.get_attribute("href")
            if not href or href in seen_hrefs:
                continue
            final_url = extract_final_url(href)
            if url_matches_domain(final_url, target_domain):
                log("Found target on final bottom scan.")
                click_safely(driver, a)
                return True
        except WebDriverException:
            continue

    return False


def attempt_load_more_or_next(driver) -> bool:
    """
    Desktop: click Next.
    Mobile: find/tap 'More results' (touch), else try infinite scroll, else bail.
    Returns True if more results were loaded or navigation occurred.
    
    Args:
        driver: WebDriver instance
        
    Returns:
        True if more results were loaded, False otherwise
    """
    # First: classic "Next" (desktop)
    classic = [
        (By.CSS_SELECTOR, "a#pnnext"),
        (By.CSS_SELECTOR, "a[aria-label='Next']"),
        (By.XPATH, "//a[.//span[normalize-space()='Next']]"),
        (By.XPATH, "//a[contains(@aria-label,'Next')]"),
    ]
    for by, sel in classic:
        try:
            ctl = WebDriverWait(driver, 2.0).until(EC.element_to_be_clickable((by, sel)))
            before = driver.execute_script("return document.body.scrollHeight")
            click_safely(driver, ctl)
            time.sleep(1.0)
            after = driver.execute_script("return document.body.scrollHeight")
            if after and before and after != before:
                log("Triggered next page (desktop).")
                return True
        except Exception:
            pass

    # Mobile: explicit "More results" control
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 400);")
    except Exception:
        pass

    btn = find_more_results_control(driver, timeout=2.5)
    if btn:
        before = driver.execute_script("return document.body.scrollHeight")
        if robust_tap(driver, btn):
            time.sleep(1.2)
            # consider "growth" or new results present as success
            try:
                WebDriverWait(driver, 6).until(
                    lambda d: (d.execute_script("return document.readyState") == "complete") or
                              (d.execute_script("return document.body.scrollHeight") > before)
                )
            except Exception:
                pass
            after = driver.execute_script("return document.body.scrollHeight")
            if after and before and after > before:
                log("More results loaded via 'More results' button.")
                return True

    # Stronger infinite scroll fallback (mobile)
    try:
        before = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.9)
        driver.execute_script("window.scrollBy(0, -120);"); driver.execute_script("window.scrollBy(0, 240);")
        time.sleep(0.9)
        after = driver.execute_script("return document.body.scrollHeight")
        if after and before and after > before:
            log("More results loaded via infinite scroll.")
            return True
    except Exception:
        pass

    # Last resort: snapshot for proof/debugging
    dump_serp_snapshot(driver, tag="serp_bottom")
    log("No next control and no additional content detected.")
    return False
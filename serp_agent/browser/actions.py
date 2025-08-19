"""
Browser interaction utilities - clicks, taps, scrolling
"""
import time
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from ..config.constants import MORE_RESULTS_SELECTORS
from ..logging.logger import log


def click_safely(driver, element):
    """
    Safely click an element with fallback to JavaScript click.
    
    Args:
        driver: WebDriver instance
        element: WebElement to click
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(0.12)
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)


def find_more_results_control(driver, timeout=4.0):
    """
    Returns the 'More results' control if present/visible (mobile SERP).
    We try multiple shapes: role=button, <a>, <div role=button>, etc.
    
    Args:
        driver: WebDriver instance
        timeout: Timeout in seconds
        
    Returns:
        WebElement if found, None otherwise
    """
    locators = [
        (By.XPATH, "//*[@aria-label='More results']"),
        (By.XPATH, "//*[self::a or self::button or @role='button'][.//span[normalize-space()='More results'] or contains(normalize-space(.),'More results')]"),
        (By.XPATH, "//div[@role='button' and .//span[contains(.,'More results')]]"),
        # fallback: anything with role=button near the bottom area
        (By.XPATH, "//*[@role='button' and contains(.,'More') and contains(.,'result')]"),
    ]
    end = time.time() + timeout
    while time.time() < end:
        for by, sel in locators:
            try:
                elements = driver.find_elements(by, sel)
                for el in elements:
                    if el.is_displayed():
                        return el
            except Exception:
                pass
        time.sleep(0.15)
    return None


def robust_tap(driver, el) -> bool:
    """
    Try to activate a mobile control in the most bulletproof way:
    - center scroll + blur any focused field
    - native .click()
    - JS click()
    - pointer/touch events
    - DevTools CDP touch injection at element center
    
    Args:
        driver: WebDriver instance
        el: WebElement to tap
        
    Returns:
        True if tap was successful, False otherwise
    """
    try:
        driver.execute_script("document.activeElement && document.activeElement.blur();")
    except Exception:
        pass

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", el)
        time.sleep(0.2)
    except Exception:
        pass

    # 1) normal click
    try:
        el.click()
        return True
    except Exception:
        pass

    # 2) JS click
    try:
        driver.execute_script("arguments[0].click();", el)
        return True
    except Exception:
        pass

    # 3) pointer/touch events on the element
    try:
        js = """
        const el = arguments[0];
        const fire = (type, opts={}) => el.dispatchEvent(new PointerEvent(type, Object.assign({
            bubbles:true, cancelable:true, composed:true, pointerType:'touch', isPrimary:true
        }, opts)));
        fire('pointerdown'); fire('pointerup');
        el.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, composed:true}));
        return true;
        """
        driver.execute_script(js, el)
        return True
    except Exception:
        pass

    # 4) DevTools: tap at element center (CSS pixels in main frame viewport)
    try:
        rect = driver.execute_script("""
            const r = arguments[0].getBoundingClientRect();
            return {x: r.left + r.width/2, y: r.top + r.height/2};
        """, el)
        x, y = float(rect["x"]), float(rect["y"])

        # small jiggle to unstick sticky overlays
        try:
            driver.execute_script("window.scrollBy(0, -40);"); time.sleep(0.05)
            driver.execute_script("window.scrollBy(0,  60);"); time.sleep(0.05)
        except Exception:
            pass

        # touch start/end = tap
        driver.execute_cdp_cmd("Input.dispatchTouchEvent", {
            "type": "touchStart",
            "touchPoints": [{"x": x, "y": y, "radiusX": 2, "radiusY": 2, "force": 1}]
        })
        driver.execute_cdp_cmd("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        return True
    except Exception as e:
        log(f"[tap] CDP tap failed: {e}")

    return False
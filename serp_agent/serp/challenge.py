"""
Search engine challenge and captcha detection
"""
from selenium.webdriver.common.by import By


def is_google_challenge(driver) -> bool:
    """
    Return True if Google 'unusual traffic' / challenge page is shown.
    
    Args:
        driver: WebDriver instance
        
    Returns:
        True if a challenge/captcha page is detected
    """
    try:
        title = (driver.title or "").lower()
        if "unusual traffic" in title or "sorry" in title:
            return True
            
        if driver.find_elements(By.CSS_SELECTOR, 'form[action*="sorry"], #captcha, img[alt*="captcha"]'):
            return True
            
        texts = driver.find_elements(
            By.XPATH,
            "//*[contains(translate(., 'UNUSUAL TRAFFIC', 'unusual traffic'), 'unusual traffic') "
            "or contains(translate(., 'VERIFY YOU ARE A HUMAN', 'verify you are a human'), 'verify you are a human')]"
        )
        return len(texts) > 0
    except Exception:
        return False
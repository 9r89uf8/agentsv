"""
Google search engine implementation
"""
import time
from typing import Set
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .base import SearchEngine, SearchStatus
from .challenge import is_google_challenge
from .scan_strategies import progressive_scroll_and_scan, attempt_load_more_or_next
from ..browser.consent import accept_cookies_if_present
from ..config.constants import GOOGLE_URL, DEFAULT_SERP_TIMEOUT, DEFAULT_CHALLENGE_WAIT
from ..logging.logger import log


def ensure_serp_loaded(driver, timeout=12):
    """
    Wait for Google SERP to load.
    
    Args:
        driver: WebDriver instance
        timeout: Timeout in seconds
    """
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#search, #rso"))
    )


class GoogleSearchEngine(SearchEngine):
    """Google search engine implementation"""
    
    def prepare(self, driver) -> bool:
        """
        Navigate to Google homepage and accept cookies.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if preparation was successful
        """
        try:
            driver.get(GOOGLE_URL)
            accept_cookies_if_present(driver)
            return True
        except Exception as e:
            log(f"Failed to prepare Google search: {e}")
            return False
    
    def perform_query(self, driver, query: str) -> SearchStatus:
        """
        Execute search query on Google.
        
        Args:
            driver: WebDriver instance
            query: Search query string
            
        Returns:
            SearchStatus indicating result of query
        """
        try:
            # Enter query
            box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
            box.clear()
            for ch in query:
                box.send_keys(ch)
                time.sleep(0.02)
            box.send_keys(Keys.ENTER)

            # Wait for SERP or challenge
            try:
                WebDriverWait(driver, DEFAULT_CHALLENGE_WAIT).until(
                    lambda d: is_google_challenge(d) or d.find_elements(By.CSS_SELECTOR, "#search, #rso")
                )
            except TimeoutException:
                log("Timed out waiting for SERP or challenge.")
                return SearchStatus.ERROR

            if is_google_challenge(driver):
                log("Google challenge detected. Aborting Google path for this run.")
                return SearchStatus.CHALLENGE
                
            return SearchStatus.CLICKED  # Query successful, ready to search
            
        except Exception as e:
            log(f"Failed to perform Google query: {e}")
            return SearchStatus.ERROR
    
    def find_and_click_target(
        self, 
        driver, 
        target_domain: str, 
        max_pages: int = 5,
        scroll_steps_per_batch: int = 10
    ) -> SearchStatus:
        """
        Search through Google results for target domain.
        
        Args:
            driver: WebDriver instance
            target_domain: Domain to search for
            max_pages: Maximum number of result pages to search
            scroll_steps_per_batch: Scroll steps per page
            
        Returns:
            SearchStatus indicating result
        """
        seen_hrefs: Set[str] = set()

        for page_idx in range(1, max_pages + 1):
            try:
                ensure_serp_loaded(driver, timeout=DEFAULT_SERP_TIMEOUT)
                log(f"Scanning batch {page_idx} ...")

                if progressive_scroll_and_scan(
                    driver,
                    target_domain,
                    seen_hrefs=seen_hrefs,
                    max_steps=scroll_steps_per_batch
                ):
                    return SearchStatus.CLICKED

                # Not found; attempt to load more results (next page or infinite append)
                if not attempt_load_more_or_next(driver):
                    return SearchStatus.NOT_FOUND

            except TimeoutException:
                log("Timed out waiting for results; attempting to load more.")
                if not attempt_load_more_or_next(driver):
                    return SearchStatus.NOT_FOUND
            except Exception as e:
                log(f"Error during Google search: {e}")
                return SearchStatus.ERROR

        return SearchStatus.NOT_FOUND
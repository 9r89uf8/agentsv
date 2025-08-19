"""
Bing search engine implementation
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import SearchEngine, SearchStatus
from ..browser.consent import accept_cookies_if_present
from ..browser.actions import click_safely
from ..net.url_utils import extract_final_url, url_matches_domain
from ..config.constants import BING_URL
from ..logging.logger import log


class BingSearchEngine(SearchEngine):
    """Bing search engine implementation"""
    
    def prepare(self, driver) -> bool:
        """
        Navigate to Bing homepage and accept cookies.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if preparation was successful
        """
        try:
            driver.get(BING_URL)
            accept_cookies_if_present(driver)
            return True
        except Exception as e:
            log(f"Failed to prepare Bing search: {e}")
            return False
    
    def perform_query(self, driver, query: str) -> SearchStatus:
        """
        Execute search query on Bing.
        
        Args:
            driver: WebDriver instance
            query: Search query string
            
        Returns:
            SearchStatus indicating result of query
        """
        try:
            box = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.NAME, "q")))
            box.clear()
            box.send_keys(query)
            box.send_keys(Keys.ENTER)
            return SearchStatus.CLICKED  # Query successful, ready to search
        except Exception as e:
            log(f"Failed to perform Bing query: {e}")
            return SearchStatus.ERROR
    
    def find_and_click_target(
        self, 
        driver, 
        target_domain: str, 
        max_pages: int = 3,  # Bing typically needs fewer pages
        scroll_steps_per_batch: int = 10
    ) -> SearchStatus:
        """
        Search through Bing results for target domain.
        
        Args:
            driver: WebDriver instance
            target_domain: Domain to search for
            max_pages: Maximum number of result pages to search
            scroll_steps_per_batch: Not used for Bing (simple pagination)
            
        Returns:
            SearchStatus indicating result
        """
        try:
            for page_idx in range(1, max_pages + 1):
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ol#b_results")))
                anchors = driver.find_elements(By.CSS_SELECTOR, "ol#b_results li.b_algo h2 a, ol#b_results li.b_algo a")
                
                for a in anchors:
                    href = a.get_attribute("href")
                    final_url = extract_final_url(href)
                    if url_matches_domain(final_url, target_domain):
                        log(f"Found target in Bing results: {final_url}")
                        click_safely(driver, a)
                        return SearchStatus.CLICKED
                
                # Try to go to next page
                try:
                    next_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.sb_pagN, a[title='Next page']"))
                    )
                    click_safely(driver, next_btn)
                    time.sleep(1.0)
                except Exception:
                    # No more pages available
                    break
                    
            return SearchStatus.NOT_FOUND
            
        except Exception as e:
            log(f"Error during Bing search: {e}")
            return SearchStatus.ERROR
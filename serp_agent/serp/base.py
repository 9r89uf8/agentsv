"""
Base classes and interfaces for search engines
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class SearchStatus(Enum):
    """Status of a search operation"""
    CLICKED = "clicked"           # Successfully clicked target domain
    NOT_FOUND = "not_found"       # Target domain not found in results
    CHALLENGE = "challenge"       # Challenge/captcha detected
    ERROR = "error"               # Other error occurred


class SearchEngine(ABC):
    """
    Abstract base class for search engines.
    
    Defines the interface that all search engines must implement.
    """
    
    @abstractmethod
    def prepare(self, driver) -> bool:
        """
        Prepare the search engine (navigate to homepage, accept cookies, etc).
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if preparation was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def perform_query(self, driver, query: str) -> SearchStatus:
        """
        Execute the search query and wait for results.
        
        Args:
            driver: WebDriver instance
            query: Search query string
            
        Returns:
            SearchStatus indicating the result of the query
        """
        pass
    
    @abstractmethod
    def find_and_click_target(
        self, 
        driver, 
        target_domain: str, 
        max_pages: int = 5,
        scroll_steps_per_batch: int = 10
    ) -> SearchStatus:
        """
        Search through results pages looking for target domain and click it.
        
        Args:
            driver: WebDriver instance
            target_domain: Domain to search for and click
            max_pages: Maximum number of pages/batches to search
            scroll_steps_per_batch: Number of scroll steps per batch
            
        Returns:
            SearchStatus indicating the result of the search
        """
        pass
    
    def search_and_click(
        self, 
        driver, 
        query: str, 
        target_domain: str,
        max_pages: int = 5,
        scroll_steps_per_batch: int = 10
    ) -> SearchStatus:
        """
        Complete search workflow: prepare -> query -> find and click.
        
        Args:
            driver: WebDriver instance
            query: Search query string
            target_domain: Domain to search for and click
            max_pages: Maximum number of pages/batches to search
            scroll_steps_per_batch: Number of scroll steps per batch
            
        Returns:
            SearchStatus indicating the final result
        """
        if not self.prepare(driver):
            return SearchStatus.ERROR
            
        status = self.perform_query(driver, query)
        if status != SearchStatus.CLICKED:
            # If query failed, return the failure status
            if status in (SearchStatus.CHALLENGE, SearchStatus.ERROR):
                return status
        
        # Query succeeded, now look for target domain
        return self.find_and_click_target(driver, target_domain, max_pages, scroll_steps_per_batch)
"""
Search engine routing and fallback logic
"""
from .base import SearchEngine, SearchStatus
from .google import GoogleSearchEngine
from .bing import BingSearchEngine
from ..logging.logger import log


class SearchEngineRouter:
    """
    Handles search engine selection and fallback logic.
    """
    
    @staticmethod
    def get_engine(engine_name: str) -> SearchEngine:
        """
        Get a search engine instance by name.
        
        Args:
            engine_name: "google", "bing", or "auto"
            
        Returns:
            SearchEngine instance
            
        Raises:
            ValueError: If engine_name is not supported
        """
        engine_name = (engine_name or "auto").lower()
        
        if engine_name == "google":
            return GoogleSearchEngine()
        elif engine_name == "bing":
            return BingSearchEngine()
        elif engine_name == "auto":
            # Auto mode starts with Google
            return GoogleSearchEngine()
        else:
            raise ValueError(f"Unsupported search engine: {engine_name}")
    
    @staticmethod
    def search_with_fallback(
        driver,
        query: str,
        target_domain: str,
        engine_name: str = "auto",
        max_pages: int = 5,
        scroll_steps_per_batch: int = 10
    ) -> SearchStatus:
        """
        Execute search with automatic fallback from Google to Bing if needed.
        
        Args:
            driver: WebDriver instance
            query: Search query string
            target_domain: Domain to search for and click
            engine_name: "google", "bing", or "auto" 
            max_pages: Maximum pages to search
            scroll_steps_per_batch: Scroll steps per batch for Google
            
        Returns:
            SearchStatus indicating final result
        """
        engine_name = (engine_name or "auto").lower()
        
        if engine_name == "bing":
            # Use Bing directly
            engine = BingSearchEngine()
            return engine.search_and_click(driver, query, target_domain, max_pages=3)  # Bing uses fewer pages
        
        if engine_name == "google":
            # Use Google directly
            engine = GoogleSearchEngine()
            return engine.search_and_click(driver, query, target_domain, max_pages, scroll_steps_per_batch)
        
        # Auto mode: try Google first, fallback to Bing on challenge
        google_engine = GoogleSearchEngine()
        status = google_engine.search_and_click(driver, query, target_domain, max_pages, scroll_steps_per_batch)
        
        if status == SearchStatus.CLICKED:
            return status
            
        if status == SearchStatus.CHALLENGE:
            log("Falling back to Bing due to Google challenge.")
            bing_engine = BingSearchEngine()
            return bing_engine.search_and_click(driver, query, target_domain, max_pages=3)
        
        # Other statuses (NOT_FOUND, ERROR) - don't fallback
        return status


def search_and_click_domain(
    driver,
    query: str,
    target_domain: str,
    engine: str = "auto",
    max_pages: int = 5,
    scroll_steps_per_batch: int = 10
) -> bool:
    """
    Legacy function for backward compatibility.
    
    Args:
        driver: WebDriver instance
        query: Search query string
        target_domain: Domain to search for
        engine: Search engine ("auto", "google", "bing")
        max_pages: Maximum pages to search
        scroll_steps_per_batch: Scroll steps per batch
        
    Returns:
        True if target was found and clicked, False otherwise
    """
    status = SearchEngineRouter.search_with_fallback(
        driver, query, target_domain, engine_name=engine, max_pages=max_pages, scroll_steps_per_batch=scroll_steps_per_batch
    )
    return status == SearchStatus.CLICKED
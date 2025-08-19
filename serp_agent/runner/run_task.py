"""
Main task orchestration for SERP Agent
"""
import time
from typing import Optional
from ..config.settings import Settings
from ..browser.driver_factory import build_driver
from ..browser.history import wipe_browsing_history
from ..serp.router import SearchEngineRouter
from ..serp.base import SearchStatus
from ..logging.logger import log


def run_task(
    search_query: str,
    target_domain: str,
    settings: Optional[Settings] = None,
    proxy_url: Optional[str] = None,
    device: str = "desktop",
    headless: bool = False,
    engine: str = "auto",
    max_pages: int = 6,
    scroll_steps_per_batch: int = 10,
    user_data_dir: Optional[str] = "./chrome-profile",
    profile_directory: str = "Default",
) -> bool:
    """
    Execute a complete search and click task.
    
    Args:
        search_query: The search query to execute
        target_domain: Domain to search for and click
        settings: Settings object (if None, uses legacy parameters)
        proxy_url: Proxy URL (legacy parameter)
        device: "desktop" or "mobile" (legacy parameter)
        headless: Run in headless mode (legacy parameter)
        engine: Search engine to use (legacy parameter)
        max_pages: Maximum pages to search (legacy parameter)
        scroll_steps_per_batch: Scroll steps per batch (legacy parameter)
        user_data_dir: Chrome profile directory (legacy parameter)
        profile_directory: Profile subdirectory (legacy parameter)
        
    Returns:
        True if target domain was successfully clicked, False otherwise
    """
    # Use settings object if provided, otherwise use legacy parameters
    if settings:
        actual_proxy_url = settings.proxy.proxy_url if settings.proxy.enabled else None
        actual_device = settings.browser.device
        actual_headless = settings.browser.headless
        actual_engine = settings.search.engine
        actual_max_pages = settings.search.max_pages
        actual_scroll_steps = settings.search.scroll_steps_per_batch
        actual_user_data_dir = settings.browser.user_data_dir
        actual_profile_dir = settings.browser.profile_directory
        history_wipe_enabled = settings.paths.history_wipe_enabled
    else:
        # Legacy mode - use passed parameters
        actual_proxy_url = proxy_url
        actual_device = device
        actual_headless = headless
        actual_engine = engine
        actual_max_pages = max_pages
        actual_scroll_steps = scroll_steps_per_batch
        actual_user_data_dir = user_data_dir
        actual_profile_dir = profile_directory
        history_wipe_enabled = bool(actual_user_data_dir)

    # Build driver
    driver = build_driver(
        proxy_url=actual_proxy_url,
        device=actual_device,
        headless=actual_headless,
        user_data_dir=actual_user_data_dir,
        profile_directory=actual_profile_dir,
    )
    
    try:
        # Execute search
        status = SearchEngineRouter.search_with_fallback(
            driver,
            search_query,
            target_domain,
            engine_name=actual_engine,
            max_pages=actual_max_pages,
            scroll_steps_per_batch=actual_scroll_steps
        )
        
        # Log results
        if status == SearchStatus.CLICKED:
            log(f"✅ Clicked a result on {target_domain}")
            success = True
        elif status == SearchStatus.NOT_FOUND:
            log(f"❌ Could not find {target_domain} within {actual_max_pages} batches.")
            success = False
        elif status == SearchStatus.CHALLENGE:
            log(f"❌ Challenge detected, could not complete search for {target_domain}")
            success = False
        else:  # ERROR
            log(f"❌ Error occurred during search for {target_domain}")
            success = False
            
        time.sleep(2.0)  # Brief pause before cleanup
        return success
        
    finally:
        driver.quit()
        if history_wipe_enabled and actual_user_data_dir:
            wipe_browsing_history(actual_user_data_dir, actual_profile_dir)


def run_with_env_settings(
    search_query: str,
    target_domain: str
) -> bool:
    """
    Run task using settings loaded from environment variables.
    
    Args:
        search_query: The search query to execute
        target_domain: Domain to search for and click
        
    Returns:
        True if target domain was successfully clicked, False otherwise
    """
    settings = Settings.from_env()
    return run_task(search_query, target_domain, settings=settings)
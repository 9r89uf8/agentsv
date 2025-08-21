"""
SEO-enhanced task runner for SERP Agent
"""
import time
import random
from ..behaviors.simple_engagement import engage_with_page, add_human_delays
from ..strategies.simple_search import SimpleSearchStrategy
from .run_task import run_task as original_run_task
from ..serp.router import SearchEngineRouter
from ..serp.base import SearchStatus
from ..browser.driver_factory import build_driver
from ..browser.history import wipe_browsing_history
from ..logging.logger import log


def run_seo_task(
    brand_name: str,
    target_domain: str, 
    base_topic: str,
    num_searches: int = 10,
    settings=None
) -> dict:
    """
    Run multiple SEO-enhanced searches with simple human behaviors
    
    Args:
        brand_name: Your brand name for brand searches
        target_domain: Target domain to click on
        base_topic: Base topic for search queries
        num_searches: Number of searches to perform
        settings: Configuration settings
        
    Returns:
        Results summary
    """
    
    search_strategy = SimpleSearchStrategy(brand_name, target_domain)
    results = []
    
    for i in range(num_searches):
        log(f"Iniciando búsqueda {i+1}/{num_searches}")
        
        try:
            # Generate search query
            query = search_strategy.get_search_query(base_topic)
            
            # Add delay between searches
            if i > 0:
                delay = random.uniform(10, 60)  # 10-60 seconds between searches
                log(f"Esperando {delay:.1f} segundos antes de la siguiente búsqueda...")
                time.sleep(delay)
            
            # Perform search
            success = _perform_enhanced_search(query, target_domain, settings)
            
            results.append({
                'search_num': i + 1,
                'query': query,
                'success': success
            })
            
        except Exception as e:
            log(f"Búsqueda {i+1} falló: {e}", "error")
            results.append({
                'search_num': i + 1,
                'query': query if 'query' in locals() else 'N/A',
                'success': False,
                'error': str(e)
            })
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    log(f"Completadas {num_searches} búsquedas: {successful} exitosas, {num_searches - successful} fallidas")
    
    return {
        'total_searches': num_searches,
        'successful': successful,
        'success_rate': successful / num_searches if num_searches > 0 else 0,
        'results': results
    }


def _perform_enhanced_search(query: str, target_domain: str, settings=None) -> bool:
    """Perform single search with engagement"""
    
    # Use settings or defaults
    if settings:
        device = settings.browser.device
        headless = settings.browser.headless
        proxy_url = settings.proxy.proxy_url if settings.proxy.enabled else None
        user_data_dir = settings.browser.user_data_dir
        profile_dir = settings.browser.profile_directory
        max_pages = settings.search.max_pages
        scroll_steps = settings.search.scroll_steps_per_batch
        engine = settings.search.engine
        
        # SEO settings if available
        if settings.seo:
            min_dwell_time = settings.seo.min_dwell_time
            max_dwell_time = settings.seo.max_dwell_time
        else:
            min_dwell_time = 120
            max_dwell_time = 180
    else:
        device = "desktop"
        headless = False
        proxy_url = None
        user_data_dir = "./chrome-profile"
        profile_dir = "Default"
        max_pages = 6
        scroll_steps = 10
        engine = "auto"
        min_dwell_time = 120
        max_dwell_time = 180
    
    # Build driver
    driver = build_driver(
        proxy_url=proxy_url,
        device=device,
        headless=headless,
        user_data_dir=user_data_dir,
        profile_directory=profile_dir
    )
    
    try:
        # Add human delay before starting
        add_human_delays()
        
        # Perform search
        status = SearchEngineRouter.search_with_fallback(
            driver=driver,
            query=query,
            target_domain=target_domain,
            engine_name=engine,
            max_pages=max_pages,
            scroll_steps_per_batch=scroll_steps
        )
        
        if status == SearchStatus.CLICKED:
            log(f"Clic exitoso en {target_domain}")
            
            # ENHANCED: Engage with the page
            engage_with_page(driver, min_time=min_dwell_time, max_time=max_dwell_time)
            
            return True
        else:
            log(f"No se pudo encontrar/hacer clic en {target_domain}: {status}")
            return False
            
    finally:
        driver.quit()
        if user_data_dir:
            wipe_browsing_history(user_data_dir, profile_dir)
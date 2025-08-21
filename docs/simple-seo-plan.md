# Simple SEO Enhancement Plan

## 🎯 Overview

A practical, easy-to-implement enhancement that adds basic human-like behaviors to improve SEO signals without overwhelming complexity.

## 🔧 Core Features (4 Simple Additions)

### 1. **Dwell Time (2-3 Minutes)**
Stay on the target page for 2-3 minutes after clicking, scrolling naturally to simulate reading.

### 2. **Brand Search Mixing**
- 30% brand searches: "Your Brand Name", "Your Brand website"
- 70% discovery searches: "best product type", "product reviews"

### 3. **Simple Human Behaviors**
- Random delays between actions (0.5-2 seconds)
- Natural scrolling patterns
- Occasional pause as if reading something interesting

### 4. **Basic Engagement**
- Click 1-2 internal links if found
- Scroll to bottom of page
- Sometimes scroll back up

## 🚀 Implementation

### New Module: Simple Engagement

```python
# serp_agent/behaviors/simple_engagement.py
import time
import random
from selenium.webdriver.common.by import By
from ..logging.logger import log

def engage_with_page(driver, min_time=120, max_time=180):
    """
    Simple engagement: stay on page 2-3 minutes with basic behaviors
    
    Args:
        driver: WebDriver instance
        min_time: Minimum time in seconds (default 120 = 2 minutes)
        max_time: Maximum time in seconds (default 180 = 3 minutes)
    """
    total_time = random.randint(min_time, max_time)
    start_time = time.time()
    
    log(f"Starting page engagement for {total_time} seconds")
    
    # Get page height for scrolling
    page_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # Calculate scroll steps
    scroll_steps = max(3, int(page_height / viewport_height))
    time_per_step = total_time / (scroll_steps + 2)  # +2 for initial pause and final actions
    
    # Initial pause (user reading top of page)
    time.sleep(random.uniform(5, 15))
    
    # Scroll through page gradually
    for step in range(scroll_steps):
        scroll_amount = int(page_height / scroll_steps)
        driver.execute_script(f"window.scrollTo(0, {scroll_amount * step});")
        
        # Pause as if reading this section
        pause_time = time_per_step * random.uniform(0.7, 1.3)
        
        # Sometimes pause longer (found something interesting)
        if random.random() < 0.2:  # 20% chance
            pause_time *= random.uniform(1.5, 2.5)
            log("Extended pause - interesting content")
        
        time.sleep(pause_time)
    
    # Try to click 1-2 internal links
    _click_internal_links(driver)
    
    # Scroll back up sometimes
    if random.random() < 0.3:  # 30% chance
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
        time.sleep(random.uniform(3, 8))
    
    # Fill remaining time if needed
    remaining_time = total_time - (time.time() - start_time)
    if remaining_time > 0:
        time.sleep(remaining_time)
    
    log(f"Page engagement completed after {time.time() - start_time:.1f} seconds")

def _click_internal_links(driver):
    """Click 1-2 internal links if available"""
    try:
        # Find internal links (basic approach)
        current_domain = driver.current_url.split('/')[2]
        internal_links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{current_domain}') or starts-with(@href, '/')]")
        
        # Filter out navigation links
        content_links = []
        for link in internal_links:
            link_text = link.text.lower()
            if len(link_text) > 5 and any(word in link_text for word in ['read', 'more', 'article', 'guide', 'see']):
                content_links.append(link)
        
        if content_links:
            # Click 1-2 links
            num_clicks = random.choice([1, 2]) if len(content_links) > 1 else 1
            
            for _ in range(min(num_clicks, len(content_links))):
                link = random.choice(content_links)
                content_links.remove(link)
                
                try:
                    if link.is_displayed() and link.is_enabled():
                        log(f"Clicking internal link: {link.text[:30]}")
                        link.click()
                        
                        # Stay on new page briefly
                        time.sleep(random.uniform(10, 30))
                        
                        # Go back
                        driver.back()
                        time.sleep(random.uniform(2, 5))
                        
                except Exception as e:
                    log(f"Failed to click internal link: {e}")
                    continue
    
    except Exception as e:
        log(f"Internal link clicking failed: {e}")

def add_human_delays():
    """Add small random delays to seem human"""
    time.sleep(random.uniform(0.5, 2.0))
```

### Simple Search Strategy

```python
# serp_agent/strategies/simple_search.py
import random
import os
from ..logging.logger import log

class SimpleSearchStrategy:
    def __init__(self, brand_name: str, target_domain: str):
        self.brand_name = brand_name
        self.target_domain = target_domain
        self.search_count = 0
    
    def get_search_query(self, base_topic: str) -> str:
        """
        Generate search query: 30% brand, 70% discovery
        """
        self.search_count += 1
        
        # 30% brand searches
        if random.random() < 0.3:
            brand_queries = [
                self.brand_name,
                f"{self.brand_name} website",
                f"{self.brand_name} official",
                f"www {self.brand_name}",
                f"{self.brand_name} {base_topic}"
            ]
            query = random.choice(brand_queries)
            log(f"Brand search #{self.search_count}: {query}")
            
        else:
            # 70% discovery searches
            discovery_queries = [
                f"best {base_topic}",
                f"{base_topic} reviews",
                f"top {base_topic} 2024",
                f"how to choose {base_topic}",
                f"{base_topic} comparison",
                f"where to buy {base_topic}",
                f"{base_topic} guide"
            ]
            query = random.choice(discovery_queries)
            log(f"Discovery search #{self.search_count}: {query}")
        
        return query
```

### Enhanced Runner

```python
# serp_agent/runner/seo_enhanced_task.py
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
        log(f"Starting search {i+1}/{num_searches}")
        
        try:
            # Generate search query
            query = search_strategy.get_search_query(base_topic)
            
            # Add delay between searches
            if i > 0:
                delay = random.uniform(10, 60)  # 10-60 seconds between searches
                log(f"Waiting {delay:.1f} seconds before next search...")
                time.sleep(delay)
            
            # Perform search
            success = _perform_enhanced_search(query, target_domain, settings)
            
            results.append({
                'search_num': i + 1,
                'query': query,
                'success': success
            })
            
        except Exception as e:
            log(f"Search {i+1} failed: {e}", "error")
            results.append({
                'search_num': i + 1,
                'query': query,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    log(f"Completed {num_searches} searches: {successful} successful, {num_searches - successful} failed")
    
    return {
        'total_searches': num_searches,
        'successful': successful,
        'success_rate': successful / num_searches,
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
    else:
        device = "desktop"
        headless = False
        proxy_url = None
        user_data_dir = "./chrome-profile"
        profile_dir = "Default"
    
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
            engine_name="auto"
        )
        
        if status == SearchStatus.CLICKED:
            log(f"Successfully clicked on {target_domain}")
            
            # ENHANCED: Engage with the page
            engage_with_page(driver, min_time=120, max_time=180)  # 2-3 minutes
            
            return True
        else:
            log(f"Failed to find/click {target_domain}: {status}")
            return False
            
    finally:
        driver.quit()
        if user_data_dir:
            wipe_browsing_history(user_data_dir, profile_dir)
```

### Configuration

```python
# Add to serp_agent/config/settings.py
@dataclass  
class SEOConfig:
    """Simple SEO enhancement settings"""
    brand_name: str = "Your Brand"
    base_topic: str = "your product"
    min_dwell_time: int = 120  # 2 minutes
    max_dwell_time: int = 180  # 3 minutes
    brand_search_ratio: float = 0.3  # 30% brand searches
    searches_per_session: int = 10
```

### Simple Usage

```python
# main_seo.py - Simple usage example
from serp_agent.runner.seo_enhanced_task import run_seo_task
from serp_agent.config.settings import Settings

def main():
    """Simple SEO-enhanced main function"""
    settings = Settings.from_env()
    
    results = run_seo_task(
        brand_name="Your Brand Name",
        target_domain="yoursite.com", 
        base_topic="your main product/service",
        num_searches=20,
        settings=settings
    )
    
    print(f"Success rate: {results['success_rate']:.1%}")

if __name__ == "__main__":
    main()
```

## 📋 Environment Variables

Add these to your `.env` file:

```bash
# SEO Enhancement
BRAND_NAME=Your Brand Name
BASE_TOPIC=your product category
MIN_DWELL_TIME=120
MAX_DWELL_TIME=180
SEARCHES_PER_SESSION=20
```

## 🚀 Benefits

### What This Simple Enhancement Provides:

1. **Quality Dwell Time**: 2-3 minutes per visit (vs typical 5-10 seconds)
2. **Brand Recognition**: Mix of direct brand searches
3. **Natural Behavior**: Random delays and scrolling patterns  
4. **Internal Engagement**: Clicks 1-2 internal links per visit
5. **Easy Implementation**: Minimal changes to existing code

### Expected Results:

- **Better Engagement Metrics**: Higher time on site, lower bounce rate
- **Mixed Traffic Patterns**: Both brand and discovery traffic
- **Reduced Detection Risk**: More human-like behavior patterns
- **Simple Maintenance**: Easy to understand and modify

## ⚙️ Implementation Steps

1. **Add the 3 new modules** (simple_engagement.py, simple_search.py, seo_enhanced_task.py)
2. **Update your .env file** with brand and topic settings
3. **Test with a few searches** to verify behavior
4. **Scale up gradually** to avoid detection

This simple approach gives you 80% of the SEO benefits with 20% of the complexity!
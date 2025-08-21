# SERP Agent Developer Guide

## Overview

This guide explains how to extend, modify, and contribute to the SERP Agent codebase. It covers common development scenarios and best practices.

## Table of Contents

- [Development Setup](#development-setup)
- [Adding New Search Engines](#adding-new-search-engines)
- [Creating Custom Scanning Strategies](#creating-custom-scanning-strategies)
- [Adding New Device Profiles](#adding-new-device-profiles)
- [Testing](#testing)
- [Configuration Management](#configuration-management)
- [Debugging and Troubleshooting](#debugging-and-troubleshooting)
- [Best Practices](#best-practices)
- [Contributing Guidelines](#contributing-guidelines)

## Development Setup

### Prerequisites
- Python 3.8+
- Chrome browser installed
- Virtual environment recommended

### Installation
```bash
git clone <repository>
cd superv2simple
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file with your settings:
```bash
# Search settings
SEARCH_QUERY=test query
TARGET_DOMAIN=example.com
ENGINE=auto
MAX_PAGES=5

# Browser settings  
DEVICE=desktop
HEADLESS=false
USER_DATA_DIR=./chrome-profile

# Proxy settings (optional)
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
PROXY_HOST=proxy.example.com
PROXY_PORT=8080
```

### Running Tests
```bash
python test_refactor.py  # Basic functionality tests
python main.py          # Full integration test
```

## Adding New Search Engines

### Step 1: Create Search Engine Class

Create a new file in `serp_agent/serp/` (e.g., `duckduckgo.py`):

```python
"""
DuckDuckGo search engine implementation
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
from ..logging.logger import log


class DuckDuckGoSearchEngine(SearchEngine):
    """DuckDuckGo search engine implementation"""
    
    def prepare(self, driver) -> bool:
        """Navigate to DuckDuckGo and accept any consent"""
        try:
            driver.get("https://duckduckgo.com")
            accept_cookies_if_present(driver)
            return True
        except Exception as e:
            log(f"Failed to prepare DuckDuckGo search: {e}")
            return False
    
    def perform_query(self, driver, query: str) -> SearchStatus:
        """Execute search query on DuckDuckGo"""
        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.ENTER)
            
            # Wait for results
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "links"))
            )
            return SearchStatus.CLICKED  # Ready to search results
            
        except Exception as e:
            log(f"Failed to perform DuckDuckGo query: {e}")
            return SearchStatus.ERROR
    
    def find_and_click_target(
        self, 
        driver, 
        target_domain: str, 
        max_pages: int = 3,
        scroll_steps_per_batch: int = 10
    ) -> SearchStatus:
        """Search through DuckDuckGo results for target domain"""
        try:
            for page_idx in range(1, max_pages + 1):
                # Find all result links
                results = driver.find_elements(
                    By.CSS_SELECTOR, 
                    "#links .result__a"
                )
                
                for result in results:
                    href = result.get_attribute("href")
                    if href and url_matches_domain(href, target_domain):
                        log(f"Found target in DuckDuckGo results: {href}")
                        click_safely(driver, result)
                        return SearchStatus.CLICKED
                
                # Try to go to next page
                try:
                    next_link = driver.find_element(
                        By.CSS_SELECTOR, 
                        ".sb_pagN, a[aria-label='Next']"
                    )
                    click_safely(driver, next_link)
                    time.sleep(2)
                except:
                    break  # No more pages
                    
            return SearchStatus.NOT_FOUND
            
        except Exception as e:
            log(f"Error during DuckDuckGo search: {e}")
            return SearchStatus.ERROR
```

### Step 2: Register in Router

Update `serp_agent/serp/router.py`:

```python
# Add import
from .duckduckgo import DuckDuckGoSearchEngine

class SearchEngineRouter:
    @staticmethod
    def get_engine(engine_name: str) -> SearchEngine:
        engine_name = (engine_name or "auto").lower()
        
        if engine_name == "google":
            return GoogleSearchEngine()
        elif engine_name == "bing":
            return BingSearchEngine()
        elif engine_name == "duckduckgo":  # Add this
            return DuckDuckGoSearchEngine()
        elif engine_name == "auto":
            return GoogleSearchEngine()
        else:
            raise ValueError(f"Unsupported search engine: {engine_name}")
```

### Step 3: Add to Constants

Update `serp_agent/config/constants.py`:

```python
# Add DuckDuckGo URL
DUCKDUCKGO_URL = "https://duckduckgo.com"
```

### Step 4: Test Your Engine

```python
from serp_agent.browser.driver_factory import build_driver
from serp_agent.serp.duckduckgo import DuckDuckGoSearchEngine

driver = build_driver()
try:
    engine = DuckDuckGoSearchEngine()
    status = engine.search_and_click(
        driver, 
        "python programming", 
        "python.org"
    )
    print(f"Search result: {status}")
finally:
    driver.quit()
```

## Creating Custom Scanning Strategies

### Basic Strategy Function

Create new strategies in `serp_agent/serp/scan_strategies.py`:

```python
def horizontal_scan_strategy(
    driver,
    target_domain: str,
    seen_hrefs: Optional[Set[str]] = None,
    scan_rows: int = 5
) -> bool:
    """
    Scans results horizontally (left-to-right, top-to-bottom)
    instead of scrolling vertically.
    """
    if seen_hrefs is None:
        seen_hrefs = set()
    
    try:
        # Get all visible result links
        anchors = driver.find_elements(
            By.XPATH, 
            "//div[@id='search']//a[@href] | //div[@id='rso']//a[@href]"
        )
        
        for i, anchor in enumerate(anchors[:scan_rows * 3]):  # Limit scan
            href = anchor.get_attribute("href")
            if not href or href in seen_hrefs:
                continue
                
            seen_hrefs.add(href)
            final_url = extract_final_url(href)
            
            if url_matches_domain(final_url, target_domain):
                log(f"Found target with horizontal scan: {final_url}")
                click_safely(driver, anchor)
                return True
                
        return False
        
    except Exception as e:
        log(f"Horizontal scan failed: {e}")
        return False
```

### Using Custom Strategy in Search Engine

Modify your search engine's `find_and_click_target` method:

```python
def find_and_click_target(self, driver, target_domain: str, **kwargs) -> SearchStatus:
    """Use custom scanning strategy"""
    
    # Try custom strategy first
    if horizontal_scan_strategy(driver, target_domain):
        return SearchStatus.CLICKED
    
    # Fall back to default strategy
    if progressive_scroll_and_scan(driver, target_domain):
        return SearchStatus.CLICKED
        
    return SearchStatus.NOT_FOUND
```

## Adding New Device Profiles

### Step 1: Define Device Metrics

Update `serp_agent/config/constants.py`:

```python
# Add new device profile
IPHONE_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
)

IPHONE_WINDOW_SIZE = {"width": 375, "height": 667}

IPHONE_DEVICE_METRICS = {
    "width": 375,
    "height": 667,
    "deviceScaleFactor": 2.0,
    "mobile": True
}
```

### Step 2: Update Configuration

Update `serp_agent/config/settings.py`:

```python
@dataclass
class BrowserConfig:
    device: str = "desktop"  # "desktop", "mobile", "iphone"
    # ... other fields
    
    @property
    def user_agent(self) -> str:
        if self.device == "mobile":
            return MOBILE_USER_AGENT
        elif self.device == "iphone":
            return IPHONE_USER_AGENT
        else:
            return DESKTOP_USER_AGENT
    
    @property
    def window_size(self) -> dict:
        if self.device == "mobile":
            return MOBILE_WINDOW_SIZE
        elif self.device == "iphone":
            return IPHONE_WINDOW_SIZE
        else:
            return DESKTOP_WINDOW_SIZE
```

### Step 3: Update Driver Factory

Update `serp_agent/browser/driver_factory.py`:

```python
def build_driver(proxy_url=None, device="desktop", **kwargs):
    # ... existing code ...
    
    # Configure device-specific settings
    if device == "mobile":
        options.add_argument(f"--user-agent={MOBILE_USER_AGENT}")
        options.add_argument(f"--window-size={MOBILE_WINDOW_SIZE['width']},{MOBILE_WINDOW_SIZE['height']}")
    elif device == "iphone":  # Add this block
        options.add_argument(f"--user-agent={IPHONE_USER_AGENT}")
        options.add_argument(f"--window-size={IPHONE_WINDOW_SIZE['width']},{IPHONE_WINDOW_SIZE['height']}")
    else:
        options.add_argument(f"--user-agent={DESKTOP_USER_AGENT}")
        options.add_argument(f"--window-size={DESKTOP_WINDOW_SIZE['width']},{DESKTOP_WINDOW_SIZE['height']}")
    
    # ... device emulation setup ...
    
    if device == "iphone":  # Add iPhone emulation
        try:
            driver.set_window_rect(
                width=IPHONE_WINDOW_SIZE['width'],
                height=IPHONE_WINDOW_SIZE['height'],
                x=0, y=0
            )
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", IPHONE_DEVICE_METRICS)
            driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {"enabled": True})
            driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
                "userAgent": IPHONE_USER_AGENT,
                "platform": "iPhone",
                "acceptLanguage": "en-US,en"
            })
            log("iPhone emulation enabled.")
        except Exception as e:
            log(f"Warning: failed to enable iPhone emulation: {e}")
```

## Testing

### Unit Testing Framework

Create `tests/test_url_utils.py`:

```python
import pytest
from serp_agent.net.url_utils import extract_final_url, url_matches_domain


class TestUrlUtils:
    def test_extract_final_url_google_redirect(self):
        """Test Google redirect URL extraction"""
        redirect = "https://www.google.com/url?q=https://example.com/page&sa=U"
        result = extract_final_url(redirect)
        assert result == "https://example.com/page"
    
    def test_extract_final_url_regular(self):
        """Test regular URL passthrough"""
        url = "https://example.com/page"
        result = extract_final_url(url)
        assert result == url
    
    def test_url_matches_domain_basic(self):
        """Test basic domain matching"""
        assert url_matches_domain("https://example.com/page", "example.com")
        assert not url_matches_domain("https://other.com/page", "example.com")
    
    def test_url_matches_domain_subdomain(self):
        """Test subdomain matching"""
        assert url_matches_domain("https://www.example.com/page", "example.com")
        assert url_matches_domain("https://blog.example.com/post", "example.com")


if __name__ == "__main__":
    pytest.main([__file__])
```

### Integration Testing

Create `tests/test_search_engines.py`:

```python
import pytest
from unittest.mock import Mock, patch
from serp_agent.serp.google import GoogleSearchEngine
from serp_agent.serp.base import SearchStatus


class TestGoogleSearchEngine:
    def test_prepare_success(self):
        """Test successful Google preparation"""
        mock_driver = Mock()
        engine = GoogleSearchEngine()
        
        result = engine.prepare(mock_driver)
        
        assert result == True
        mock_driver.get.assert_called_once_with("https://www.google.com/ncr")
    
    @patch('serp_agent.serp.google.is_google_challenge')
    def test_perform_query_challenge_detected(self, mock_challenge):
        """Test challenge detection during query"""
        mock_driver = Mock()
        mock_challenge.return_value = True
        engine = GoogleSearchEngine()
        
        # Mock search box
        mock_box = Mock()
        mock_driver.find_element.return_value = mock_box
        
        result = engine.perform_query(mock_driver, "test query")
        
        assert result == SearchStatus.CHALLENGE
```

### Testing with Real Browser

Create `tests/test_integration.py`:

```python
import pytest
from serp_agent.browser.driver_factory import build_driver
from serp_agent.runner.run_task import run_task


@pytest.mark.slow
def test_integration_headless():
    """Integration test with headless browser"""
    success = run_task(
        search_query="python",
        target_domain="python.org",
        device="desktop",
        headless=True,
        max_pages=1  # Limit for testing
    )
    # Note: This may fail if python.org isn't in first page
    # Use for testing workflow, not assertions
```

## Configuration Management

### Adding New Configuration Options

1. **Add to Settings dataclass:**
```python
# In serp_agent/config/settings.py
@dataclass
class SearchConfig:
    engine: str = "auto"
    max_pages: int = 6
    scroll_steps_per_batch: int = 10
    timeout_multiplier: float = 1.0  # New option
```

2. **Add environment variable support:**
```python
def from_env(cls) -> "Settings":
    # ... existing code ...
    
    timeout_multiplier = float(os.getenv("TIMEOUT_MULTIPLIER", "1.0"))
    
    search_config = SearchConfig(
        engine=engine,
        max_pages=max_pages,
        scroll_steps_per_batch=scroll_steps,
        timeout_multiplier=timeout_multiplier
    )
```

3. **Use in implementation:**
```python
# In search engine code
timeout = DEFAULT_SERP_TIMEOUT * settings.search.timeout_multiplier
WebDriverWait(driver, timeout).until(...)
```

### Configuration Validation

Add validation to Settings:

```python
@dataclass
class Settings:
    browser: BrowserConfig
    proxy: ProxyConfig
    search: SearchConfig
    paths: PathsConfig
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.browser.device not in ["desktop", "mobile", "iphone"]:
            raise ConfigError(f"Invalid device: {self.browser.device}")
        
        if self.search.max_pages < 1:
            raise ConfigError("max_pages must be at least 1")
        
        if self.proxy.enabled and not self.proxy.proxy_url:
            raise ConfigError("Proxy enabled but no proxy_url provided")
```

## Debugging and Troubleshooting

### Debug Logging

Enable debug logging:

```python
from serp_agent.logging.logger import log

# Throughout your code
log("Starting search process", "debug")
log("Found element with selector: xyz", "debug")
```

### Page Snapshots

Capture page state for debugging:

```python
from serp_agent.browser.diagnostics import dump_serp_snapshot

# After any significant action
driver.get("https://google.com")
dump_serp_snapshot(driver, "after_navigation")

# After search
search_box.send_keys("query")
dump_serp_snapshot(driver, "after_query")
```

### Browser Developer Tools

Run in non-headless mode for visual debugging:

```python
driver = build_driver(headless=False)
input("Press Enter after manually inspecting browser...")
```

### Common Issues and Solutions

#### 1. Element Not Found
```python
try:
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "selector"))
    )
except TimeoutException:
    # Debug: capture page state
    dump_serp_snapshot(driver, "element_not_found")
    log(f"Current URL: {driver.current_url}")
    log(f"Page title: {driver.title}")
    raise
```

#### 2. Challenge Detection
```python
if is_google_challenge(driver):
    dump_serp_snapshot(driver, "google_challenge")
    log("Challenge page HTML captured for analysis")
```

#### 3. Proxy Connection Issues
```python
try:
    proxy_url = build_proxy_url_from_env()
    if proxy_url:
        log(f"Testing proxy connection to {proxy_url}")
        # Test proxy before creating driver
except Exception as e:
    log(f"Proxy setup failed: {e}", "error")
```

## Best Practices

### Code Organization

1. **Single Responsibility**: Each function should do one thing well
2. **Dependency Injection**: Pass dependencies as parameters, don't import globally
3. **Error Handling**: Use specific exceptions, not generic Exception catches
4. **Logging**: Use centralized logger, include context in messages

### Performance

1. **Lazy Loading**: Only load what you need when you need it
2. **Connection Reuse**: Use persistent Chrome profiles
3. **Timeouts**: Set appropriate timeouts for different operations
4. **Resource Cleanup**: Always close drivers in finally blocks

### Security

1. **Credential Handling**: Never log full credentials
2. **Input Validation**: Validate all external inputs
3. **Proxy Security**: Use HTTPS proxies when possible
4. **History Cleanup**: Remove browsing traces

### Testing

1. **Unit Tests**: Test pure functions without browser dependencies
2. **Integration Tests**: Test with real browser but limit scope
3. **Mocking**: Use protocols to mock browser interactions
4. **Test Data**: Use predictable test queries and domains

## Contributing Guidelines

### Code Style

1. **Type Hints**: Use type hints for all function parameters and returns
2. **Docstrings**: Document all public functions with examples
3. **Naming**: Use descriptive names, avoid abbreviations
4. **Constants**: Put magic numbers and strings in constants.py

### Pull Request Process

1. **Tests**: Add tests for new functionality
2. **Documentation**: Update relevant documentation
3. **Backwards Compatibility**: Don't break existing APIs
4. **Performance**: Consider impact on execution time

### Example Pull Request Checklist

- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Error handling implemented
- [ ] Logging added for debugging
- [ ] Constants extracted from magic values
- [ ] Integration test passes
- [ ] No breaking changes to public API

This developer guide should help you extend and contribute to the SERP Agent codebase effectively. The modular architecture makes it easy to add new components while maintaining system stability.
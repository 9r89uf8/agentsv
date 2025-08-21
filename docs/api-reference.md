# SERP Agent API Reference

## Overview

This document provides detailed API documentation for all public functions and classes in the SERP Agent package.

## Table of Contents

- [Configuration API](#configuration-api)
- [Browser API](#browser-api)
- [Search Engine API](#search-engine-api)
- [Network Utilities API](#network-utilities-api)
- [Proxy API](#proxy-api)
- [Runner API](#runner-api)
- [Logging API](#logging-api)
- [Types & Protocols](#types--protocols)

## Configuration API

### `serp_agent.config.settings`

#### `Settings`
Main configuration container that holds all settings for SERP Agent.

```python
@dataclass
class Settings:
    browser: BrowserConfig
    proxy: ProxyConfig
    search: SearchConfig
    paths: PathsConfig
```

**Methods:**

##### `Settings.from_env() -> Settings`
Creates a Settings instance from environment variables.

```python
from serp_agent.config.settings import Settings

settings = Settings.from_env()
print(f"Device: {settings.browser.device}")
print(f"Engine: {settings.search.engine}")
```

**Environment Variables Read:**
- `DEVICE` → `BrowserConfig.device`
- `HEADLESS` → `BrowserConfig.headless`
- `USER_DATA_DIR` → `BrowserConfig.user_data_dir`
- `PROFILE_DIRECTORY` → `BrowserConfig.profile_directory`
- `ENGINE` → `SearchConfig.engine`
- `MAX_PAGES` → `SearchConfig.max_pages`
- `SCROLLS_PER_BATCH` → `SearchConfig.scroll_steps_per_batch`
- `PROXY_*` → `ProxyConfig` (via proxy builder)

#### `BrowserConfig`
Browser-specific configuration settings.

```python
@dataclass
class BrowserConfig:
    device: str = "desktop"  # "desktop" or "mobile"
    headless: bool = False
    user_data_dir: Optional[str] = "./chrome-profile"
    profile_directory: str = "Default"
    language: str = "en-US,en"
```

**Properties:**
- `user_agent: str` - Returns appropriate UA based on device
- `window_size: dict` - Returns window dimensions for device

#### `SearchConfig`
Search engine configuration settings.

```python
@dataclass
class SearchConfig:
    engine: str = "auto"  # "auto", "google", "bing"
    max_pages: int = 6
    scroll_steps_per_batch: int = 10
    serp_timeout: int = 12
    element_wait: int = 10
    challenge_wait: int = 8
```

#### `ProxyConfig`
Proxy configuration settings.

```python
@dataclass
class ProxyConfig:
    enabled: bool = False
    proxy_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    host: str = "gate.decodo.com"
    port: str = "10001"
```

## Browser API

### `serp_agent.browser.driver_factory`

#### `build_driver(proxy_url=None, device="desktop", headless=False, user_data_dir="./chrome-profile", profile_directory="Default") -> uc.Chrome`

Creates and configures a Chrome WebDriver instance.

**Parameters:**
- `proxy_url` (str, optional): Proxy URL for extension-based proxy
- `device` (str): "desktop" or "mobile" for device emulation
- `headless` (bool): Whether to run in headless mode
- `user_data_dir` (str, optional): Chrome profile directory path
- `profile_directory` (str): Profile subdirectory name

**Returns:** Configured WebDriver instance

**Example:**
```python
from serp_agent.browser.driver_factory import build_driver

# Desktop browser with proxy
driver = build_driver(
    proxy_url="http://user:pass@proxy.com:8080",
    device="desktop",
    headless=False
)

# Mobile emulation
mobile_driver = build_driver(device="mobile")
```

### `serp_agent.browser.actions`

#### `click_safely(driver, element)`
Safely click an element with fallback strategies.

**Parameters:**
- `driver`: WebDriver instance
- `element`: WebElement to click

**Behavior:**
1. Scrolls element into view
2. Attempts normal click
3. Falls back to JavaScript click on interception

#### `robust_tap(driver, element) -> bool`
Advanced mobile tap with multiple fallback strategies.

**Parameters:**
- `driver`: WebDriver instance  
- `element`: WebElement to tap

**Returns:** True if tap successful, False otherwise

**Strategies:**
1. Normal element click
2. JavaScript click
3. Synthetic pointer events
4. CDP touch injection

#### `find_more_results_control(driver, timeout=4.0) -> WebElement`
Finds mobile "More results" button using multiple selectors.

**Parameters:**
- `driver`: WebDriver instance
- `timeout` (float): Search timeout in seconds

**Returns:** WebElement if found, None otherwise

### `serp_agent.browser.consent`

#### `accept_cookies_if_present(driver)`
Handles cookie consent popups automatically.

**Parameters:**
- `driver`: WebDriver instance

**Behavior:**
- Searches for common consent button patterns
- Handles both top-level and iframe-based consent
- Uses configurable selectors from constants

### `serp_agent.browser.diagnostics`

#### `dump_serp_snapshot(driver, tag="serp") -> Path`
Captures diagnostic page snapshot for debugging.

**Parameters:**
- `driver`: WebDriver instance
- `tag` (str): Prefix for filename

**Returns:** Path to saved HTML file

**Output:**
- Logs viewport and user agent info
- Saves complete page HTML with timestamp
- Returns Path object to saved file

### `serp_agent.browser.history`

#### `wipe_browsing_history(user_data_dir, profile_dir="Default")`
Removes Chrome history while preserving cookies.

**Parameters:**
- `user_data_dir` (str): Chrome profile directory
- `profile_dir` (str): Profile subdirectory

**Files Removed:**
- History databases and journals
- Visited links
- Top sites
- Navigation predictions

## Search Engine API

### `serp_agent.serp.base`

#### `SearchStatus` (Enum)
Status codes for search operations.

```python
class SearchStatus(Enum):
    CLICKED = "clicked"           # Successfully clicked target
    NOT_FOUND = "not_found"       # Target not found in results  
    CHALLENGE = "challenge"       # Captcha/challenge detected
    ERROR = "error"               # Other error occurred
```

#### `SearchEngine` (Abstract Base Class)
Interface that all search engines must implement.

**Abstract Methods:**

##### `prepare(driver) -> bool`
Prepare the search engine (navigate to homepage, accept cookies).

##### `perform_query(driver, query: str) -> SearchStatus`  
Execute search query and wait for results.

##### `find_and_click_target(driver, target_domain: str, max_pages=5, scroll_steps_per_batch=10) -> SearchStatus`
Search through results for target domain and click it.

**Implemented Methods:**

##### `search_and_click(driver, query, target_domain, max_pages=5, scroll_steps_per_batch=10) -> SearchStatus`
Complete workflow: prepare → query → find and click.

### `serp_agent.serp.google`

#### `GoogleSearchEngine`
Google search implementation.

```python
engine = GoogleSearchEngine()
status = engine.search_and_click(
    driver=driver,
    query="python tutorials", 
    target_domain="realpython.com"
)
```

#### `ensure_serp_loaded(driver, timeout=12)`
Waits for Google SERP to load completely.

**Parameters:**
- `driver`: WebDriver instance
- `timeout` (int): Wait timeout in seconds

### `serp_agent.serp.bing`

#### `BingSearchEngine`
Bing search implementation with simpler pagination.

```python
engine = BingSearchEngine()
status = engine.search_and_click(
    driver=driver,
    query="machine learning courses",
    target_domain="coursera.org"
)
```

### `serp_agent.serp.router`

#### `SearchEngineRouter`
Handles search engine selection and fallback logic.

##### `get_engine(engine_name: str) -> SearchEngine`
Returns search engine instance by name.

**Parameters:**
- `engine_name` (str): "google", "bing", or "auto"

**Returns:** SearchEngine instance

##### `search_with_fallback(driver, query, target_domain, engine_name="auto", max_pages=5, scroll_steps_per_batch=10) -> SearchStatus`
Execute search with automatic Google → Bing fallback.

**Parameters:**
- `driver`: WebDriver instance
- `query` (str): Search query
- `target_domain` (str): Domain to find and click
- `engine_name` (str): "google", "bing", or "auto"
- `max_pages` (int): Maximum pages to search
- `scroll_steps_per_batch` (int): Scroll steps per page

**Returns:** SearchStatus enum value

**Example:**
```python
from serp_agent.serp.router import SearchEngineRouter

status = SearchEngineRouter.search_with_fallback(
    driver=driver,
    query="web development tutorials",
    target_domain="mdn.org",
    engine_name="auto",  # Try Google, fallback to Bing on challenge
    max_pages=3
)
```

### `serp_agent.serp.scan_strategies`

#### `progressive_scroll_and_scan(driver, target_domain, seen_hrefs=None, max_steps=10, step_px=700) -> bool`
Scrolls page progressively while scanning for target domain.

**Parameters:**
- `driver`: WebDriver instance
- `target_domain` (str): Domain to search for
- `seen_hrefs` (Set[str], optional): URLs already processed
- `max_steps` (int): Maximum scroll steps
- `step_px` (int): Pixels to scroll per step

**Returns:** True if target found and clicked

**Behavior:**
- Scrolls page in configurable steps
- Scans for links after each scroll
- Uses staggered delays to appear human-like
- Handles Google URL redirects automatically

#### `attempt_load_more_or_next(driver) -> bool`
Attempts to load more search results.

**Parameters:**
- `driver`: WebDriver instance

**Returns:** True if more results loaded

**Strategies:**
1. Desktop: Click "Next" button
2. Mobile: Click "More results" button
3. Fallback: Infinite scroll
4. Last resort: Debug snapshot

### `serp_agent.serp.challenge`

#### `is_google_challenge(driver) -> bool`
Detects Google challenge/captcha pages.

**Parameters:**
- `driver`: WebDriver instance

**Returns:** True if challenge detected

**Detection Methods:**
- Page title analysis ("unusual traffic", "sorry")
- DOM element detection (captcha forms)
- Text content scanning

## Network Utilities API

### `serp_agent.net.url_utils`

#### `extract_final_url(a_href: str) -> str`
Extracts final URL from Google redirect links.

**Parameters:**
- `a_href` (str): URL to process

**Returns:** Final destination URL

**Example:**
```python
from serp_agent.net.url_utils import extract_final_url

redirect_url = "https://www.google.com/url?q=https://www.example.com/page&sa=U"
final_url = extract_final_url(redirect_url)
# Returns: "https://www.example.com/page"
```

#### `url_matches_domain(url: str, target_domain: str) -> bool`
Checks if URL belongs to target domain.

**Parameters:**
- `url` (str): URL to check
- `target_domain` (str): Domain to match against

**Returns:** True if URL matches domain

**Features:**
- Handles subdomains (www.example.com matches example.com)
- Ignores protocol (http/https)
- Handles authentication parts in URLs

**Example:**
```python
from serp_agent.net.url_utils import url_matches_domain

# All return True
url_matches_domain("https://www.example.com/page", "example.com")
url_matches_domain("https://blog.example.com/post", "example.com") 
url_matches_domain("http://example.com", "example.com")
```

## Proxy API

### `serp_agent.proxy.extension_builder`

#### `build_proxy_extension(proxy_url: str) -> str`
Creates Chrome MV3 extension for authenticated proxy.

**Parameters:**
- `proxy_url` (str): Full proxy URL with credentials

**Returns:** Path to ZIP file containing extension

**Example:**
```python
from serp_agent.proxy.extension_builder import build_proxy_extension

proxy_url = "http://user:pass@proxy.example.com:8080"
zip_path = build_proxy_extension(proxy_url)
# Returns path to temporary ZIP file
```

**Generated Extension:**
- Manifest v3 compliant
- Configures fixed proxy server
- Handles authentication automatically
- Includes bypass list for localhost

### `serp_agent.proxy.env_proxy`

#### `build_proxy_url_from_env() -> Optional[str]`
Builds proxy URL from environment variables.

**Returns:** Proxy URL string or None if incomplete

**Required Environment Variables:**
- `PROXY_USERNAME`: Proxy username
- `PROXY_PASSWORD`: Proxy password
- `PROXY_HOST`: Proxy hostname (default: gate.decodo.com)
- `PROXY_PORT`: Proxy port (default: 10001)

**Features:**
- URL-encodes credentials safely
- Masks username in log output
- Returns None for incomplete configuration

## Runner API

### `serp_agent.runner.run_task`

#### `run_task(search_query, target_domain, settings=None, **kwargs) -> bool`
Execute complete search and click workflow.

**Parameters:**
- `search_query` (str): Search query to execute
- `target_domain` (str): Domain to find and click
- `settings` (Settings, optional): Configuration object
- `**kwargs`: Legacy parameters for backward compatibility

**Returns:** True if target was successfully clicked

**Example:**
```python
from serp_agent.runner.run_task import run_task

# Using settings object (recommended)
settings = Settings.from_env()
success = run_task("python tutorials", "realpython.com", settings=settings)

# Using legacy parameters
success = run_task(
    "python tutorials", 
    "realpython.com",
    device="mobile",
    headless=True,
    engine="google"
)
```

#### `run_with_env_settings(search_query, target_domain) -> bool`
Convenience function that loads settings from environment.

**Parameters:**
- `search_query` (str): Search query
- `target_domain` (str): Target domain

**Returns:** True if successful

### `serp_agent.runner.cli`

#### `main() -> bool`
Main CLI entry point that reads from environment variables.

**Environment Variables Used:**
- `SEARCH_QUERY` (default: "novia virtual gratis")
- `TARGET_DOMAIN` (default: "noviachat.com")
- All Settings.from_env() variables

**Returns:** True if successful

## Logging API

### `serp_agent.logging.logger`

#### `log(msg: str, level="info")`
Centralized logging function with consistent formatting.

**Parameters:**
- `msg` (str): Message to log
- `level` (str): Log level ("info", "warning", "error", "debug")

**Output Format:**
- Info: `[agent] {message}`
- Warning: `[agent] WARNING: {message}`
- Error: `[agent] ERROR: {message}`
- Debug: `[agent] DEBUG: {message}`

**Example:**
```python
from serp_agent.logging.logger import log

log("Starting search task")
log("Proxy configuration incomplete", "warning")
log("Failed to load page", "error")
log("Detailed trace information", "debug")
```

## Types & Protocols

### `serp_agent.types`

#### `DriverProtocol`
Minimal WebDriver interface for testing.

```python
class DriverProtocol(Protocol):
    def get(self, url: str) -> None: ...
    def quit(self) -> None: ...
    def find_elements(self, by: str, value: str) -> List[ElementProtocol]: ...
    def execute_script(self, script: str, *args) -> Any: ...
    def execute_cdp_cmd(self, cmd: str, cmd_args: dict) -> dict: ...
    @property
    def title(self) -> str: ...
```

#### `ElementProtocol`
Minimal WebElement interface for testing.

```python
class ElementProtocol(Protocol):
    def click(self) -> None: ...
    def send_keys(self, *value: str) -> None: ...
    def clear(self) -> None: ...
    def get_attribute(self, name: str) -> Optional[str]: ...
    def is_displayed(self) -> bool: ...
```

### `serp_agent.errors`

#### Custom Exceptions

```python
class SerpAgentError(Exception):
    """Base exception for SERP Agent"""

class ChallengeDetected(SerpAgentError):
    """Raised when search engine challenge/captcha detected"""

class NavigationError(SerpAgentError):
    """Raised when navigation or page loading fails"""

class ConfigError(SerpAgentError):
    """Raised when configuration is invalid"""

class ProxyError(SerpAgentError):
    """Raised when proxy connection fails"""

class SearchError(SerpAgentError):
    """Raised when search operation fails"""
```

## Usage Examples

### Basic Usage
```python
from serp_agent.runner.run_task import run_with_env_settings

# Uses .env file configuration
success = run_with_env_settings("python tutorials", "realpython.com")
```

### Advanced Usage
```python
from serp_agent.config.settings import Settings, BrowserConfig, SearchConfig
from serp_agent.runner.run_task import run_task

# Custom configuration
settings = Settings(
    browser=BrowserConfig(device="mobile", headless=True),
    search=SearchConfig(engine="google", max_pages=10)
)

success = run_task("web development", "mdn.org", settings=settings)
```

### Direct API Usage
```python
from serp_agent.browser.driver_factory import build_driver
from serp_agent.serp.router import SearchEngineRouter

# Manual workflow
driver = build_driver(device="desktop")
try:
    status = SearchEngineRouter.search_with_fallback(
        driver, "machine learning", "tensorflow.org"
    )
    print(f"Search result: {status}")
finally:
    driver.quit()
```

This API reference provides complete documentation for integrating and extending SERP Agent in your projects.
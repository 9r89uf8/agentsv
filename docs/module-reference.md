# SERP Agent Module Reference

Quick reference guide to what each file and directory contains.

## 📁 Project Structure

```
superv2simple/
├── serp_agent/                 # Main package
├── docs/                      # Documentation
├── .env                       # Environment variables
├── main.py                    # Entry point
├── README.md                  # Project overview
└── test_refactor.py          # Basic tests
```

## 🔍 Module Breakdown

### 🏗️ Core Package (`serp_agent/`)

#### 📋 Configuration (`config/`)
**Purpose**: Centralized configuration management

- **`settings.py`** - Configuration dataclasses and environment loading
  - `Settings` - Main configuration container
  - `BrowserConfig` - Browser-specific settings (device, headless, profile)
  - `ProxyConfig` - Proxy credentials and settings
  - `SearchConfig` - Search engine parameters (max pages, timeouts)
  - `PathsConfig` - File paths and cleanup settings
  - `Settings.from_env()` - Load all settings from environment variables

- **`constants.py`** - Static values and default settings
  - User agent strings for desktop/mobile
  - Window sizes and device metrics
  - Timeout values and scroll parameters
  - CSS selectors for common elements
  - Chrome arguments and browser settings

#### 🌐 Browser Control (`browser/`)
**Purpose**: WebDriver management and browser interactions

- **`driver_factory.py`** - WebDriver creation and setup
  - `build_driver()` - Create configured Chrome WebDriver
  - Device emulation (desktop vs Pixel 5 mobile)
  - Anti-automation script injection
  - Proxy extension installation

- **`actions.py`** - User interaction utilities
  - `click_safely()` - Robust clicking with fallbacks
  - `robust_tap()` - Advanced mobile tapping (4 strategies)
  - `find_more_results_control()` - Mobile "More results" button finder

- **`consent.py`** - Cookie/GDPR popup handling
  - `accept_cookies_if_present()` - Auto-accept cookie consent
  - Handles both top-level and iframe consent forms
  - Uses configurable selectors

- **`history.py`** - Browser profile management
  - `wipe_browsing_history()` - Clean history while keeping cookies
  - Removes browsing traces for privacy
  - Handles file permissions and delays

- **`diagnostics.py`** - Debug and troubleshooting tools
  - `dump_serp_snapshot()` - Save HTML snapshot with timestamp
  - Log viewport, user agent, and page state
  - Create diagnostic files for debugging

#### 🔍 Search Engines (`serp/`)
**Purpose**: Search engine implementations and result processing

- **`base.py`** - Core interfaces and types
  - `SearchEngine` - Abstract base class for all engines
  - `SearchStatus` - Enum for search results (CLICKED, NOT_FOUND, CHALLENGE, ERROR)
  - Template method pattern for search workflow

- **`google.py`** - Google search implementation
  - `GoogleSearchEngine` - Complete Google search workflow
  - `ensure_serp_loaded()` - Wait for search results page
  - Challenge detection integration
  - Progressive scrolling and pagination

- **`bing.py`** - Bing search implementation
  - `BingSearchEngine` - Bing search with simpler pagination
  - Traditional next-page navigation
  - Fallback option when Google fails

- **`router.py`** - Engine selection and orchestration
  - `SearchEngineRouter` - Central engine dispatcher
  - Auto-fallback logic (Google → Challenge → Bing)
  - `search_with_fallback()` - Complete search workflow
  - Legacy compatibility functions

- **`scan_strategies.py`** - Result scanning algorithms
  - `progressive_scroll_and_scan()` - Scroll-based result scanning
  - `attempt_load_more_or_next()` - Pagination handling (desktop/mobile)
  - Staggered delays for human-like behavior
  - URL extraction and domain matching

- **`challenge.py`** - Anti-bot detection
  - `is_google_challenge()` - Detect captcha/challenge pages
  - Multiple detection heuristics (title, DOM, text)
  - Pure function for easy testing

#### 🔌 Proxy Management (`proxy/`)
**Purpose**: Proxy setup and credential handling

- **`extension_builder.py`** - Chrome extension generator
  - `build_proxy_extension()` - Create MV3 proxy extension
  - Generate manifest.json and background.js
  - Embed credentials safely in extension
  - Return temporary ZIP file path

- **`env_proxy.py`** - Environment-based proxy config
  - `build_proxy_url_from_env()` - Build proxy URL from env vars
  - URL-encode credentials properly
  - Mask sensitive info in logs
  - Only module that loads .env file for proxy

#### 🌐 Network Utilities (`net/`)
**Purpose**: URL processing and network helpers

- **`url_utils.py`** - URL parsing and domain matching
  - `extract_final_url()` - Extract final URL from Google redirects
  - `url_matches_domain()` - Check if URL belongs to target domain
  - Handle subdomains, protocols, authentication parts
  - Pure functions for easy unit testing

#### 🏃 Orchestration (`runner/`)
**Purpose**: Main workflow coordination and CLI

- **`run_task.py`** - Main workflow orchestrator
  - `run_task()` - Complete search workflow (setup → search → cleanup)
  - `run_with_env_settings()` - Convenience function using env vars
  - Supports both Settings objects and legacy parameters
  - Proper cleanup order (driver quit → history wipe)

- **`cli.py`** - Command-line interface
  - `main()` - CLI entry point with env var loading
  - Load .env file before reading environment
  - Maintain backward compatibility
  - Simple success/failure reporting

#### 📝 Logging (`logging/`)
**Purpose**: Centralized logging system

- **`logger.py`** - Single logging function
  - `log()` - Consistent formatted logging
  - Support for different levels (info, warning, error, debug)
  - All modules import from here (no direct print statements)

#### 🚨 Support Files (Package Root)

- **`errors.py`** - Custom exception hierarchy
  - `SerpAgentError` - Base exception
  - `ChallengeDetected` - Search engine challenge
  - `NavigationError` - Page loading failures
  - `ConfigError` - Invalid configuration
  - `ProxyError` - Proxy connection issues
  - `SearchError` - Search operation failures

- **`types.py`** - Type protocols for testing
  - `DriverProtocol` - Minimal WebDriver interface
  - `ElementProtocol` - Minimal WebElement interface
  - Enable mocking without tight Selenium coupling

### 📄 Root Files

- **`main.py`** - Application entry point
  - Imports and calls CLI main function
  - Keep this file minimal

- **`.env`** - Environment configuration
  - All configuration values
  - Not tracked in git (add to .gitignore)

- **`test_refactor.py`** - Basic functionality tests
  - URL utility tests
  - Settings loading tests
  - Logging functionality tests
  - Quick smoke tests

### 📚 Documentation (`docs/`)

- **`architecture.md`** - Complete system design documentation
  - Design principles and module responsibilities
  - Data flow and interaction patterns
  - Configuration model and extension points

- **`api-reference.md`** - Detailed function documentation
  - All public APIs with examples
  - Parameter descriptions and return values
  - Usage patterns and best practices

- **`developer-guide.md`** - Extension and contribution guide
  - Adding new search engines
  - Creating custom strategies
  - Testing approaches and debugging

- **`module-reference.md`** - This file, quick module overview

## 🔄 Data Flow Summary

### High-Level Flow
```
CLI → Settings → Driver → Search Engine → Results → Cleanup
```

### Detailed Flow
1. **CLI** (`cli.py`) loads environment and calls runner
2. **Settings** (`settings.py`) parses configuration from env vars
3. **Driver Factory** (`driver_factory.py`) creates configured browser
4. **Router** (`router.py`) selects appropriate search engine
5. **Search Engine** (`google.py`/`bing.py`) executes search workflow:
   - **Prepare**: Navigate to homepage, accept cookies (`consent.py`)
   - **Query**: Type search query and submit
   - **Scan**: Use strategies (`scan_strategies.py`) to find results
   - **Click**: Use actions (`actions.py`) to click target
6. **Cleanup**: Quit driver, wipe history (`history.py`)

## 🎯 Key Design Patterns

### Dependency Injection
- Pass dependencies as parameters, not global imports
- Example: `build_driver(proxy_url=...)` instead of importing proxy module

### Template Method
- `SearchEngine.search_and_click()` defines workflow
- Subclasses implement specific steps (`prepare`, `perform_query`, `find_and_click_target`)

### Strategy Pattern
- Multiple scanning strategies in `scan_strategies.py`
- Search engines choose appropriate strategy for their results format

### Protocol-Based Testing
- `types.py` defines minimal interfaces
- Enables mocking without importing Selenium

### Centralized Configuration
- All settings in `config/` module
- Environment variables mapped to typed dataclasses
- Single source of truth for defaults

## 🚦 Import Rules

### Allowed Imports
- Any module can import from `logging/`, `config/`, `errors.py`
- `browser/` modules can import from each other
- `serp/` modules can import from `browser/`, `net/`
- `runner/` can import from any module (orchestration layer)

### Forbidden Imports
- `config/` cannot import from other modules (circular dependency)
- `browser/` cannot import from `serp/` (wrong direction)
- `serp/` cannot import from `proxy/` directly (use config)
- Only `proxy/env_proxy.py` should import `dotenv`

## 🧪 Testing Strategy

### Unit Tests (Fast)
- `net/url_utils.py` - Pure functions
- `serp/challenge.py` - Detection logic
- `config/settings.py` - Configuration parsing

### Integration Tests (Slower)  
- `browser/driver_factory.py` - Browser creation
- `serp/` engines - Complete search workflows
- `runner/run_task.py` - End-to-end orchestration

### Mocking Strategy
- Use `types.py` protocols to create fake drivers
- Mock browser interactions without real Chrome instance
- Test business logic separately from browser automation

This module reference provides a quick way to understand what each file does and how the system fits together.
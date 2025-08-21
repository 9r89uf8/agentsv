# SERP Agent Architecture Documentation

## Overview

SERP Agent is a modular web search automation package that was refactored from a monolithic 822-line script into a clean, maintainable architecture with proper separation of concerns.

## Design Principles

### 1. **Single Responsibility Principle**
Each module has one clear purpose:
- `config/` - Configuration management
- `browser/` - Browser setup and interaction
- `serp/` - Search engine logic
- `proxy/` - Proxy handling
- `net/` - Network utilities
- `logging/` - Centralized logging
- `runner/` - Orchestration and CLI

### 2. **Dependency Inversion**
Core logic depends on interfaces (e.g., `SearchEngine` protocol), not concrete implementations. This enables:
- Easy testing with mocks
- Simple addition of new search engines
- Swappable components

### 3. **Clean Boundaries**
Modules don't reach "across the stack":
- `browser/*` never imports `serp/*`
- `serp/*` never reaches `proxy/*` directly
- Only `runner/` orchestrates between layers

## Package Structure

```
serp_agent/
├── __init__.py
├── config/                 # Configuration & Constants
│   ├── settings.py         # Dataclasses for configuration
│   └── constants.py        # Static values, timeouts, selectors
├── logging/                # Centralized Logging
│   └── logger.py          # Single log() function
├── proxy/                  # Proxy Management
│   ├── extension_builder.py  # Chrome MV3 proxy extension
│   └── env_proxy.py       # Environment-based proxy config
├── browser/                # Browser Control & Interaction
│   ├── driver_factory.py  # WebDriver creation & setup
│   ├── history.py         # History management
│   ├── consent.py         # Cookie/GDPR handling
│   ├── actions.py         # Click/tap/scroll utilities
│   └── diagnostics.py     # Debug snapshots
├── net/                    # Network Utilities
│   └── url_utils.py       # URL parsing & domain matching
├── serp/                   # Search Engine Results Processing
│   ├── base.py           # SearchEngine interface & status enum
│   ├── google.py         # Google search implementation
│   ├── bing.py           # Bing search implementation
│   ├── scan_strategies.py # Page scanning algorithms
│   ├── challenge.py      # Captcha/challenge detection
│   └── router.py         # Engine selection & fallback
├── runner/                 # Orchestration & CLI
│   ├── run_task.py       # Main workflow orchestrator
│   └── cli.py            # Command-line interface
├── errors.py              # Custom exceptions
└── types.py               # Type protocols for testing
```

## Data Flow Architecture

### High-Level Flow
```
CLI Input → Settings → Driver Setup → Search Engine → Result Processing
    ↓           ↓           ↓             ↓              ↓
   .env    Configuration  Browser    SERP Processing   Cleanup
```

### Detailed Sequence

1. **Initialization**
   ```
   cli.py → load_dotenv() → Settings.from_env() → Proxy/Browser Config
   ```

2. **Driver Setup**
   ```
   Settings → driver_factory.build_driver() → Chrome + Extensions + Emulation
   ```

3. **Search Execution**
   ```
   router.py → SearchEngine.prepare() → perform_query() → find_and_click_target()
   ```

4. **Result Processing**
   ```
   scan_strategies.py → URL matching → Click actions → Status reporting
   ```

5. **Cleanup**
   ```
   driver.quit() → history.wipe_browsing_history() → Status logging
   ```

## Module Responsibilities

### Configuration Layer (`config/`)

**`settings.py`**
- Defines configuration dataclasses: `BrowserConfig`, `ProxyConfig`, `SearchConfig`, `PathsConfig`
- Provides `Settings.from_env()` for environment-based configuration
- Maintains backward compatibility with original environment variables

**`constants.py`**
- Centralizes all static values: timeouts, user agents, selectors
- Device profiles for desktop/mobile emulation
- Chrome arguments and browser settings

### Logging Layer (`logging/`)

**`logger.py`**
- Single `log(msg, level)` function with consistent formatting
- Supports different log levels (info, warning, error, debug)
- All modules import from here - no direct print statements

### Proxy Layer (`proxy/`)

**`extension_builder.py`**
- Creates Chrome MV3 extension ZIP for authenticated proxies
- Handles proxy URL parsing and credential embedding
- Generates manifest.json and background.js for Chrome extension

**`env_proxy.py`**
- Reads proxy credentials from environment variables
- URL-encodes credentials and builds proxy URLs
- Masks sensitive information in logs
- Only module that touches `dotenv`

### Browser Layer (`browser/`)

**`driver_factory.py`**
- Creates and configures undetected Chrome WebDriver
- Applies device emulation (desktop vs mobile Pixel 5)
- Injects CDP anti-automation scripts
- Handles proxy extension installation

**`history.py`**
- Manages Chrome profile history cleanup
- Removes browsing history while preserving cookies
- Handles file permissions and cleanup delays

**`consent.py`**
- Handles cookie consent and GDPR popups
- Supports both top-level and iframe-based consent forms
- Uses configurable selectors from constants

**`actions.py`**
- Provides robust click/tap utilities (`click_safely`, `robust_tap`)
- Handles element interaction failures with multiple fallback strategies
- Finds and interacts with mobile "More results" controls

**`diagnostics.py`**
- Captures page snapshots for debugging
- Logs viewport, user agent, and page state information
- Creates timestamped HTML dumps

### Network Layer (`net/`)

**`url_utils.py`**
- Extracts final URLs from Google redirect links
- Matches domains with subdomain support
- Pure functions with no side effects - easily testable

### Search Engine Layer (`serp/`)

**`base.py`**
- Defines `SearchEngine` abstract interface
- Declares `SearchStatus` enum (CLICKED, NOT_FOUND, CHALLENGE, ERROR)
- Provides template workflow: prepare → query → find_and_click

**`google.py`**
- Implements Google-specific search logic
- Handles query input with realistic typing simulation
- Detects and handles Google challenges/captchas
- Uses progressive scrolling and pagination

**`bing.py`**
- Implements Bing search with simpler pagination
- Handles Bing-specific selectors and navigation
- Provides fallback when Google is unavailable

**`scan_strategies.py`**
- `progressive_scroll_and_scan()`: Scrolls page in steps, scanning for target domain
- `attempt_load_more_or_next()`: Handles pagination (desktop "Next" vs mobile "More results")
- Implements throttling and staggered delays to appear human-like

**`challenge.py`**
- Detects Google "unusual traffic" and captcha pages
- Uses multiple heuristics: page title, DOM elements, text content
- Pure function - easily unit testable

**`router.py`**
- Implements engine selection logic ("google", "bing", "auto")
- Handles automatic fallback: Google → Challenge → Bing
- Provides both class-based and legacy function interfaces

### Orchestration Layer (`runner/`)

**`run_task.py`**
- Main workflow orchestrator
- Coordinates: Settings → Driver → Search → Cleanup
- Supports both modern Settings objects and legacy parameters
- Ensures proper cleanup order: quit driver → wipe history

**`cli.py`**
- Command-line interface with environment variable support
- Loads .env file before reading environment variables
- Maintains backward compatibility with original script behavior

### Support Files

**`errors.py`**
- Custom exception hierarchy for better error handling
- Specific exceptions: `ChallengeDetected`, `NavigationError`, `ConfigError`
- Enables predictable control flow

**`types.py`**
- Type protocols for WebDriver and WebElement interfaces
- Enables unit testing with mock objects
- Provides type safety without tight coupling to Selenium

## Configuration Model

### Settings Hierarchy
```
Settings
├── BrowserConfig (device, headless, profile settings)
├── ProxyConfig (proxy URL, credentials)
├── SearchConfig (engine, pagination, timeouts)
└── PathsConfig (directories, cleanup settings)
```

### Environment Variable Mapping
```
SEARCH_QUERY        → CLI query input
TARGET_DOMAIN       → CLI target input
DEVICE             → BrowserConfig.device
HEADLESS           → BrowserConfig.headless
MAX_PAGES          → SearchConfig.max_pages
SCROLLS_PER_BATCH  → SearchConfig.scroll_steps_per_batch
ENGINE             → SearchConfig.engine
USER_DATA_DIR      → BrowserConfig.user_data_dir
PROFILE_DIRECTORY  → BrowserConfig.profile_directory
PROXY_USERNAME     → ProxyConfig (via env_proxy)
PROXY_PASSWORD     → ProxyConfig (via env_proxy)
PROXY_HOST         → ProxyConfig (via env_proxy)
PROXY_PORT         → ProxyConfig (via env_proxy)
```

## Extension Points

### Adding New Search Engines
1. Implement `SearchEngine` interface in new file (e.g., `duckduckgo.py`)
2. Add engine to `router.py` selection logic
3. Register in `SearchEngineRouter.get_engine()`

### Adding New Scanning Strategies
1. Create new strategy function in `scan_strategies.py`
2. Accept driver and configuration parameters
3. Return boolean success/failure
4. Integrate into search engine `find_and_click_target()` methods

### Adding New Device Profiles
1. Add device metrics to `constants.py`
2. Update `BrowserConfig` to recognize new device name
3. Modify `driver_factory.py` to apply new profile

## Testing Strategy

### Unit Tests (Fast, No Browser)
- **URL utilities**: Test redirect extraction and domain matching with sample URLs
- **Challenge detection**: Feed HTML snippets to detection functions
- **Configuration**: Test settings loading and validation
- **Router logic**: Test engine selection and fallback behavior

### Integration Tests (Optional, Slower)
- **Driver creation**: Test browser setup with different configurations
- **Search flow**: Test complete workflow with mock search engines
- **History cleanup**: Test file deletion with temporary profiles

### Testing with Mocks
The `types.py` protocols enable easy mocking:
```python
class FakeDriver:
    def __init__(self):
        self.actions = []
    
    def execute_script(self, script):
        self.actions.append(('script', script))
        return mock_result
```

## Performance Considerations

### Memory Management
- Driver instances are properly cleaned up in `finally` blocks
- History files are removed to prevent profile bloat
- Temporary proxy extensions are created in temp directories

### Network Efficiency
- Progressive scrolling reduces unnecessary page loads
- Staggered delays prevent rate limiting
- Connection reuse via persistent Chrome profiles

### Scalability
- Stateless search engines support parallel execution
- Configuration-driven timeouts allow tuning for different environments
- Modular design enables horizontal scaling

## Security Considerations

### Proxy Credentials
- Credentials are URL-encoded and embedded in Chrome extension
- Username is masked in logs (shows first 2 + last 1 characters)
- Proxy extensions are created in temporary directories

### Browser Fingerprinting
- Anti-automation scripts injected via CDP
- Realistic user agents for desktop/mobile
- Human-like typing and scrolling patterns
- Persistent profiles maintain cookies and login state

### Data Privacy
- History cleanup removes browsing traces while preserving cookies
- No sensitive data logged or stored permanently
- Proxy configuration isolated in dedicated modules

## Troubleshooting

### Common Issues
1. **Environment variables not loaded**: Ensure `.env` file exists and `load_dotenv()` is called
2. **Proxy connection failed**: Check proxy credentials and network connectivity
3. **Challenge detection**: May require adjusting selectors in `constants.py`
4. **Mobile emulation**: Verify device metrics and CDP commands work

### Debug Tools
- `diagnostics.dump_serp_snapshot()` captures page state
- Logging levels can be adjusted for verbose output
- Browser can be run in non-headless mode for visual debugging

## Future Improvements

### Potential Enhancements
- Structured logging with JSON output
- Metrics collection and reporting
- Plugin system for custom search engines
- Distributed execution with message queues
- Machine learning for better challenge detection

### Monitoring
- Success/failure rates by search engine
- Response time tracking
- Challenge detection frequency
- Resource usage metrics

This architecture provides a solid foundation for web search automation while maintaining flexibility, testability, and maintainability.
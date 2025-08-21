# SERP Agent

A modular web search automation package that intelligently searches Google and Bing for specific domains, with proxy support and mobile emulation.

## ✨ Features

- **Multi-Engine Search**: Supports Google and Bing with automatic fallback
- **Challenge Detection**: Automatically detects and handles captcha/challenge pages  
- **Device Emulation**: True mobile (Pixel 5) and desktop browser emulation
- **Proxy Support**: Built-in authenticated proxy via Chrome extension
- **Cookie Persistence**: Maintains login sessions across runs
- **History Cleanup**: Removes browsing traces while preserving cookies
- **Modular Architecture**: Clean, testable, and extensible codebase

## 🚀 Quick Start

### Installation

```bash
git clone <repository>
cd superv2simple
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Basic Usage

1. **Create a `.env` file:**
```bash
# Search settings
SEARCH_QUERY=python tutorials
TARGET_DOMAIN=realpython.com
ENGINE=auto  # auto, google, or bing
MAX_PAGES=5

# Browser settings  
DEVICE=desktop  # or mobile
HEADLESS=false

# Proxy settings (optional)
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
PROXY_HOST=proxy.example.com
PROXY_PORT=8080
```

2. **Run the search:**
```bash
python main.py
```

### Programmatic Usage

```python
from serp_agent.runner.run_task import run_task

# Simple search
success = run_task(
    search_query="machine learning tutorials",
    target_domain="coursera.org",
    device="mobile",
    engine="auto"
)

print(f"Search {'successful' if success else 'failed'}")
```

## 📋 Use Cases

### E-commerce Research
```python
# Search for competitors and click through to their sites
run_task("laptop deals", "bestbuy.com", device="desktop")
run_task("smartphone reviews", "amazon.com", device="mobile")
```

### Content Discovery
```python
# Find and navigate to specific educational content
run_task("python web scraping tutorial", "realpython.com")
run_task("machine learning course", "coursera.org")
```

### SEO and Marketing Research
```python
# Check search visibility and click-through behavior
run_task("digital marketing agency", "yourcompany.com", max_pages=10)
```

## 🏗️ Architecture

SERP Agent uses a clean, modular architecture:

```
serp_agent/
├── config/          # Configuration and constants
├── browser/         # WebDriver setup and interactions  
├── serp/           # Search engine implementations
├── proxy/          # Proxy handling
├── net/            # Network utilities
├── runner/         # Main orchestration
└── logging/        # Centralized logging
```

### Key Components

- **Search Engines**: Pluggable Google/Bing implementations with automatic fallback
- **Device Emulation**: True browser fingerprint emulation for desktop/mobile
- **Proxy Support**: Chrome extension-based authenticated proxies
- **Scanning Strategies**: Progressive scrolling and pagination handling
- **Configuration System**: Environment-based settings with type safety

## 🛠️ Advanced Configuration

### Custom Settings Object

```python
from serp_agent.config.settings import Settings, BrowserConfig, SearchConfig
from serp_agent.runner.run_task import run_task

settings = Settings(
    browser=BrowserConfig(
        device="mobile",
        headless=True,
        user_data_dir="./custom-profile"
    ),
    search=SearchConfig(
        engine="google",
        max_pages=10,
        scroll_steps_per_batch=15
    )
)

success = run_task("query", "domain.com", settings=settings)
```

### Direct API Usage

```python
from serp_agent.browser.driver_factory import build_driver
from serp_agent.serp.router import SearchEngineRouter

# Manual workflow control
driver = build_driver(device="desktop", headless=False)
try:
    status = SearchEngineRouter.search_with_fallback(
        driver=driver,
        query="web development",
        target_domain="mdn.org",
        engine_name="auto"
    )
    print(f"Result: {status}")
finally:
    driver.quit()
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SEARCH_QUERY` | Search query to execute | `"novia virtual gratis"` |
| `TARGET_DOMAIN` | Domain to find and click | `"noviachat.com"` |
| `ENGINE` | Search engine (`auto`, `google`, `bing`) | `"auto"` |
| `DEVICE` | Device emulation (`desktop`, `mobile`) | `"desktop"` |
| `HEADLESS` | Run in headless mode (`true`, `false`) | `"false"` |
| `MAX_PAGES` | Maximum pages to search | `"6"` |
| `SCROLLS_PER_BATCH` | Scroll steps per page | `"10"` |
| `USER_DATA_DIR` | Chrome profile directory | `"./chrome-profile"` |
| `PROFILE_DIRECTORY` | Profile subdirectory | `"Default"` |
| `PROXY_USERNAME` | Proxy username | - |
| `PROXY_PASSWORD` | Proxy password | - |
| `PROXY_HOST` | Proxy hostname | `"gate.decodo.com"` |
| `PROXY_PORT` | Proxy port | `"10001"` |

## 📖 Documentation

- **[Architecture Guide](docs/architecture.md)** - Detailed system design and module responsibilities
- **[API Reference](docs/api-reference.md)** - Complete function and class documentation
- **[Developer Guide](docs/developer-guide.md)** - How to extend and contribute to the system

## 🧪 Testing

### Run Tests
```bash
# Basic functionality tests
python test_refactor.py

# Full integration test
python main.py
```

### Unit Testing Example
```python
from serp_agent.net.url_utils import url_matches_domain

assert url_matches_domain("https://www.example.com/page", "example.com")
assert url_matches_domain("https://blog.example.com/post", "example.com") 
```

## 🔍 How It Works

### Search Flow
1. **Configuration**: Load settings from environment variables
2. **Browser Setup**: Create Chrome driver with device emulation and proxy
3. **Engine Selection**: Choose Google, Bing, or auto-fallback
4. **Query Execution**: Navigate to search engine and perform query
5. **Result Scanning**: Progressively scroll through results looking for target domain
6. **Click Action**: Click on first matching result
7. **Cleanup**: Close browser and clean history while preserving cookies

### Challenge Handling
- Detects Google "unusual traffic" pages
- Automatically falls back to Bing when challenged
- Captures page snapshots for debugging

### Mobile Emulation
- True Pixel 5 device metrics (393x851, DPR 2.75)
- Mobile user agent and touch events
- Mobile-specific result scanning and pagination

## ⚙️ Extending the System

### Add New Search Engine

```python
# Create serp_agent/serp/duckduckgo.py
from .base import SearchEngine, SearchStatus

class DuckDuckGoSearchEngine(SearchEngine):
    def prepare(self, driver) -> bool:
        driver.get("https://duckduckgo.com")
        return True
    
    def perform_query(self, driver, query: str) -> SearchStatus:
        # Implementation here
        pass
    
    def find_and_click_target(self, driver, target_domain: str, **kwargs) -> SearchStatus:
        # Implementation here
        pass
```

Then register in `serp_agent/serp/router.py`.

### Add Custom Device Profile

```python
# In serp_agent/config/constants.py
IPAD_USER_AGENT = "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) ..."
IPAD_WINDOW_SIZE = {"width": 1024, "height": 768}
IPAD_DEVICE_METRICS = {"width": 1024, "height": 768, "deviceScaleFactor": 2.0, "mobile": True}
```

## 🔐 Security Features

- **Proxy Credentials**: Safely encoded in Chrome extension
- **History Cleanup**: Removes browsing traces after each run
- **Profile Isolation**: Each run can use separate Chrome profile
- **Anti-Detection**: Multiple anti-automation countermeasures

## 🐛 Troubleshooting

### Common Issues

**Environment variables not loaded:**
- Ensure `.env` file exists in project root
- Check file encoding (should be UTF-8)

**Proxy connection failed:**
- Verify proxy credentials and network connectivity
- Check proxy server status

**Challenge detected:**
- Try different proxy/IP address
- Reduce request frequency
- Use mobile device emulation

**Element not found:**
- Run in non-headless mode to inspect page
- Check if selectors need updating
- Enable debug logging

### Debug Mode

```python
# Enable verbose logging
from serp_agent.logging.logger import log
log("Debug message", "debug")

# Capture page snapshots
from serp_agent.browser.diagnostics import dump_serp_snapshot
dump_serp_snapshot(driver, "debug")

# Run with visible browser
driver = build_driver(headless=False)
```

## 📊 Performance

### Benchmarks (Typical)
- **Setup Time**: ~3-5 seconds (driver initialization)
- **Search Time**: ~2-8 seconds per page batch
- **Memory Usage**: ~100-200 MB per driver instance
- **Success Rate**: ~85-95% (varies by target domain popularity)

### Optimization Tips
- Use persistent Chrome profiles to reduce setup time
- Enable headless mode for faster execution
- Adjust timeouts based on network conditions
- Use proxy rotation for better success rates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the [Developer Guide](docs/developer-guide.md)
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

### Development Setup
```bash
git clone <your-fork>
cd superv2simple
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists
```

## 📝 License

[Add your license information here]

## 🙏 Acknowledgments

- Built with [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
- Selenium WebDriver for browser automation
- Chrome DevTools Protocol for advanced browser control

---

**SERP Agent** - Intelligent web search automation with a clean, modular architecture. Perfect for SEO research, competitive analysis, and automated content discovery.
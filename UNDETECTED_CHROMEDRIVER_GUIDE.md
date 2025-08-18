# Undetected ChromeDriver Guide

This guide explains how to use undetected-chromedriver to perform web automation while bypassing anti-bot detection systems.

## What is Undetected ChromeDriver?

Undetected ChromeDriver is a Python library that provides an optimized Selenium ChromeDriver patch designed to bypass anti-bot services like:
- Cloudflare
- Distill Network 
- Imperva
- DataDome
- And other bot detection systems

## Installation

### Prerequisites
- Python 3.6 or higher
- Chrome browser installed on your system

### Install via pip
```bash
pip install undetected-chromedriver
```

### Install additional dependencies (optional)
```bash
pip install selenium
pip install requests
```

## Basic Usage

### Simple Example
```python
import undetected_chromedriver as uc

# Create Chrome instance with anti-detection patches
driver = uc.Chrome()

# Navigate to any website
driver.get('https://example.com')

# Perform your automation tasks
# ...

# Clean up
driver.quit()
```

### Running the Basic Example
```bash
python undetected_browser_basic.py
```

This script will:
1. Test bot detection on nowsecure.nl
2. Perform a Google search
3. Save screenshots for verification

## Advanced Configuration

### Custom Options Example
```python
import undetected_chromedriver as uc

# Create Chrome options
options = uc.ChromeOptions()

# Set custom profile directory
options.add_argument("--user-data-dir=/path/to/profile")

# Additional stealth options
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

# Create driver with custom options
driver = uc.Chrome(
    options=options,
    version_main=None,  # Auto-detect Chrome version
    headless=False      # Keep visible for better stealth
)
```

### Running the Advanced Example
```bash
python undetected_browser_advanced.py
```

This script demonstrates:
- Custom Chrome options for maximum stealth
- Multiple bot detection site testing
- Session and cookie management
- Human-like interaction patterns

## Key Features

### Automatic Driver Management
- Automatically downloads the correct ChromeDriver version
- Patches the driver binary to avoid detection
- Handles version compatibility automatically

### Stealth Capabilities
- Removes automation indicators from the browser
- Bypasses common WebDriver detection methods
- Supports custom user agents and profiles

### Compatibility
- Works with Chrome, Brave, and other Chromium browsers
- Compatible with existing Selenium code
- Cross-platform support (Windows, Linux, macOS)

## Important Limitations

⚠️ **What it CANNOT do:**
- Hide your IP address
- Guarantee 100% undetection (depends on IP reputation)
- Work reliably in headless mode (limited support)

⚠️ **Performance Considerations:**
- Running from datacenter IPs may trigger detection
- Residential IPs generally work better
- Some sites may still detect automation based on behavior patterns

## Configuration Options

### Chrome Options
```python
options = uc.ChromeOptions()

# Window and display options
options.add_argument("--window-size=1366,768")
options.add_argument("--disable-gpu")

# Performance options  
options.add_argument("--disable-images")
options.add_argument("--disable-plugins")
options.add_argument("--disable-extensions")

# Stealth options
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
```

### Driver Initialization Parameters
```python
driver = uc.Chrome(
    options=options,
    version_main=120,                    # Specific Chrome version
    driver_executable_path="/path/to/driver",  # Custom driver path
    browser_executable_path="/path/to/chrome", # Custom Chrome path  
    port=9222,                          # Custom port
    log_level=0,                        # Logging level
    headless=False,                     # Headless mode (not recommended)
    use_subprocess=True,                # Use subprocess for stability
    debug=False                         # Debug mode
)
```

## Testing Your Setup

### Bot Detection Test Sites
Use these sites to verify your setup is working:

1. **nowsecure.nl** - Basic bot detection test
2. **bot.sannysoft.com** - Comprehensive detection analysis  
3. **intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html** - Headless detection test

### Verification Steps
1. Run the basic example script
2. Check the generated screenshots
3. Look for "Chrome is being controlled by automated test software" warnings
4. Verify that detection tests show "Not detected" or similar

## Troubleshooting

### Common Issues

**Chrome not found:**
```bash
# Install Chrome on Ubuntu/Debian
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install google-chrome-stable
```

**Permission errors:**
```bash
# Fix permissions on Linux
chmod +x /path/to/chromedriver
```

**Detection still occurring:**
- Try running from a residential IP
- Reduce automation speed (add delays)
- Use different user agents
- Enable JavaScript and images
- Avoid headless mode

### Debug Mode
Enable debug mode for troubleshooting:
```python
driver = uc.Chrome(debug=True)
```

## Next Steps

1. Start with the basic example to verify your setup
2. Customize the advanced example for your specific needs
3. Test thoroughly with your target websites
4. Implement proper error handling and retry logic
5. Consider using residential proxies for additional stealth

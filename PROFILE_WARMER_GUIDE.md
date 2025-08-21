# Chrome Profile Warmer Guide

A standalone utility for warming up Chrome profiles with proxy support, built using components from the SERP Agent system.

## Features

- **Proxy Support**: Automatically uses proxy configuration from `.env` file
- **Manual Navigation**: Full control over browsing - no automation
- **Profile Persistence**: Updates and maintains Chrome profile state
- **Mobile/Desktop Mode**: Respects device settings from configuration
- **Reusable Components**: Built entirely using existing SERP Agent components

## Usage

### Basic Usage

Run without arguments to open a blank page:
```bash
python profile_warmer.py
```

### With Starting URL

Provide a URL to navigate to initially:
```bash
python profile_warmer.py google.com
```

Or with full URL:
```bash
python profile_warmer.py https://www.example.com
```

## Configuration

The warmer uses the same `.env` configuration as the main SERP Agent:

```env
# Proxy settings (required for proxy)
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
PROXY_HOST=proxy.example.com
PROXY_PORT=20000

# Browser settings
DEVICE=desktop  # or mobile
HEADLESS=false
USER_DATA_DIR=./chrome-profile
PROFILE_DIRECTORY=Default
```

## How It Works

1. **Loads Configuration**: Reads settings from `.env` file
2. **Builds Browser**: Creates Chrome instance with:
   - Proxy extension (if configured)
   - User profile directory
   - Device emulation settings
3. **Manual Control**: Opens browser and waits for user navigation
4. **Profile Update**: All browsing activity updates the Chrome profile

## Workflow

1. Start the warmer:
   ```bash
   python profile_warmer.py
   ```

2. Browser opens with configuration details displayed:
   ```
   Chrome Profile Warmer
   ==================================================
   Profile Directory: ./chrome-profile
   Device Mode: desktop
   Proxy: mx.decodo.com:20000
   Proxy User: sppv44l85w
   ==================================================
   ```

3. Navigate manually to warm the profile:
   - Visit target sites
   - Accept cookies
   - Log into accounts
   - Build browsing history

4. Press ENTER in the console when done

5. Browser closes and profile is saved

## Benefits

- **Cookie Persistence**: Maintains cookies across sessions
- **History Building**: Creates natural browsing patterns
- **Proxy Verification**: Test proxy connectivity
- **Manual Control**: Full control over what sites to visit
- **Profile Warming**: Prepare profiles for automated tasks

## Troubleshooting

### Browser doesn't open
- Check if Chrome/Chromium is installed
- Verify proxy credentials in `.env`
- Ensure USER_DATA_DIR path is writable

### Proxy not working
- Verify PROXY_USERNAME and PROXY_PASSWORD are correct
- Check PROXY_HOST and PROXY_PORT
- Test proxy connectivity separately

### Profile not persisting
- Check USER_DATA_DIR permissions
- Ensure PROFILE_DIRECTORY exists
- Don't delete chrome-profile directory

## Integration

This warmer is designed to prepare Chrome profiles for use with the main SEO task runner. After warming a profile:

1. The same profile can be used by `main_seo.py`
2. Cookies and authentication persist
3. Browsing patterns appear more natural

## Notes

- The proxy extension is automatically built and injected
- All navigation is manual - no automation
- Profile changes are saved automatically
- Works with both desktop and mobile modes
- Respects all settings from `.env` file
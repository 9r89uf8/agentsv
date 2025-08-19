"""
WebDriver factory and configuration
"""
import os
from typing import Optional
import undetected_chromedriver as uc
from ..config.constants import *
from ..logging.logger import log
from ..proxy.extension_builder import build_proxy_extension


def build_driver(
    proxy_url: Optional[str] = None,
    device: str = "desktop",
    headless: bool = False,
    user_data_dir: Optional[str] = "./chrome-profile",
    profile_directory: str = "Default",
) -> uc.Chrome:
    """
    Creates and configures a Chrome WebDriver instance.
    
    Args:
        proxy_url: Optional proxy URL for extension-based proxy
        device: "desktop" or "mobile" 
        headless: Whether to run in headless mode
        user_data_dir: Path to persist Chrome profile (cookies, prefs, etc.)
        profile_directory: Profile directory name within user_data_dir
        
    Returns:
        Configured WebDriver instance
    """
    options = uc.ChromeOptions()
    
    # Add base Chrome arguments
    for arg in CHROME_ARGS:
        options.add_argument(arg)

    # Persist profile unless user passes None
    if user_data_dir:
        options.add_argument(f'--user-data-dir={os.path.abspath(user_data_dir)}')
        options.add_argument(f'--profile-directory={profile_directory}')

    # Configure device-specific settings
    if device == "mobile":
        options.add_argument(f"--user-agent={MOBILE_USER_AGENT}")
        options.add_argument(f"--window-size={MOBILE_WINDOW_SIZE['width']},{MOBILE_WINDOW_SIZE['height']}")
    else:
        options.add_argument(f"--user-agent={DESKTOP_USER_AGENT}")
        options.add_argument(f"--window-size={DESKTOP_WINDOW_SIZE['width']},{DESKTOP_WINDOW_SIZE['height']}")

    if headless:
        options.add_argument("--headless=new")

    # Add proxy extension if provided
    if proxy_url:
        ext_zip = build_proxy_extension(proxy_url)
        options.add_extension(ext_zip)

    # Create the driver
    driver = uc.Chrome(options=options, headless=headless)

    # Reduce webdriver signals via CDP
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            window.chrome = { runtime: {} };
        '''
    })

    # Configure mobile emulation if needed
    if device == "mobile":
        # True Pixel 5 metrics (no 'scale' param)
        # CSS viewport 393x851, DPR ~2.75
        try:
            driver.set_window_rect(
                width=MOBILE_WINDOW_SIZE['width'], 
                height=MOBILE_WINDOW_SIZE['height'], 
                x=0, y=0
            )
        except Exception:
            pass

        try:
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", MOBILE_DEVICE_METRICS)
            driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {"enabled": True})
            driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
                "userAgent": MOBILE_USER_AGENT,
                "platform": "Android",
                "acceptLanguage": "en-US,en"
            })
            log("Mobile emulation enabled and window sized to Pixel 5.")
        except Exception as e:
            log(f"Warning: failed to enable mobile emulation via CDP: {e}")
    else:
        # Ensure desktop is clean
        try:
            driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
            driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {"enabled": False})
        except Exception:
            pass

    # Quick verification
    try:
        w = driver.execute_script("return window.innerWidth")
        h = driver.execute_script("return window.innerHeight")
        dpr = driver.execute_script("return window.devicePixelRatio")
        ua = driver.execute_script("return navigator.userAgent")
        plat = driver.execute_script("return navigator.platform || 'n/a'")
        log(f"Viewport: {w}x{h} | DPR: {dpr} | UA Mobile? {'Mobile' in ua} | platform: {plat}")
    except Exception:
        pass

    return driver
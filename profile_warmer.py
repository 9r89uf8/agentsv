"""
Chrome Profile Warmer with Proxy Support

This script opens a Chrome browser with proxy configuration for manual navigation.
It reuses components from the SERP Agent without modifying any existing files.
"""
import sys
import time
from dotenv import load_dotenv
from serp_agent.config.settings import Settings
from serp_agent.browser.driver_factory import build_driver
from serp_agent.logging.logger import log


def warm_profile(initial_url: str = None):
    """
    Open Chrome browser with proxy for manual profile warming
    
    Args:
        initial_url: Optional URL to navigate to initially (default: blank page)
    """
    # Load environment variables
    load_dotenv()
    
    # Load settings from environment
    settings = Settings.from_env()
    
    # Display configuration
    print("\nChrome Profile Warmer")
    print("=" * 50)
    print(f"Profile Directory: {settings.browser.user_data_dir}")
    print(f"Device Mode: {settings.browser.device}")
    print(f"Headless: {settings.browser.headless}")
    
    if settings.proxy.enabled:
        print(f"Proxy: {settings.proxy.host}:{settings.proxy.port}")
        print(f"Proxy User: {settings.proxy.username}")
    else:
        print("Proxy: Not configured")
    
    print("=" * 50)
    
    # Build Chrome driver with proxy
    print("\nStarting Chrome browser...")
    driver = build_driver(
        proxy_url=settings.proxy.proxy_url if settings.proxy.enabled else None,
        device=settings.browser.device,
        headless=settings.browser.headless,
        user_data_dir=settings.browser.user_data_dir,
        profile_directory=settings.browser.profile_directory
    )
    
    try:
        # Navigate to initial URL if provided
        if initial_url:
            print(f"Navigating to: {initial_url}")
            driver.get(initial_url)
        else:
            # Open Google search page
            driver.get("https://www.google.com")
            print("Opened Google search page")
        
        # Display browser info
        current_url = driver.current_url
        print(f"\nBrowser ready at: {current_url}")
        print("\n" + "=" * 50)
        print("PROFILE WARMING MODE ACTIVE")
        print("Navigate manually to warm up the Chrome profile")
        print("The proxy is active for all navigation")
        print("=" * 50)
        
        # Keep browser open for manual navigation
        print("\nPress ENTER to close the browser when done...")
        input()
        
        # Get final URL before closing
        final_url = driver.current_url
        print(f"\nFinal URL: {final_url}")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        log(f"Profile warmer error: {e}", "error")
    finally:
        print("\nClosing browser...")
        driver.quit()
        print("Browser closed successfully")
        print("\nProfile has been updated with your browsing session")


def main():
    """Main entry point"""
    # Check if URL was provided as command line argument
    initial_url = None
    if len(sys.argv) > 1:
        initial_url = sys.argv[1]
        if not initial_url.startswith(("http://", "https://")):
            initial_url = "https://" + initial_url
    
    try:
        warm_profile(initial_url)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
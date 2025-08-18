import undetected_chromedriver as uc
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def advanced_undetected_browsing():
    """
    Advanced example of using undetected-chromedriver with custom configuration
    options for maximum stealth and control.
    """
    
    # Create Chrome options for advanced configuration
    options = uc.ChromeOptions()
    
    # Set custom user data directory to maintain sessions
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    
    # Additional stealth options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")  # Faster loading
    options.add_argument("--disable-javascript")  # Optional: disable JS for faster scraping
    
    # Set window size to appear more human-like
    options.add_argument("--window-size=1366,768")
    
    # Set user agent to appear more legitimate
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Create Chrome instance with advanced options
    driver = uc.Chrome(
        options=options,
        version_main=None,  # Auto-detect Chrome version
        driver_executable_path=None,  # Auto-download driver
        browser_executable_path=None,  # Use system Chrome
        port=0,  # Use random port
        log_level=0,  # Minimal logging
        headless=False,  # Keep visible for better stealth
        use_subprocess=True,
        debug=False
    )
    
    try:
        # Set additional JavaScript to hide automation indicators
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                window.chrome = {
                    runtime: {},
                };
            '''
        })
        
        # Test with multiple bot detection sites
        test_sites = [
            'https://nowsecure.nl',
            'https://bot.sannysoft.com',
            'https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html'
        ]
        
        for i, site in enumerate(test_sites):
            print(f"Testing site {i+1}: {site}")
            driver.get(site)
            
            # Random human-like delay
            time.sleep(2 + (i * 0.5))
            
            # Take screenshot for verification
            screenshot_name = f"advanced_test_{i+1}.png"
            driver.save_screenshot(screenshot_name)
            print(f"Screenshot saved: {screenshot_name}")
        
        # Example of advanced interaction - handling dynamic content
        print("Testing dynamic content handling...")
        driver.get('https://httpbin.org/user-agent')
        
        # Wait for content and extract user agent
        try:
            user_agent_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "pre"))
            )
            user_agent_info = user_agent_element.text
            print(f"Detected User Agent: {user_agent_info}")
        except Exception as e:
            print(f"Could not extract user agent: {e}")
        
        # Test with form submission and cookies
        print("Testing cookie and session handling...")
        driver.get('https://httpbin.org/cookies/set/test_cookie/undetected_session')
        time.sleep(2)
        
        driver.get('https://httpbin.org/cookies')
        cookie_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "pre"))
        )
        cookie_info = cookie_element.text
        print(f"Session cookies: {cookie_info}")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    
    finally:
        # Clean up
        driver.quit()
        print("Advanced browser session closed")

def stealth_google_search(query):
    """
    Perform a stealth Google search with maximum anti-detection measures.
    """
    options = uc.ChromeOptions()
    
    # Minimal profile for clean session
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    driver = uc.Chrome(options=options)
    
    try:
        # Navigate with human-like behavior
        driver.get('https://www.google.com')
        time.sleep(2)
        
        # Handle cookie consent if present
        try:
            accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'I agree')]")
            accept_button.click()
            time.sleep(1)
        except:
            pass  # No cookie consent dialog
        
        # Find search box and enter query with human-like typing
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        # Type with human-like delays
        for char in query:
            search_box.send_keys(char)
            time.sleep(0.1)
        
        time.sleep(1)
        search_box.submit()
        
        # Wait for results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        # Extract search results
        results = driver.find_elements(By.CSS_SELECTOR, "h3")
        print(f"Found {len(results)} search results for: {query}")
        
        for i, result in enumerate(results[:5]):  # First 5 results
            try:
                print(f"{i+1}. {result.text}")
            except:
                pass
        
        driver.save_screenshot(f"stealth_search_{query.replace(' ', '_')}.png")
        
    except Exception as e:
        print(f"Search error: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # Run advanced browsing test
    advanced_undetected_browsing()
    
    # Run stealth search example
    stealth_google_search("python web scraping")
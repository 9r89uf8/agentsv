import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def basic_undetected_browsing():
    """
    Basic example of using undetected-chromedriver to browse websites
    without triggering anti-bot detection systems.
    """
    
    # Create Chrome instance with anti-detection patches
    driver = uc.Chrome()
    
    try:
        # Test with a site that detects bots
        print("Testing bot detection...")
        driver.get('https://nowsecure.nl')
        
        # Wait for page to load
        time.sleep(3)
        
        # Take a screenshot to verify success
        driver.save_screenshot('bot_detection_test.png')
        print("Bot detection test completed - check bot_detection_test.png")
        
        # Example: Navigate to Google and perform a search
        print("Navigating to Google...")
        driver.get('https://www.google.com')
        
        # Wait for search box and perform search
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        search_box.send_keys("web scraping best practices")
        search_box.submit()
        
        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        print("Search completed successfully")
        
        # Take screenshot of results
        driver.save_screenshot('google_search_results.png')
        print("Search results saved to google_search_results.png")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    
    finally:
        # Clean up
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    basic_undetected_browsing()
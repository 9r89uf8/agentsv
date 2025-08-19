"""
Simple test to verify the refactored modules work correctly
"""
from serp_agent.net.url_utils import extract_final_url, url_matches_domain
from serp_agent.config.settings import Settings
from serp_agent.logging.logger import log

def test_url_utils():
    """Test URL utility functions"""
    print("Testing URL utilities...")
    
    # Test extract_final_url
    google_redirect = "https://www.google.com/url?q=https://www.car.com/test&sa=U"
    final_url = extract_final_url(google_redirect)
    assert final_url == "https://www.car.com/test", f"Expected https://www.car.com/test, got {final_url}"
    
    regular_url = "https://example.com/page"
    final_url = extract_final_url(regular_url)
    assert final_url == regular_url, f"Expected {regular_url}, got {final_url}"
    
    # Test url_matches_domain
    assert url_matches_domain("https://www.car.com/page", "car.com"), "Should match car.com"
    assert url_matches_domain("https://subdomain.car.com/page", "car.com"), "Should match subdomain"
    assert not url_matches_domain("https://www.example.com/page", "car.com"), "Should not match different domain"
    
    print("OK URL utilities tests passed")

def test_settings():
    """Test settings loading"""
    print("Testing settings...")
    
    settings = Settings.from_env()
    assert settings.browser.device in ["desktop", "mobile"], "Device should be desktop or mobile"
    assert settings.search.engine in ["auto", "google", "bing"], "Engine should be auto, google, or bing"
    
    print("OK Settings tests passed")

def test_logging():
    """Test logging functionality"""
    print("Testing logging...")
    
    log("Test message")
    log("Warning message", "warning")
    log("Error message", "error")
    
    print("OK Logging tests passed")

if __name__ == "__main__":
    test_url_utils()
    test_settings()
    test_logging()
    print("\nAll tests passed! Refactoring appears successful.")
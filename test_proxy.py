"""
Test Decodo proxy connection
"""
import os
import requests
from dotenv import load_dotenv

def test_proxy_connection():
    """Test if the Decodo proxy is working correctly"""
    
    # Load environment variables
    load_dotenv()
    
    # Get proxy credentials from .env
    username = os.getenv("PROXY_USERNAME")
    password = os.getenv("PROXY_PASSWORD") 
    host = os.getenv("PROXY_HOST")
    port = os.getenv("PROXY_PORT")
    
    if not all([username, password, host, port]):
        print("❌ Error: Missing proxy credentials in .env file")
        print(f"   Username: {'✓' if username else '✗'}")
        print(f"   Password: {'✓' if password else '✗'}")
        print(f"   Host: {'✓' if host else '✗'}")
        print(f"   Port: {'✓' if port else '✗'}")
        return False
    
    # Construct proxy URL
    proxy_url = f"http://{username}:{password}@{host}:{port}"
    
    print(f"🔧 Testing Decodo proxy connection...")
    print(f"   Host: {host}:{port}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    
    # Test proxy connection
    try:
        # First test without proxy to see real IP
        print("\n📍 Your real IP (without proxy):")
        try:
            real_response = requests.get('https://ip.decodo.com/json', timeout=10)
            real_data = real_response.json()
            print(f"   IP: {real_data.get('ip', 'Unknown')}")
            print(f"   Location: {real_data.get('country', 'Unknown')}, {real_data.get('city', 'Unknown')}")
        except:
            print("   Could not fetch real IP")
        
        # Now test with proxy
        print(f"\n🌐 Testing proxy connection to {host}...")
        
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        response = requests.get(
            'https://ip.decodo.com/json',
            proxies=proxies,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Proxy connection successful!")
            print(f"   Proxy IP: {data.get('ip', 'Unknown')}")
            print(f"   Country: {data.get('country', 'Unknown')}")
            print(f"   City: {data.get('city', 'Unknown')}")
            print(f"   ISP: {data.get('org', 'Unknown')}")
            
            # Check if it's a mobile proxy (Mexico)
            if 'Mexico' in data.get('country', '') or 'MX' in data.get('country_code', ''):
                print(f"   ✓ Mobile proxy from Mexico confirmed")
            
            return True
        else:
            print(f"❌ Proxy returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ProxyError as e:
        print(f"\n❌ Proxy authentication failed!")
        print(f"   Error: {str(e)}")
        print(f"\n   Check your credentials:")
        print(f"   - Username: {username}")
        print(f"   - Password: {password}")
        print(f"   - Host: {host}")
        print(f"   - Port: {port}")
        return False
        
    except requests.exceptions.Timeout:
        print(f"\n❌ Connection timeout!")
        print(f"   The proxy server at {host}:{port} is not responding")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("    Decodo Proxy Connection Test")
    print("=" * 50)
    
    success = test_proxy_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Proxy is ready to use with main_seo.py")
    else:
        print("❌ Fix proxy issues before running main_seo.py")
    print("=" * 50)
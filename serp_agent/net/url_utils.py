"""
URL parsing and domain matching utilities
"""
import urllib.parse as urlparse


def extract_final_url(a_href: str) -> str:
    """
    For links like https://www.google.com/url?q=https://www.car.com/...,
    return the value of q; otherwise return the original URL.
    
    Args:
        a_href: The URL to parse
        
    Returns:
        The final URL after extracting from Google's redirect format
    """
    if not a_href:
        return ""
    parsed = urlparse.urlparse(a_href)
    if "google" in (parsed.netloc or "") and parsed.path.startswith("/url"):
        q = urlparse.parse_qs(parsed.query).get("q", [""])[0]
        return q or a_href
    return a_href


def url_matches_domain(url: str, target_domain: str) -> bool:
    """
    True if URL's registrable domain ends with target_domain
    (handles www., subdomains, http/https, and trailing paths)
    
    Args:
        url: The URL to check
        target_domain: The domain to match against
        
    Returns:
        True if the URL matches the target domain
    """
    try:
        netloc = urlparse.urlparse(url).netloc.lower()
        netloc = netloc.split("@")[-1]  # Remove user:pass@ part if present
        return netloc.endswith(target_domain.lower())
    except Exception:
        return False
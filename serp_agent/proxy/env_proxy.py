"""
Environment-based proxy configuration
"""
import os
import urllib.parse as urlparse
from typing import Optional
from dotenv import load_dotenv
from ..logging.logger import log


def build_proxy_url_from_env() -> Optional[str]:
    """
    Safely read .env and build a URL-encoded proxy URL.
    
    Required environment variables:
        PROXY_USERNAME: Proxy username
        PROXY_PASSWORD: Proxy password  
        PROXY_HOST: Proxy host (defaults to gate.decodo.com)
        PROXY_PORT: Proxy port (defaults to 10001)
    
    Returns:
        Proxy URL string if all variables are present, None otherwise
    """
    load_dotenv()

    user_raw = os.getenv("PROXY_USERNAME")
    pass_raw = os.getenv("PROXY_PASSWORD")
    host = os.getenv("PROXY_HOST", "gate.decodo.com")
    port = os.getenv("PROXY_PORT", "10001")

    if not user_raw or not pass_raw or not host or not port:
        log("Proxy env incomplete; launching without proxy.")
        return None

    user_enc = urlparse.quote(user_raw, safe="")
    pass_enc = urlparse.quote(pass_raw, safe="")
    proxy_url = f"http://{user_enc}:{pass_enc}@{host}:{port}"

    masked_user = f"{user_raw[:2]}***{user_raw[-1:]}" if len(user_raw) > 3 else "***"
    log(f"Proxy configured from env: user={masked_user}, host={host}, port={port}")
    return proxy_url
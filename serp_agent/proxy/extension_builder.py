"""
Chrome proxy extension builder for MV3
"""
import os
import json
import zipfile
import tempfile
import urllib.parse as urlparse


def build_proxy_extension(proxy_url: str) -> str:
    """
    Creates a Chrome MV3 extension ZIP that configures a fixed HTTP proxy and
    responds to proxy auth challenges with the supplied username/password.

    Args:
        proxy_url: Proxy URL in format http://USERNAME:PASSWORD@gate.decodo.com:10001

    Returns:
        Path to the generated ZIP file containing the extension

    Raises:
        ValueError: If proxy URL format is invalid
    """
    parsed = urlparse.urlparse(proxy_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Proxy URL must start with http:// or https://")

    if not parsed.hostname or not parsed.port or not parsed.username or not parsed.password:
        raise ValueError("Proxy URL must include username, password, host, and port")

    host = parsed.hostname
    port = parsed.port
    username = urlparse.unquote(parsed.username)
    password = urlparse.unquote(parsed.password)
    scheme = parsed.scheme

    manifest = {
        "name": "Proxy Auth",
        "version": "1.0.0",
        "manifest_version": 3,
        "permissions": [
            "proxy",
            "storage",
            "webRequest",
            "webRequestAuthProvider",
            "tabs"
        ],
        "host_permissions": ["<all_urls>"],
        "background": { "service_worker": "background.js" }
    }

    background_js = f"""
// Configure a fixed proxy
chrome.runtime.onInstalled.addListener(() => {{
  const config = {{
    mode: "fixed_servers",
    rules: {{
      singleProxy: {{
        scheme: "{scheme}",
        host: "{host}",
        port: {port}
      }},
      bypassList: ["localhost", "127.0.0.1"]
    }}
  }};
  chrome.proxy.settings.set({{ value: config, scope: "regular" }}, () => {{}});
}});

// Supply credentials on proxy auth challenges
chrome.webRequest.onAuthRequired.addListener(
  function(details, callback) {{
    callback({{
      authCredentials: {{ username: "{username}", password: "{password}" }}
    }});
  }},
  {{ urls: ["<all_urls>"] }},
  ["blocking"]
);
"""

    tmpdir = tempfile.mkdtemp(prefix="proxy_ext_")
    zip_path = os.path.join(tmpdir, "proxy_auth_extension.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.writestr("background.js", background_js)

    return zip_path
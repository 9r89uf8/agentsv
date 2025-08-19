import os
import re
import json
import zipfile
import tempfile
import time
import urllib.parse as urlparse
from pathlib import Path
from typing import Optional, Set

import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    WebDriverException,
)

# =======================
# Logging
# =======================
def log(msg: str):
    print(f"[agent] {msg}", flush=True)

# =======================
# Proxy extension builder
# =======================
def build_proxy_extension(proxy_url: str) -> str:
    """
    Creates a Chrome MV3 extension ZIP that configures a fixed HTTP proxy and
    responds to proxy auth challenges with the supplied username/password.

    proxy_url example:  http://USERNAME:PASSWORD@gate.decodo.com:10001
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

# =======================
# Driver builder (persistent profile + fixed mobile emu)
# =======================
def build_driver(
    proxy: Optional[str] = None,
    device: str = "desktop",
    headless: bool = False,
    user_data_dir: Optional[str] = "./chrome-profile",
    profile_directory: str = "Default",
) -> uc.Chrome:
    """
    device: "desktop" or "mobile"
    user_data_dir: path to persist Chrome profile (cookies, prefs, etc.)
    """
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-US,en")
    options.add_argument("--force-device-scale-factor=1")  # avoid zoom/DPI oddities

    # Persist profile unless user passes None
    if user_data_dir:
        options.add_argument(f'--user-data-dir={os.path.abspath(user_data_dir)}')
        options.add_argument(f'--profile-directory={profile_directory}')

    if device == "mobile":
        # We'll also override via CDP after launch.
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Linux; Android 12; Pixel 5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
        )
        # Window hint; we hard-set post-launch too.
        options.add_argument("--window-size=393,851")
    else:
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        options.add_argument("--window-size=1366,820")

    if headless:
        options.add_argument("--headless=new")

    if proxy:
        ext_zip = build_proxy_extension(proxy)
        options.add_extension(ext_zip)

    driver = uc.Chrome(options=options, headless=headless)

    # Reduce webdriver signals
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            window.chrome = { runtime: {} };
        '''
    })

    if device == "mobile":
        # True Pixel 5 metrics (no 'scale' param)
        # CSS viewport 393x851, DPR ~2.75
        try:
            driver.set_window_rect(width=393, height=851, x=0, y=0)
        except Exception:
            pass

        try:
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 393,
                "height": 851,
                "deviceScaleFactor": 2.75,
                "mobile": True
            })
            driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {"enabled": True})
            driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
                "userAgent": (
                    "Mozilla/5.0 (Linux; Android 12; Pixel 5) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
                ),
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

# =======================
# Helpers
# =======================
def accept_cookies_if_present(driver):
    """
    Handle common consent flows, including consent iframes.
    """
    time.sleep(0.6)
    selectors = [
        "//button//*[contains(text(),'Accept')]/ancestor::button",
        "//button[contains(., 'Accept')]",
        "//button[contains(., 'I agree')]",
        "//div[contains(@role,'button') and (contains(.,'Accept') or contains(.,'I agree'))]"
    ]
    for sel in selectors:
        try:
            btn = WebDriverWait(driver, 1.5).until(EC.element_to_be_clickable((By.XPATH, sel)))
            btn.click()
            time.sleep(0.4)
            log("Accepted cookies (top-level).")
            return
        except Exception:
            pass

    try:
        iframes = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='consent'],iframe[src*='consent.google']")
        for fr in iframes:
            driver.switch_to.frame(fr)
            try:
                iframe_btns = [
                    "//button//*[contains(text(),'Accept')]/ancestor::button",
                    "//button[contains(., 'Accept all')]",
                    "//button[contains(., 'I agree')]",
                    "//button[@aria-label='Accept all']",
                ]
                for ib in iframe_btns:
                    try:
                        btn = WebDriverWait(driver, 1.5).until(EC.element_to_be_clickable((By.XPATH, ib)))
                        btn.click()
                        time.sleep(0.4)
                        driver.switch_to.default_content()
                        log("Accepted cookies (iframe).")
                        return
                    except Exception:
                        continue
            finally:
                driver.switch_to.default_content()
    except Exception:
        pass

def ensure_serp_loaded(driver, timeout=12):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#search, #rso"))
    )

def extract_final_url(a_href: str) -> str:
    """
    For links like https://www.google.com/url?q=https://www.car.com/...,
    return the value of q; otherwise return the original URL.
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
    True if URL's registrable domain endswith target_domain
    (handles www., subdomains, http/https, and trailing paths)
    """
    try:
        netloc = urlparse.urlparse(url).netloc.lower()
        netloc = netloc.split("@")[-1]
        return netloc.endswith(target_domain.lower())
    except Exception:
        return False

def click_safely(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(0.12)
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();")

def find_more_results_control(driver, timeout=4.0):
    """
    Returns the 'More results' control if present/visible (mobile SERP).
    We try multiple shapes: role=button, <a>, <div role=button>, etc.
    """
    locators = [
        (By.XPATH, "//*[@aria-label='More results']"),
        (By.XPATH, "//*[self::a or self::button or @role='button'][.//span[normalize-space()='More results'] or contains(normalize-space(.),'More results')]"),
        (By.XPATH, "//div[@role='button' and .//span[contains(.,'More results')]]"),
        # fallback: anything with role=button near the bottom area
        (By.XPATH, "//*[@role='button' and contains(.,'More') and contains(.,'result')]"),
    ]
    end = time.time() + timeout
    while time.time() < end:
        for by, sel in locators:
            try:
                elements = driver.find_elements(by, sel)
                for el in elements:
                    if el.is_displayed():
                        return el
            except Exception:
                pass
        time.sleep(0.15)
    return None

def robust_tap(driver, el) -> bool:
    """
    Try to activate a mobile control in the most bulletproof way:
    - center scroll + blur any focused field
    - native .click()
    - JS click()
    - pointer/touch events
    - DevTools CDP touch injection at element center
    """
    try:
        driver.execute_script("document.activeElement && document.activeElement.blur();")
    except Exception:
        pass

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", el)
        time.sleep(0.2)
    except Exception:
        pass

    # 1) normal click
    try:
        el.click()
        return True
    except Exception:
        pass

    # 2) JS click
    try:
        driver.execute_script("arguments[0].click();", el)
        return True
    except Exception:
        pass

    # 3) pointer/touch events on the element
    try:
        js = """
        const el = arguments[0];
        const fire = (type, opts={}) => el.dispatchEvent(new PointerEvent(type, Object.assign({
            bubbles:true, cancelable:true, composed:true, pointerType:'touch', isPrimary:true
        }, opts)));
        fire('pointerdown'); fire('pointerup');
        el.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, composed:true}));
        return true;
        """
        driver.execute_script(js, el)
        return True
    except Exception:
        pass

    # 4) DevTools: tap at element center (CSS pixels in main frame viewport)
    try:
        rect = driver.execute_script("""
            const r = arguments[0].getBoundingClientRect();
            return {x: r.left + r.width/2, y: r.top + r.height/2};
        """, el)
        x, y = float(rect["x"]), float(rect["y"])

        # small jiggle to unstick sticky overlays
        try:
            driver.execute_script("window.scrollBy(0, -40);"); time.sleep(0.05)
            driver.execute_script("window.scrollBy(0,  60);"); time.sleep(0.05)
        except Exception:
            pass

        # touch start/end = tap
        driver.execute_cdp_cmd("Input.dispatchTouchEvent", {
            "type": "touchStart",
            "touchPoints": [{"x": x, "y": y, "radiusX": 2, "radiusY": 2, "force": 1}]
        })
        driver.execute_cdp_cmd("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        return True
    except Exception as e:
        log(f"[tap] CDP tap failed: {e}")

    return False

def dump_serp_snapshot(driver, tag: str = "serp") -> Path:
    try:
        ua = driver.execute_script("return navigator.userAgent")
        vw = driver.execute_script("return window.innerWidth")
        vh = driver.execute_script("return window.innerHeight")
        log(f"[diag] UA: {ua}")
        log(f"[diag] Viewport: {vw}x{vh}")
    except Exception:
        pass

    html = driver.execute_script("return document.documentElement.outerHTML")
    ts = time.strftime("%Y%m%d-%H%M%S")
    out = Path(f"{tag}_{ts}.html")
    out.write_text(html, encoding="utf-8")
    log(f"[diag] DOM snapshot saved -> {out.resolve()}")
    return out

# Throttled mobile-friendly scroll/scan
def progressive_scroll_and_scan(
    driver,
    target_domain: str,
    seen_hrefs: Optional[Set[str]] = None,
    max_steps: int = 10,
    step_px: int = 700
) -> bool:
    """
    Scroll down the page in steps, scanning for matching anchors after each step.
    Adds staggered delays to look less bursty.
    """
    if seen_hrefs is None:
        seen_hrefs = set()

    last_height = driver.execute_script("return document.body.scrollHeight") or 0

    for i in range(max_steps):
        anchors = driver.find_elements(By.XPATH, "//div[@id='search']//a[@href] | //div[@id='rso']//a[@href]")
        for a in anchors:
            try:
                href = a.get_attribute("href")
                if not href or href in seen_hrefs:
                    continue
                seen_hrefs.add(href)
                final_url = extract_final_url(href)
                if url_matches_domain(final_url, target_domain):
                    log(f"Found target on step {i+1}: {final_url}")
                    click_safely(driver, a)
                    return True
            except WebDriverException:
                continue

        driver.execute_script("window.scrollBy(0, arguments[0]);", step_px)
        time.sleep(0.6 + (0.4 * (i % 3)))  # staggered delay

        try:
            new_height = driver.execute_script("return document.body.scrollHeight") or last_height
            if new_height > last_height:
                last_height = new_height
        except Exception:
            pass

    # Final scan at bottom
    anchors = driver.find_elements(By.XPATH, "//div[@id='search']//a[@href] | //div[@id='rso']//a[@href]")
    for a in anchors:
        try:
            href = a.get_attribute("href")
            if not href or href in seen_hrefs:
                continue
            final_url = extract_final_url(href)
            if url_matches_domain(final_url, target_domain):
                log("Found target on final bottom scan.")
                click_safely(driver, a)
                return True
        except WebDriverException:
            continue

    return False

def attempt_load_more_or_next(driver) -> bool:
    """
    Desktop: click Next.
    Mobile: find/tap 'More results' (touch), else try infinite scroll, else bail.
    Returns True if more results were loaded or navigation occurred.
    """
    # First: classic "Next" (desktop)
    classic = [
        (By.CSS_SELECTOR, "a#pnnext"),
        (By.CSS_SELECTOR, "a[aria-label='Next']"),
        (By.XPATH, "//a[.//span[normalize-space()='Next']]"),
        (By.XPATH, "//a[contains(@aria-label,'Next')]"),
    ]
    for by, sel in classic:
        try:
            ctl = WebDriverWait(driver, 2.0).until(EC.element_to_be_clickable((by, sel)))
            before = driver.execute_script("return document.body.scrollHeight")
            click_safely(driver, ctl)
            time.sleep(1.0)
            after = driver.execute_script("return document.body.scrollHeight")
            if after and before and after != before:
                log("Triggered next page (desktop).")
                return True
        except Exception:
            pass

    # Mobile: explicit "More results" control
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 400);")
    except Exception:
        pass

    btn = find_more_results_control(driver, timeout=2.5)
    if btn:
        before = driver.execute_script("return document.body.scrollHeight")
        if robust_tap(driver, btn):
            time.sleep(1.2)
            # consider "growth" or new results present as success
            try:
                WebDriverWait(driver, 6).until(
                    lambda d: (d.execute_script("return document.readyState") == "complete") or
                              (d.execute_script("return document.body.scrollHeight") > before)
                )
            except TimeoutException:
                pass
            after = driver.execute_script("return document.body.scrollHeight")
            if after and before and after > before:
                log("More results loaded via 'More results' button.")
                return True

    # Stronger infinite scroll fallback (mobile)
    try:
        before = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.9)
        driver.execute_script("window.scrollBy(0, -120);"); driver.execute_script("window.scrollBy(0, 240);")
        time.sleep(0.9)
        after = driver.execute_script("return document.body.scrollHeight")
        if after and before and after > before:
            log("More results loaded via infinite scroll.")
            return True
    except Exception:
        pass

    # Last resort: snapshot for proof/debugging
    dump_serp_snapshot(driver, tag="serp_bottom")
    log("No next control and no additional content detected.")
    return False

# =======================
# Challenge detection
# =======================
def is_google_challenge(driver) -> bool:
    """Return True if Google 'unusual traffic' / challenge page is shown."""
    try:
        title = (driver.title or "").lower()
        if "unusual traffic" in title or "sorry" in title:
            return True
        if driver.find_elements(By.CSS_SELECTOR, 'form[action*="sorry"], #captcha, img[alt*="captcha"]'):
            return True
        texts = driver.find_elements(
            By.XPATH,
            "//*[contains(translate(., 'UNUSUAL TRAFFIC', 'unusual traffic'), 'unusual traffic') "
            "or contains(translate(., 'VERIFY YOU ARE A HUMAN', 'verify you are a human'), 'verify you are a human')]"
        )
        return len(texts) > 0
    except Exception:
        return False

# =======================
# Search flows
# =======================
def search_and_click_domain_google(
    driver,
    query: str,
    target_domain: str,
    max_pages: int = 5,
    scroll_steps_per_batch: int = 10
) -> int:
    """
    Google path.
    Returns:
        1  -> clicked
        0  -> not found / ended
       -1  -> challenge detected (caller may fallback)
    """
    driver.get("https://www.google.com/ncr")
    accept_cookies_if_present(driver)

    # Enter query
    box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
    box.clear()
    for ch in query:
        box.send_keys(ch)
        time.sleep(0.02)
    box.send_keys(Keys.ENTER)

    # Wait for SERP or challenge
    try:
        WebDriverWait(driver, 8).until(
            lambda d: is_google_challenge(d) or d.find_elements(By.CSS_SELECTOR, "#search, #rso")
        )
    except TimeoutException:
        log("Timed out waiting for SERP or challenge.")
        return 0

    if is_google_challenge(driver):
        log("Google challenge detected. Aborting Google path for this run.")
        return -1

    seen_hrefs: Set[str] = set()

    for page_idx in range(1, max_pages + 1):
        try:
            ensure_serp_loaded(driver, timeout=12)
            log(f"Scanning batch {page_idx} ...")

            if progressive_scroll_and_scan(
                driver,
                target_domain,
                seen_hrefs=seen_hrefs,
                max_steps=scroll_steps_per_batch
            ):
                return 1

            # Not found; attempt to load more results (next page or infinite append)
            if not attempt_load_more_or_next(driver):
                return 0

        except TimeoutException:
            log("Timed out waiting for results; attempting to load more.")
            if not attempt_load_more_or_next(driver):
                return 0

    return 0

def search_and_click_domain_bing(
    driver,
    query: str,
    target_domain: str,
    max_pages: int = 3
) -> bool:
    driver.get("https://www.bing.com/?setlang=en")
    accept_cookies_if_present(driver)
    box = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.NAME, "q")))
    box.clear()
    box.send_keys(query)
    box.send_keys(Keys.ENTER)

    for page_idx in range(1, max_pages + 1):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ol#b_results")))
        anchors = driver.find_elements(By.CSS_SELECTOR, "ol#b_results li.b_algo h2 a, ol#b_results li.b_algo a")
        for a in anchors:
            href = a.get_attribute("href")
            final_url = extract_final_url(href)
            if url_matches_domain(final_url, target_domain):
                click_safely(driver, a)
                return True
        # next page
        try:
            next_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.sb_pagN, a[title='Next page']"))
            )
            click_safely(driver, next_btn)
            time.sleep(1.0)
        except Exception:
            break
    return False

def search_and_click_domain(
    driver,
    query: str,
    target_domain: str,
    engine: str = "auto",
    max_pages: int = 5,
    scroll_steps_per_batch: int = 10
) -> bool:
    """
    engine: "google", "bing", or "auto" (try Google; if challenge, fallback to Bing)
    """
    engine = (engine or "auto").lower()
    if engine == "bing":
        return search_and_click_domain_bing(driver, query, target_domain, max_pages=3)

    if engine == "google":
        return search_and_click_domain_google(driver, query, target_domain, max_pages, scroll_steps_per_batch) == 1

    # auto
    g_result = search_and_click_domain_google(driver, query, target_domain, max_pages, scroll_steps_per_batch)
    if g_result == 1:
        return True
    if g_result == -1:
        log("Falling back to Bing due to Google challenge.")
        return search_and_click_domain_bing(driver, query, target_domain, max_pages=3)
    return False

# =======================
# Env / Proxy
# =======================
def build_proxy_url_from_env() -> Optional[str]:
    """
    Safely read .env and build a URL-encoded proxy URL.
    Required vars: PROXY_USERNAME, PROXY_PASSWORD, PROXY_HOST, PROXY_PORT
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

# =======================
# History wipe (keep cookies, remove local history artifacts)
# =======================
def wipe_browsing_history(user_data_dir: str, profile_dir: str = "Default"):
    """
    Removes Chrome history DBs but leaves cookies/logins intact.
    Run only after Chrome is closed.
    """
    p = Path(user_data_dir) / profile_dir
    targets = [
        "History", "History-journal", "History-wal", "History-shm",
        "Archived History", "Archived History-journal", "Archived History-wal", "Archived History-shm",
        "History Provider Cache",
        "Visited Links",
        "Top Sites", "Top Sites-journal",
        "Shortcuts",
        "Network Action Predictor",
    ]
    for name in targets:
        f = p / name
        try:
            if f.exists():
                os.remove(f)
        except PermissionError:
            time.sleep(0.3)
            try:
                os.remove(f)
            except Exception:
                pass

# =======================
# Runner
# =======================
def run_task(
    search_query: str = "cars in chicago",
    target_domain: str = "car.com",
    proxy_url: Optional[str] = None,
    device: str = "desktop",
    headless: bool = False,
    engine: str = "auto",                 # "google" | "bing" | "auto"
    max_pages: int = 6,
    scroll_steps_per_batch: int = 10,
    user_data_dir: Optional[str] = "./chrome-profile",
    profile_directory: str = "Default",
):
    driver = build_driver(
        proxy=proxy_url,
        device=device,
        headless=headless,
        user_data_dir=user_data_dir,
        profile_directory=profile_directory,
    )
    try:
        clicked = search_and_click_domain(
            driver,
            search_query,
            target_domain,
            engine=engine,
            max_pages=max_pages,
            scroll_steps_per_batch=scroll_steps_per_batch
        )
        if clicked:
            log(f"✅ Clicked a result on {target_domain}")
        else:
            log(f"❌ Could not click {target_domain} within {max_pages} batches.")
        time.sleep(2.0)
    finally:
        driver.quit()
        if user_data_dir:
            wipe_browsing_history(user_data_dir, profile_directory)

# =======================
# Example usage
# =======================
if __name__ == "__main__":
    proxy_url = build_proxy_url_from_env()

    query = os.getenv("SEARCH_QUERY", "novia virtual gratis")
    target = os.getenv("TARGET_DOMAIN", "noviachat.com")
    device = os.getenv("DEVICE", "desktop")             # "desktop" or "mobile"
    headless_env = os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes")
    max_pages = int(os.getenv("MAX_PAGES", "8"))
    scroll_steps_per_batch = int(os.getenv("SCROLLS_PER_BATCH", "10"))
    engine = os.getenv("ENGINE", "auto")                # "google" | "bing" | "auto"
    user_data_dir = os.getenv("USER_DATA_DIR", "./chrome-profile")
    profile_directory = os.getenv("PROFILE_DIRECTORY", "Default")

    run_task(
        search_query=query,
        target_domain=target,
        proxy_url=proxy_url,
        device=device,
        headless=headless_env,
        engine=engine,
        max_pages=max_pages,
        scroll_steps_per_batch=scroll_steps_per_batch,
        user_data_dir=user_data_dir,
        profile_directory=profile_directory,
    )

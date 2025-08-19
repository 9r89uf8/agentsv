"""
Browser diagnostics and debugging utilities
"""
import time
from pathlib import Path
from ..logging.logger import log


def dump_serp_snapshot(driver, tag: str = "serp") -> Path:
    """
    Capture diagnostic information about the current page state.
    
    Args:
        driver: WebDriver instance
        tag: Tag to include in filename
        
    Returns:
        Path to the saved HTML snapshot
    """
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
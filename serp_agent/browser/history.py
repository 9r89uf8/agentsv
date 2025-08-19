"""
Browser history management
"""
import os
import time
from pathlib import Path
from ..config.constants import HISTORY_FILES


def wipe_browsing_history(user_data_dir: str, profile_dir: str = "Default"):
    """
    Removes Chrome history DBs but leaves cookies/logins intact.
    Run only after Chrome is closed.
    
    Args:
        user_data_dir: Path to Chrome user data directory
        profile_dir: Profile directory name (default: "Default")
    """
    p = Path(user_data_dir) / profile_dir
    
    for name in HISTORY_FILES:
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
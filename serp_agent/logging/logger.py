"""
Centralized logging functionality for SERP Agent
"""

def log(msg: str, level: str = "info"):
    """
    Log a message with consistent formatting.
    
    Args:
        msg: Message to log
        level: Log level (info, warning, error, debug)
    """
    prefix = "[agent]"
    if level.lower() == "warning":
        prefix = "[agent] WARNING:"
    elif level.lower() == "error":
        prefix = "[agent] ERROR:"
    elif level.lower() == "debug":
        prefix = "[agent] DEBUG:"
    
    print(f"{prefix} {msg}", flush=True)
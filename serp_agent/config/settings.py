"""
Configuration settings and environment loading for SERP Agent
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from .constants import *


@dataclass
class BrowserConfig:
    """Browser-related configuration"""
    device: str = "desktop"  # "desktop" or "mobile"
    headless: bool = False
    user_data_dir: Optional[str] = "./chrome-profile"
    profile_directory: str = "Default"
    language: str = "en-US,en"
    
    @property
    def user_agent(self) -> str:
        return MOBILE_USER_AGENT if self.device == "mobile" else DESKTOP_USER_AGENT
    
    @property
    def window_size(self) -> dict:
        return MOBILE_WINDOW_SIZE if self.device == "mobile" else DESKTOP_WINDOW_SIZE


@dataclass
class ProxyConfig:
    """Proxy-related configuration"""
    enabled: bool = False
    proxy_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    host: str = DEFAULT_PROXY_HOST
    port: str = DEFAULT_PROXY_PORT


@dataclass
class SearchConfig:
    """Search engine configuration"""
    engine: str = "auto"  # "auto", "google", "bing"
    max_pages: int = DEFAULT_MAX_PAGES
    scroll_steps_per_batch: int = DEFAULT_MAX_SCROLL_STEPS
    serp_timeout: int = DEFAULT_SERP_TIMEOUT
    element_wait: int = DEFAULT_ELEMENT_WAIT
    challenge_wait: int = DEFAULT_CHALLENGE_WAIT


@dataclass
class PathsConfig:
    """Paths and file management configuration"""
    snapshot_dir: str = "."
    history_wipe_enabled: bool = True
    temp_dir: Optional[str] = None


@dataclass
class Settings:
    """Complete configuration settings"""
    browser: BrowserConfig
    proxy: ProxyConfig
    search: SearchConfig
    paths: PathsConfig
    
    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create Settings instance from environment variables.
        Maintains backward compatibility with existing env vars.
        """
        load_dotenv()
        
        # Browser configuration
        device = os.getenv("DEVICE", "desktop")
        headless = os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes")
        user_data_dir = os.getenv("USER_DATA_DIR", "./chrome-profile")
        profile_directory = os.getenv("PROFILE_DIRECTORY", "Default")
        
        browser_config = BrowserConfig(
            device=device,
            headless=headless,
            user_data_dir=user_data_dir,
            profile_directory=profile_directory
        )
        
        # Proxy configuration
        proxy_username = os.getenv("PROXY_USERNAME")
        proxy_password = os.getenv("PROXY_PASSWORD")
        proxy_host = os.getenv("PROXY_HOST", DEFAULT_PROXY_HOST)
        proxy_port = os.getenv("PROXY_PORT", DEFAULT_PROXY_PORT)
        
        proxy_enabled = bool(proxy_username and proxy_password)
        proxy_url = None
        if proxy_enabled:
            from urllib.parse import quote
            user_enc = quote(proxy_username, safe="")
            pass_enc = quote(proxy_password, safe="")
            proxy_url = f"http://{user_enc}:{pass_enc}@{proxy_host}:{proxy_port}"
        
        proxy_config = ProxyConfig(
            enabled=proxy_enabled,
            proxy_url=proxy_url,
            username=proxy_username,
            password=proxy_password,
            host=proxy_host,
            port=proxy_port
        )
        
        # Search configuration
        engine = os.getenv("ENGINE", "auto")
        max_pages = int(os.getenv("MAX_PAGES", str(DEFAULT_MAX_PAGES)))
        scroll_steps = int(os.getenv("SCROLLS_PER_BATCH", str(DEFAULT_MAX_SCROLL_STEPS)))
        
        search_config = SearchConfig(
            engine=engine,
            max_pages=max_pages,
            scroll_steps_per_batch=scroll_steps
        )
        
        # Paths configuration
        paths_config = PathsConfig(
            history_wipe_enabled=bool(user_data_dir)
        )
        
        return cls(
            browser=browser_config,
            proxy=proxy_config,
            search=search_config,
            paths=paths_config
        )
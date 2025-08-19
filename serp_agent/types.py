"""
Type protocols and interfaces for testing
"""
from typing import Protocol, Any, List, Optional


class ElementProtocol(Protocol):
    """Minimal WebElement interface for testing"""
    
    def click(self) -> None:
        """Click the element"""
        pass
    
    def send_keys(self, *value: str) -> None:
        """Send keys to the element"""
        pass
    
    def clear(self) -> None:
        """Clear the element content"""
        pass
    
    def get_attribute(self, name: str) -> Optional[str]:
        """Get element attribute"""
        pass
    
    def is_displayed(self) -> bool:
        """Check if element is displayed"""
        pass


class DriverProtocol(Protocol):
    """Minimal WebDriver interface for testing"""
    
    def get(self, url: str) -> None:
        """Navigate to URL"""
        pass
    
    def quit(self) -> None:
        """Quit the driver"""
        pass
    
    def find_elements(self, by: str, value: str) -> List[ElementProtocol]:
        """Find elements"""
        pass
    
    def execute_script(self, script: str, *args: Any) -> Any:
        """Execute JavaScript"""
        pass
    
    def execute_cdp_cmd(self, cmd: str, cmd_args: dict) -> dict:
        """Execute Chrome DevTools command"""
        pass
    
    @property
    def title(self) -> str:
        """Get page title"""
        pass
    
    def switch_to(self) -> Any:
        """Switch context (frames, windows)"""
        pass
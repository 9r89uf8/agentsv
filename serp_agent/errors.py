"""
Custom exceptions for SERP Agent
"""


class SerpAgentError(Exception):
    """Base exception for SERP Agent"""
    pass


class ChallengeDetected(SerpAgentError):
    """Raised when a search engine challenge/captcha is detected"""
    pass


class NavigationError(SerpAgentError):
    """Raised when navigation or page loading fails"""
    pass


class ConfigError(SerpAgentError):
    """Raised when configuration is invalid or incomplete"""
    pass


class ProxyError(SerpAgentError):
    """Raised when proxy configuration or connection fails"""
    pass


class SearchError(SerpAgentError):
    """Raised when search operation fails"""
    pass
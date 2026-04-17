"""Custom exceptions for the application."""

from typing import Optional


class IncidentBriefError(Exception):
    """Base exception for incident brief generator."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DataFetchError(IncidentBriefError):
    """Exception raised when failing to fetch data from external services."""
    pass


class NewRelicAPIError(DataFetchError):
    """New Relic API specific errors."""
    pass


class SplunkAPIError(DataFetchError):
    """Splunk API specific errors."""
    pass


class JiraAPIError(DataFetchError):
    """Jira API specific errors."""
    pass


class ValidationError(IncidentBriefError):
    """Exception raised for input validation errors."""
    pass


class ConfigurationError(IncidentBriefError):
    """Exception raised for configuration errors."""
    pass
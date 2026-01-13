"""
Base API client interface.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseAPIClient(ABC):
    """Base class for API clients."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: API key for authentication
            base_url: Optional custom base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url.strip() if base_url and base_url.strip() else None
    
    @abstractmethod
    def call(
        self,
        prompt: str,
        model: str,
        system_message: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Make an API call.
        
        Args:
            prompt: User prompt
            model: Model name to use
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Response text from the API
            
        Raises:
            APIError: If the API call fails
        """
        ...

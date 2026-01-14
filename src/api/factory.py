"""
Factory for creating API clients based on model name.
"""

import logging
from typing import Optional

from .base import BaseAPIClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from ..exceptions import APIError

logger = logging.getLogger(__name__)


def get_api_client(
    model_name: str,
    api_key: str,
    base_url: Optional[str] = None
) -> BaseAPIClient:
    """
    Get the appropriate API client based on model name.
    
    Args:
        model_name: Name of the model (e.g., "gpt-5.2", "deepseek-v3-2", "claude-3-5-sonnet")
        api_key: API key for authentication
        base_url: Optional custom base URL
        
    Returns:
        Appropriate API client instance
        
    Raises:
        APIError: If the model provider is not supported
    """
    model_lower = model_name.lower()
    
    if model_lower.startswith(("gpt-", "o1-", "deepseek-")):
        logger.debug(f"Using OpenAI client for model: {model_name}")
        return OpenAIClient(api_key, base_url)
    elif model_lower.startswith("claude-"):
        logger.debug(f"Using Anthropic client for model: {model_name}")
        return AnthropicClient(api_key, base_url)
    else:
        # Default to OpenAI for unknown models
        logger.warning(
            f"Unknown model provider for {model_name}, defaulting to OpenAI"
        )
        return OpenAIClient(api_key, base_url)

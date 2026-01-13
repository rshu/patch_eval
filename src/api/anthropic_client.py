"""
Anthropic API client implementation.
"""

import logging
from typing import Optional

try:
    import anthropic
except ImportError:
    anthropic = None

from .base import BaseAPIClient
from ..exceptions import APIError

logger = logging.getLogger(__name__)


class AnthropicClient(BaseAPIClient):
    """Anthropic API client."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize Anthropic client."""
        if anthropic is None:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )
        
        super().__init__(api_key, base_url)
        
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        
        self.client = anthropic.Anthropic(**client_kwargs)
        logger.debug("Initialized Anthropic client")
    
    def call(
        self,
        prompt: str,
        model: str,
        system_message: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> str:
        """Call Anthropic API."""
        if system_message is None:
            system_message = (
                "You are a strict, detail-oriented code review judge for "
                "software-engineering patches. Always respond with valid JSON."
            )
        
        if max_tokens is None:
            max_tokens = 4096
        
        try:
            logger.info(f"Calling Anthropic API with model: {model}")
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Handle different content block types
            if message.content and len(message.content) > 0:
                content_block = message.content[0]
                if hasattr(content_block, 'text'):
                    content = content_block.text
                else:
                    content = str(content_block)
                logger.debug("Successfully received response from Anthropic API")
                return content
            else:
                raise APIError("No content in response from Anthropic API")
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}", exc_info=True)
            raise APIError(f"Error calling Anthropic API: {str(e)}") from e

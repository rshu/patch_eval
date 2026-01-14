"""
OpenAI API client implementation.
"""

import logging
from typing import Optional

try:
    import openai
except ImportError:
    openai = None

from .base import BaseAPIClient
from ..exceptions import APIError

logger = logging.getLogger(__name__)


class OpenAIClient(BaseAPIClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize OpenAI client."""
        if openai is None:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            )
        
        super().__init__(api_key, base_url)
        
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        
        self.client = openai.OpenAI(**client_kwargs)
        logger.debug("Initialized OpenAI client")
    
    def call(
        self,
        prompt: str,
        model: str,
        system_message: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> str:
        """Call OpenAI API."""
        if system_message is None:
            system_message = (
                "You are a strict, detail-oriented code review judge for "
                "software-engineering patches. Always respond with valid JSON."
            )
        
        try:
            logger.info(f"Calling OpenAI API with model: {model}")
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            if not response.choices:
                raise APIError("No choices in response from OpenAI API")
            
            content = response.choices[0].message.content
            if not content:
                raise APIError("Empty content in response from OpenAI API")
            
            logger.debug(f"Successfully received response from OpenAI API ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}", exc_info=True)
            raise APIError(f"Error calling OpenAI API: {str(e)}") from e

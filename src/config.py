"""
Configuration management for the patch evaluation tool.
"""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration."""
    
    # Server configuration
    server_host: str = "127.0.0.1"
    server_port: int = 7860
    share: bool = False
    
    # Model configuration
    default_model: str = "gpt-5.1"
    available_models: List[str] = None
    
    # API configuration
    default_temperature: float = 0.3
    max_tokens: int = 4096
    
    # File configuration
    prompt_template_path: str = "prompt_ref.txt"
    max_preview_size: int = 5000
    
    # Supported file types
    supported_file_types: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.available_models is None:
            self.available_models = ["gpt-5.1", "deepseek-v3-2"]
        
        if self.supported_file_types is None:
            self.supported_file_types = [".patch", ".diff", ".txt"]


def get_config() -> AppConfig:
    """Get application configuration."""
    return AppConfig(
        server_host=os.getenv("SERVER_HOST", "127.0.0.1"),
        server_port=int(os.getenv("SERVER_PORT", "7860")),
        share=os.getenv("SHARE", "false").lower() == "true",
        prompt_template_path=os.getenv("PROMPT_TEMPLATE_PATH", "prompt_ref.txt"),
    )


def get_prompt_template_path() -> Path:
    """Get the path to the prompt template file."""
    config = get_config()
    template_path = Path(config.prompt_template_path)
    
    if not template_path.is_absolute():
        # Try relative to project root
        project_root = Path(__file__).parent.parent
        template_path = project_root / config.prompt_template_path
    
    return template_path

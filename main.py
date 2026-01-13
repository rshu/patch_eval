#!/usr/bin/env python3
"""
Main entry point for the Patch Evaluation Tool.

This script initializes logging and launches the Gradio web interface.
"""

import logging
import sys
from pathlib import Path

from src.config import get_config
from src.ui import create_ui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('patch_eval.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    logger.info("Starting Patch Evaluation Tool")
    
    # Get configuration
    config = get_config()
    
    # Verify prompt template exists
    from src.config import get_prompt_template_path
    template_path = get_prompt_template_path()
    if not template_path.exists():
        logger.error(f"Prompt template not found: {template_path}")
        print(f"Error: Prompt template not found at {template_path}")
        print("Please ensure prompt_ref.txt exists in the project root.")
        sys.exit(1)
    
    # Create and launch UI
    try:
        demo = create_ui()
        logger.info(f"Launching server on {config.server_host}:{config.server_port}")
        demo.launch(
            share=config.share,
            server_name=config.server_host,
            server_port=config.server_port
        )
    except Exception as e:
        logger.error(f"Error launching application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
File utility functions for reading and processing patch files.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from ..exceptions import FileReadError, PromptTemplateError
from ..config import get_prompt_template_path

logger = logging.getLogger(__name__)


def read_patch_file(file: Optional[Union[str, Path]]) -> str:
    """
    Read patch file content from Gradio file upload or file path.
    
    Args:
        file: File path string or file-like object from Gradio
        
    Returns:
        Content of the patch file as string
        
    Raises:
        FileReadError: If the file cannot be read
    """
    if file is None:
        return ""
    
    try:
        # Gradio file upload returns a file path string when type="filepath"
        if isinstance(file, (str, Path)):
            file_path = Path(file)
            if not file_path.exists():
                raise FileReadError(f"File not found: {file_path}")
            
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                logger.debug(f"Successfully read patch file: {file_path}")
                return content
        elif hasattr(file, 'read'):
            # File-like object
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="ignore")
            logger.debug("Successfully read patch file from file-like object")
            return content
        else:
            raise FileReadError(f"Unexpected file type: {type(file)}")
    except FileReadError:
        raise
    except Exception as e:
        logger.error(f"Error reading file: {e}", exc_info=True)
        raise FileReadError(f"Error reading file: {str(e)}") from e


def load_prompt_template() -> str:
    """
    Load the prompt template from the configured file.
    
    Returns:
        The prompt template content
        
    Raises:
        PromptTemplateError: If the template file cannot be loaded
    """
    template_path = get_prompt_template_path()
    
    try:
        if not template_path.exists():
            raise PromptTemplateError(
                f"Prompt template file not found: {template_path}"
            )
        
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
            logger.debug(f"Successfully loaded prompt template from {template_path}")
            return template
    except PromptTemplateError:
        raise
    except Exception as e:
        logger.error(f"Error loading prompt template: {e}", exc_info=True)
        raise PromptTemplateError(
            f"Error loading prompt template: {str(e)}"
        ) from e


def format_prompt(
    issue_statement: str,
    generated_patch: str,
    ground_truth_patch: str,
    optional_notes: str = "",
    repo_url: Optional[str] = None
) -> str:
    """
    Format the prompt template with actual values.
    
    Args:
        issue_statement: The issue statement
        generated_patch: The generated patch content
        ground_truth_patch: The ground truth patch content
        optional_notes: Optional additional notes
        repo_url: Optional repository URL for context
        
    Returns:
        Formatted prompt string
        
    Raises:
        PromptTemplateError: If the template cannot be formatted
    """
    try:
        template = load_prompt_template()
        
        # Build optional notes section with repo URL if provided
        notes_section = optional_notes or ""
        if repo_url and repo_url.strip():
            repo_context = f"Repository URL: {repo_url.strip()}"
            if notes_section:
                notes_section = f"{repo_context}\n\n{notes_section}"
            else:
                notes_section = repo_context
        
        prompt = template.replace("{ISSUE_STATEMENT}", issue_statement)
        prompt = prompt.replace("{GENERATED_PATCH}", generated_patch)
        prompt = prompt.replace("{GROUND_TRUTH_PATCH}", ground_truth_patch)
        prompt = prompt.replace("{OPTIONAL_NOTES}", notes_section)
        
        logger.debug("Successfully formatted prompt")
        return prompt
    except PromptTemplateError:
        raise
    except Exception as e:
        logger.error(f"Error formatting prompt: {e}", exc_info=True)
        raise PromptTemplateError(f"Error formatting prompt: {str(e)}") from e

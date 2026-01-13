"""
Patch evaluation logic.
"""

import json
import logging
from typing import Tuple, Optional, Dict, Any

from .api.factory import get_api_client
from .utils.file_utils import read_patch_file, format_prompt
from .exceptions import ValidationError, APIError, PromptTemplateError
from .config import get_config

logger = logging.getLogger(__name__)


class PatchEvaluator:
    """Main class for evaluating patches."""
    
    def __init__(self):
        """Initialize the evaluator."""
        self.config = get_config()
        logger.debug("Initialized PatchEvaluator")
    
    def validate_inputs(
        self,
        api_key: str,
        issue_statement: str,
        ground_truth_file: Optional[str],
        generated_file: Optional[str]
    ) -> None:
        """
        Validate input parameters.
        
        Args:
            api_key: API key
            issue_statement: Issue statement
            ground_truth_file: Ground truth patch file
            generated_file: Generated patch file
            
        Raises:
            ValidationError: If validation fails
        """
        if not api_key or not api_key.strip():
            raise ValidationError("API key is required")
        
        if not issue_statement or not issue_statement.strip():
            raise ValidationError("Issue statement is required")
        
        if not ground_truth_file:
            raise ValidationError("Ground truth patch file is required")
        
        if not generated_file:
            raise ValidationError("Generated patch file is required")
    
    def read_patches(
        self,
        ground_truth_file: str,
        generated_file: str
    ) -> Tuple[str, str]:
        """
        Read patch files.
        
        Args:
            ground_truth_file: Path to ground truth patch file
            generated_file: Path to generated patch file
            
        Returns:
            Tuple of (ground_truth_patch, generated_patch)
            
        Raises:
            ValidationError: If files cannot be read
        """
        try:
            ground_truth_patch = read_patch_file(ground_truth_file)
            if not ground_truth_patch:
                raise ValidationError("Ground truth patch file is empty")
            
            generated_patch = read_patch_file(generated_file)
            if not generated_patch:
                raise ValidationError("Generated patch file is empty")
            
            logger.debug("Successfully read both patch files")
            return ground_truth_patch, generated_patch
        except Exception as e:
            logger.error(f"Error reading patch files: {e}", exc_info=True)
            raise ValidationError(f"Error reading patch files: {str(e)}") from e
    
    def evaluate(
        self,
        api_key: str,
        issue_statement: str,
        model_name: str,
        base_url: Optional[str],
        ground_truth_file: str,
        generated_file: str,
        optional_notes: str = "",
        repo_url: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Evaluate a generated patch against a ground truth patch.
        
        Args:
            api_key: API key for the LLM provider
            issue_statement: Description of the issue the patch should address
            model_name: Name of the model to use
            base_url: Optional custom base URL for the API
            ground_truth_file: Path to ground truth patch file
            generated_file: Path to generated patch file
            optional_notes: Optional additional notes or constraints
            repo_url: Optional repository URL for context
            
        Returns:
            Tuple of (result_json_string, error_message)
            If successful, error_message is None
        """
        try:
            # Validate inputs
            self.validate_inputs(
                api_key, issue_statement, ground_truth_file, generated_file
            )
            
            # Read patch files
            ground_truth_patch, generated_patch = self.read_patches(
                ground_truth_file, generated_file
            )
            
            # Format prompt
            try:
                prompt = format_prompt(
                    issue_statement=issue_statement,
                    generated_patch=generated_patch,
                    ground_truth_patch=ground_truth_patch,
                    optional_notes=optional_notes or "",
                    repo_url=repo_url
                )
            except PromptTemplateError as e:
                return "", str(e)
            
            # Get API client and make call
            try:
                api_client = get_api_client(model_name, api_key, base_url)
                result = api_client.call(
                    prompt=prompt,
                    model=model_name,
                    temperature=self.config.default_temperature,
                    max_tokens=self.config.max_tokens
                )
            except APIError as e:
                return "", str(e)
            
            # Parse and format result
            if not result or result.startswith("Error"):
                return "", result
            
            try:
                parsed = json.loads(result)
                formatted_result = json.dumps(parsed, indent=2)
                logger.info("Successfully evaluated patch")
                return formatted_result, None
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code block
                if "```json" in result:
                    start = result.find("```json") + 7
                    end = result.find("```", start)
                    if end > start:
                        try:
                            parsed = json.loads(result[start:end].strip())
                            formatted_result = json.dumps(parsed, indent=2)
                            logger.info("Successfully evaluated patch (extracted from markdown)")
                            return formatted_result, None
                        except json.JSONDecodeError:
                            pass
                
                logger.warning("API response is not valid JSON, returning raw response")
                return result, None
        
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return "", str(e)
        except Exception as e:
            logger.error(f"Unexpected error during evaluation: {e}", exc_info=True)
            return "", f"Unexpected error: {str(e)}"

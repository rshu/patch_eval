"""
Patch evaluation logic.
"""

import json
import logging
from typing import Tuple, Optional

from .api.factory import get_api_client
from .utils.file_utils import read_patch_file, format_prompt
from .exceptions import ValidationError, APIError, PromptTemplateError
from .config import get_config

logger = logging.getLogger(__name__)

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
        except ValidationError:
            raise
        except Exception as e:
            logger.error("Error reading patch files: %s", e, exc_info=True)
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
            if not result:
                return "", "No response received from API"
            
            if result.strip().startswith("Error"):
                return "", result
            
            try:
                parsed = json.loads(result)
                
                # Validate required fields in the response
                if not isinstance(parsed, dict):
                    raise ValueError("Response is not a JSON object")
                
                # Validate scores are in correct range
                if "scores" in parsed:
                    scores = parsed["scores"]
                    for score_name, score_value in scores.items():
                        if not isinstance(score_value, (int, float)):
                            logger.warning("Score %s is not a number: %s", score_name, score_value)
                        elif not (0 <= score_value <= 5):
                            logger.warning("Score %s out of range (0-5): %s", score_name, score_value)
                
                # Validate overall_score if present and verify calculation
                if "overall_score" in parsed and "scores" in parsed:
                    overall = parsed["overall_score"]
                    scores = parsed["scores"]
                    if not isinstance(overall, (int, float)):
                        logger.warning("Overall score is not a number: %s", overall)
                    elif not (0 <= overall <= 100):
                        logger.warning("Overall score out of range (0-100): %s", overall)
                    else:
                        # Verify overall_score matches expected calculation
                        a = scores.get("functional_correctness", 0)
                        b = scores.get("completeness_coverage", 0)
                        c = scores.get("equivalence_to_ground_truth", 0)
                        expected = round((a * 9) + (b * 7) + (c * 4))
                        if abs(overall - expected) > 1:  # Allow 1 point difference for rounding
                            logger.warning(
                                "Overall score mismatch: expected %d (from scores A=%.1f, B=%.1f, C=%.1f), got %s",
                                expected, a, b, c, overall
                            )
                
                formatted_result = json.dumps(parsed, indent=2)
                logger.info("Successfully evaluated patch")
                return formatted_result, None
            except json.JSONDecodeError as e:
                # Try to extract JSON from markdown code block
                if "```json" in result:
                    start = result.find("```json") + 7
                    end = result.find("```", start)
                    if end > start:
                        try:
                            json_content = result[start:end].strip()
                            parsed = json.loads(json_content)
                            formatted_result = json.dumps(parsed, indent=2)
                            logger.info("Successfully evaluated patch (extracted from markdown)")
                            return formatted_result, None
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse JSON from markdown code block")
                
                # Try to extract JSON object from text
                import re
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(0))
                        formatted_result = json.dumps(parsed, indent=2)
                        logger.info("Successfully evaluated patch (extracted JSON from text)")
                        return formatted_result, None
                    except json.JSONDecodeError:
                        pass
                
                logger.warning("API response is not valid JSON: %s", str(e))
                logger.debug("Response content (first 500 chars): %s", result[:500])
                return result, None
        
        except ValidationError as e:
            logger.error("Validation error: %s", e)
            return "", str(e)
        except (APIError, PromptTemplateError) as e:
            logger.error("Evaluation error: %s", e)
            return "", str(e)
        except Exception as e:
            logger.error("Unexpected error during evaluation: %s", e, exc_info=True)
            return "", f"Unexpected error: {str(e)}"

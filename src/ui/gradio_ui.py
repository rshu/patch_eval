"""
Gradio UI components for the patch evaluation tool.
"""

import json
import logging
import gradio as gr

from ..evaluator import PatchEvaluator
from ..utils.file_utils import read_patch_file
from ..config import get_config

logger = logging.getLogger(__name__)


def create_ui():
    """
    Create the Gradio interface.
    
    Returns:
        Gradio Blocks interface
    """
    config = get_config()
    evaluator = PatchEvaluator()
    
    with gr.Blocks(title="Patch Evaluation Tool", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🔍 Patch Evaluation Tool")
        gr.Markdown(
            "Compare a generated patch against a ground-truth patch using "
            "LLM-based evaluation."
        )
        
        # API Configuration Section
        with gr.Group():
            gr.Markdown("### 🔑 API Configuration")
            with gr.Row():
                api_key_input = gr.Textbox(
                    label="API Key",
                    type="password",
                    placeholder="Enter your API key",
                    info="OpenAI or Anthropic API key",
                    scale=3
                )
                
                base_url_input = gr.Textbox(
                    label="Base URL",
                    placeholder="https://api.openai.com/v1",
                    info="Optional: Custom API base URL",
                    scale=2
                )
                
                model_dropdown = gr.Dropdown(
                    choices=config.available_models,
                    value=config.default_model,
                    label="Model",
                    info="Select the LLM model to use",
                    scale=1
                )
        
        # Repository Information Section
        with gr.Group():
            gr.Markdown("### 📦 Repository Information")
            with gr.Row():
                repo_url_input = gr.Textbox(
                    label="Repository URL",
                    placeholder="https://github.com/user/repo",
                    info="Optional: Repository URL for context",
                    scale=2
                )
                
                repo_name_input = gr.Textbox(
                    label="Repository Name",
                    placeholder="user/repo",
                    info="Optional: Repository name (e.g., owner/repo)",
                    scale=1
                )
                
                pr_id_input = gr.Textbox(
                    label="PR ID",
                    placeholder="123",
                    info="Optional: Pull Request ID",
                    scale=1
                )
        
        # Issue Statement Section
        with gr.Group():
            gr.Markdown("### 📝 Issue Statement")
            issue_statement = gr.Textbox(
                label="PR Issue Statement",
                placeholder="Describe the issue or feature request that the patch addresses...",
                lines=5,
                info="The problem statement or requirement that the patches should address"
            )
        
        # Patch Uploads Section
        with gr.Group():
            gr.Markdown("### 📄 Patch Files")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Ground Truth Patch")
                    ground_truth_upload = gr.File(
                        label="Upload Ground Truth Patch",
                        file_types=config.supported_file_types,
                        type="filepath"
                    )
                    ground_truth_preview = gr.Textbox(
                        label="Preview",
                        lines=10,
                        interactive=False,
                        placeholder="Patch preview will appear here..."
                    )
                
                with gr.Column():
                    gr.Markdown("#### Generated Patch")
                    generated_upload = gr.File(
                        label="Upload Generated Patch",
                        file_types=config.supported_file_types,
                        type="filepath"
                    )
                    generated_preview = gr.Textbox(
                        label="Preview",
                        lines=10,
                        interactive=False,
                        placeholder="Patch preview will appear here..."
                    )
        
        # Optional Notes Section
        with gr.Group():
            gr.Markdown("### 📋 Additional Notes")
            optional_notes = gr.Textbox(
                label="Optional Notes / Constraints",
                placeholder="Any additional context, constraints, or notes...",
                lines=3,
                info="Optional: Additional information that might help the evaluation"
            )
        
        # Evaluate button
        evaluate_btn = gr.Button("Evaluate Patches", variant="primary", size="lg")
        
        # Results Section
        with gr.Group():
            gr.Markdown("### 📊 Evaluation Results")
            
            with gr.Row():
                result_output = gr.JSON(
                    label="Evaluation Result (JSON)",
                    visible=False
                )
            
            result_text = gr.Textbox(
                label="Evaluation Result",
                lines=20,
                interactive=False,
                placeholder="Evaluation results will appear here..."
            )
            
            # Download button for JSON result
            download_json_btn = gr.File(
                label="Download JSON Result",
                visible=False,
                interactive=False
            )
            
            error_output = gr.Textbox(
                label="Errors",
                visible=False,
                interactive=False
            )
        
        # Preview update functions
        def update_ground_truth_preview(file):
            """Update ground truth patch preview."""
            if file:
                try:
                    content = read_patch_file(file)
                    return content[:config.max_preview_size]
                except Exception as e:
                    logger.error(f"Error updating preview: {e}")
                    return f"Error: {str(e)}"
            return ""
        
        def update_generated_preview(file):
            """Update generated patch preview."""
            if file:
                try:
                    content = read_patch_file(file)
                    return content[:config.max_preview_size]
                except Exception as e:
                    logger.error(f"Error updating preview: {e}")
                    return f"Error: {str(e)}"
            return ""
        
        ground_truth_upload.change(
            fn=update_ground_truth_preview,
            inputs=[ground_truth_upload],
            outputs=[ground_truth_preview]
        )
        
        generated_upload.change(
            fn=update_generated_preview,
            inputs=[generated_upload],
            outputs=[generated_preview]
        )
        
        # Helper function to create downloadable JSON file
        def create_json_file(json_data, repo_name=None, pr_id=None):
            """Create a temporary JSON file for download."""
            import tempfile
            import re
            from datetime import datetime
            
            if json_data is None:
                return None
            
            try:
                # Build filename components
                filename_parts = ["patch_evaluation"]
                
                if repo_name and repo_name.strip():
                    # Sanitize repo name for filename (replace / and spaces with _)
                    safe_repo_name = re.sub(r'[^\w\-]', '_', repo_name.strip())
                    filename_parts.append(safe_repo_name)
                
                if pr_id and pr_id.strip():
                    # Sanitize PR ID for filename
                    safe_pr_id = re.sub(r'[^\w\-]', '_', pr_id.strip())
                    filename_parts.append(f"PR{safe_pr_id}")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename_parts.append(timestamp)
                
                prefix = "_".join(filename_parts) + "_"
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.json',
                    prefix=prefix,
                    delete=False
                )
                
                # Write JSON data
                if isinstance(json_data, str):
                    temp_file.write(json_data)
                else:
                    json.dump(json_data, temp_file, indent=2)
                
                temp_file.close()
                return temp_file.name
            except Exception as e:
                logger.error(f"Error creating JSON file: {e}")
                return None
        
        # Evaluation function
        def run_evaluation(api_key, repo_url, repo_name, pr_id, issue, model, base_url, gt_file, gen_file, notes):
            """Run patch evaluation."""
            result, error = evaluator.evaluate(
                api_key=api_key,
                issue_statement=issue,
                model_name=model,
                base_url=base_url,
                ground_truth_file=gt_file,
                generated_file=gen_file,
                optional_notes=notes or "",
                repo_url=repo_url
            )
            
            if error:
                return (
                    gr.update(value=None, visible=False),
                    gr.update(value="", visible=True),
                    gr.update(value=None, visible=False),
                    gr.update(value=error, visible=True)
                )
            
            # Try to parse as JSON for better display
            if result:
                try:
                    parsed = json.loads(result)
                    
                    # Add metadata to the result
                    if isinstance(parsed, dict):
                        metadata = {}
                        if repo_name and repo_name.strip():
                            metadata["repository_name"] = repo_name.strip()
                        if pr_id and pr_id.strip():
                            metadata["pr_id"] = pr_id.strip()
                        if repo_url and repo_url.strip():
                            metadata["repository_url"] = repo_url.strip()
                        
                        if metadata:
                            parsed["metadata"] = metadata
                            # Update the result string with metadata
                            result = json.dumps(parsed, indent=2)
                    
                    json_file = create_json_file(parsed, repo_name, pr_id)
                    return (
                        gr.update(value=parsed, visible=True),
                        gr.update(value=result, visible=False),
                        gr.update(value=json_file, visible=json_file is not None),
                        gr.update(value="", visible=False)
                    )
                except json.JSONDecodeError:
                    # If not valid JSON, still try to create file from raw result
                    json_file = create_json_file(result, repo_name, pr_id)
                    return (
                        gr.update(value=None, visible=False),
                        gr.update(value=result, visible=True),
                        gr.update(value=json_file, visible=json_file is not None),
                        gr.update(value="", visible=False)
                    )
            else:
                return (
                    gr.update(value=None, visible=False),
                    gr.update(value="No result returned", visible=True),
                    gr.update(value=None, visible=False),
                    gr.update(value="", visible=False)
                )
        
        evaluate_btn.click(
            fn=run_evaluation,
            inputs=[
                api_key_input,
                repo_url_input,
                repo_name_input,
                pr_id_input,
                issue_statement,
                model_dropdown,
                base_url_input,
                ground_truth_upload,
                generated_upload,
                optional_notes
            ],
            outputs=[
                result_output,
                result_text,
                download_json_btn,
                error_output
            ],
            show_progress=True
        )
        
        # Usage instructions
        gr.Markdown("""
        ### Usage Instructions
        1. Enter your API key (OpenAI or Anthropic)
        2. Optionally provide the repository URL
        3. Enter the PR issue statement describing what the patch should fix
        4. Select the model to use for evaluation
        5. Optionally provide a custom base URL for the API
        6. Upload both ground truth and generated patch files
        7. Optionally add any additional notes or constraints
        8. Click "Evaluate Patches" to get the comparison results
        
        The evaluation will score the generated patch on:
        - **Functional Correctness** (0-5): Does it fix the issue?
        - **Completeness & Coverage** (0-5): Does it handle all required updates?
        - **Behavioral Equivalence to Ground Truth** (0-5): How close is it to the ground truth?
        """)
    
    return demo

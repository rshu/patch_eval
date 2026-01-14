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
    
    # Custom theme with professional colors
    custom_theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
        neutral_hue="slate"
    )
    
    with gr.Blocks(title="Patch Evaluation Tool", theme=custom_theme) as demo:
        # Header with better styling
        gr.Markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="margin-bottom: 10px;">🔍 Patch Evaluation Tool</h1>
            <p style="color: #666; font-size: 1.1em;">Compare generated patches against ground-truth using LLM-based evaluation</p>
        </div>
        """)
        
        # API Configuration Section
        with gr.Accordion("🔑 API Configuration", open=True):
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
        with gr.Accordion("📦 Repository Information (Optional)", open=False):
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
        with gr.Accordion("📝 Issue Statement", open=True):
            issue_statement = gr.Textbox(
                label="PR Issue Statement",
                placeholder="Describe the issue or feature request that the patch addresses...",
                lines=5,
                info="The problem statement or requirement that the patches should address"
            )
        
        # Patch Uploads Section
        with gr.Accordion("📄 Patch Files", open=True):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### ✅ Ground Truth Patch")
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
                    gr.Markdown("### 🔄 Generated Patch")
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
        with gr.Accordion("📋 Additional Notes (Optional)", open=False):
            optional_notes = gr.Textbox(
                label="Optional Notes / Constraints",
                placeholder="Any additional context, constraints, or notes...",
                lines=3,
                info="Optional: Additional information that might help the evaluation"
            )
        
        # Action buttons row
        with gr.Row():
            evaluate_btn = gr.Button(
                "🚀 Evaluate Patches",
                variant="primary",
                size="lg",
                scale=2
            )
            clear_btn = gr.Button(
                "🗑️ Clear All",
                variant="secondary",
                size="lg",
                scale=1
            )
        
        # Results Section
        with gr.Accordion("📊 Evaluation Results", open=True):
            # Score cards row
            score_cards = gr.HTML(visible=False)
            
            # Main results display
            with gr.Tabs():
                with gr.Tab("📋 Summary"):
                    result_summary = gr.Markdown(
                        value="*Evaluation results will appear here after running an evaluation.*",
                        visible=True
                    )
                
                with gr.Tab("📄 Full JSON"):
                    result_output = gr.JSON(
                        label="Evaluation Result (JSON)",
                        visible=True
                    )
                
                with gr.Tab("📝 Raw Output"):
                    result_text = gr.Textbox(
                        label="Evaluation Result",
                        lines=20,
                        interactive=False,
                        placeholder="Evaluation results will appear here..."
                    )
            
            # Action buttons for results
            with gr.Row():
                download_json_btn = gr.File(
                    label="📥 Download JSON Result",
                    visible=False,
                    interactive=False,
                    scale=2
                )
                refresh_btn = gr.Button(
                    "🔄 Refresh View",
                    variant="secondary",
                    visible=False,
                    scale=1
                )
            
            # Error display
            error_output = gr.Textbox(
                label="❌ Errors",
                visible=False,
                interactive=False,
                lines=5
            )
        
        # Preview update functions
        def update_ground_truth_preview(file):
            """Update ground truth patch preview."""
            if file:
                try:
                    content = read_patch_file(file)
                    return content[:config.max_preview_size]
                except Exception as e:
                    logger.error("Error updating preview: %s", e)
                    return f"Error: {str(e)}"
            return ""
        
        def update_generated_preview(file):
            """Update generated patch preview."""
            if file:
                try:
                    content = read_patch_file(file)
                    return content[:config.max_preview_size]
                except Exception as e:
                    logger.error("Error updating preview: %s", e)
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
                logger.error("Error creating JSON file: %s", e)
                return None
        
        # Helper function to create score cards HTML
        def create_score_cards_html(parsed):
            """Create HTML for score cards display."""
            if not isinstance(parsed, dict) or "scores" not in parsed:
                return ""
            
            scores = parsed.get("scores", {})
            overall = parsed.get("overall_score", 0)
            verdict = parsed.get("verdict", "UNKNOWN")
            
            # Color mapping for verdicts
            verdict_colors = {
                "PASS": "#10b981",  # green
                "PARTIAL": "#f59e0b",  # amber
                "FAIL": "#ef4444"  # red
            }
            verdict_color = verdict_colors.get(verdict, "#6b7280")
            
            # Color mapping for scores (0-5)
            def get_score_color(score):
                if score >= 4:
                    return "#10b981"  # green
                elif score >= 3:
                    return "#f59e0b"  # amber
                elif score >= 2:
                    return "#f97316"  # orange
                else:
                    return "#ef4444"  # red
            
            func_score = scores.get("functional_correctness", 0)
            comp_score = scores.get("completeness_coverage", 0)
            equiv_score = scores.get("equivalence_to_ground_truth", 0)
            
            html = f"""
            <div style="margin: 20px 0;">
                <div style="display: flex; gap: 15px; flex-wrap: wrap; justify-content: center;">
                    <div style="background: linear-gradient(135deg, {verdict_color}15 0%, {verdict_color}05 100%); 
                                border: 2px solid {verdict_color}; border-radius: 12px; padding: 20px; 
                                min-width: 200px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 14px; color: #666; margin-bottom: 8px;">VERDICT</div>
                        <div style="font-size: 32px; font-weight: bold; color: {verdict_color}; margin-bottom: 4px;">{verdict}</div>
                        <div style="font-size: 18px; color: #666;">Overall: {overall}/100</div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, {get_score_color(func_score)}15 0%, {get_score_color(func_score)}05 100%); 
                                border: 2px solid {get_score_color(func_score)}; border-radius: 12px; padding: 20px; 
                                min-width: 180px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 14px; color: #666; margin-bottom: 8px;">FUNCTIONAL CORRECTNESS</div>
                        <div style="font-size: 36px; font-weight: bold; color: {get_score_color(func_score)}; margin-bottom: 4px;">{func_score}/5</div>
                        <div style="font-size: 12px; color: #666;">Weight: 45%</div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, {get_score_color(comp_score)}15 0%, {get_score_color(comp_score)}05 100%); 
                                border: 2px solid {get_score_color(comp_score)}; border-radius: 12px; padding: 20px; 
                                min-width: 180px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 14px; color: #666; margin-bottom: 8px;">COMPLETENESS & COVERAGE</div>
                        <div style="font-size: 36px; font-weight: bold; color: {get_score_color(comp_score)}; margin-bottom: 4px;">{comp_score}/5</div>
                        <div style="font-size: 12px; color: #666;">Weight: 35%</div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, {get_score_color(equiv_score)}15 0%, {get_score_color(equiv_score)}05 100%); 
                                border: 2px solid {get_score_color(equiv_score)}; border-radius: 12px; padding: 20px; 
                                min-width: 180px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 14px; color: #666; margin-bottom: 8px;">BEHAVIORAL EQUIVALENCE</div>
                        <div style="font-size: 36px; font-weight: bold; color: {get_score_color(equiv_score)}; margin-bottom: 4px;">{equiv_score}/5</div>
                        <div style="font-size: 12px; color: #666;">Weight: 20%</div>
                    </div>
                </div>
            </div>
            """
            return html
        
        # Helper function to create summary markdown
        def create_summary_markdown(parsed):
            """Create formatted markdown summary."""
            if not isinstance(parsed, dict):
                return "*Invalid result format*"
            
            verdict = parsed.get("verdict", "UNKNOWN")
            overall = parsed.get("overall_score", 0)
            summary = parsed.get("summary", "No summary available.")
            scores = parsed.get("scores", {})
            confidence = parsed.get("confidence", 0.0)
            
            verdict_emoji = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌"}.get(verdict, "❓")
            
            md = f"""
## {verdict_emoji} Verdict: **{verdict}** | Overall Score: **{overall}/100**

### Summary
{summary}

### Scores
- **Functional Correctness**: {scores.get('functional_correctness', 'N/A')}/5
- **Completeness & Coverage**: {scores.get('completeness_coverage', 'N/A')}/5
- **Behavioral Equivalence**: {scores.get('equivalence_to_ground_truth', 'N/A')}/5

### Confidence
Confidence Level: **{confidence:.1%}**

"""
            
            # Add key findings if available
            findings = parsed.get("key_findings", [])
            if findings:
                md += "### Key Findings\n\n"
                for finding in findings:
                    ftype = finding.get("type", "info")
                    detail = finding.get("detail", "")
                    emoji = {"strength": "✅", "weakness": "⚠️", "risk": "🔴"}.get(ftype, "ℹ️")
                    md += f"- {emoji} **{ftype.upper()}**: {detail}\n"
                md += "\n"
            
            return md
        
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
                    gr.update(value="", visible=False),  # score_cards
                    gr.update(value="", visible=False),  # result_summary
                    gr.update(value=None, visible=False),  # result_output
                    gr.update(value="", visible=False),  # result_text
                    gr.update(value=None, visible=False),  # download_json_btn
                    gr.update(visible=False),  # refresh_btn
                    gr.update(value=error, visible=True)  # error_output
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
                    
                    # Create formatted displays
                    score_cards_html = create_score_cards_html(parsed)
                    summary_md = create_summary_markdown(parsed)
                    json_file = create_json_file(parsed, repo_name, pr_id)
                    
                    return (
                        gr.update(value=score_cards_html, visible=True),  # score_cards
                        gr.update(value=summary_md, visible=True),  # result_summary
                        gr.update(value=parsed, visible=True),  # result_output
                        gr.update(value=result, visible=True),  # result_text
                        gr.update(value=json_file, visible=json_file is not None),  # download_json_btn
                        gr.update(visible=True),  # refresh_btn
                        gr.update(value="", visible=False)  # error_output
                    )
                except json.JSONDecodeError:
                    # If not valid JSON, still try to create file from raw result
                    json_file = create_json_file(result, repo_name, pr_id)
                    return (
                        gr.update(value="", visible=False),  # score_cards
                        gr.update(value="*Unable to parse JSON result. See Raw Output tab.*", visible=True),  # result_summary
                        gr.update(value=None, visible=False),  # result_output
                        gr.update(value=result, visible=True),  # result_text
                        gr.update(value=json_file, visible=json_file is not None),  # download_json_btn
                        gr.update(visible=True),  # refresh_btn
                        gr.update(value="", visible=False)  # error_output
                    )
            else:
                return (
                    gr.update(value="", visible=False),  # score_cards
                    gr.update(value="*No result returned from API.*", visible=True),  # result_summary
                    gr.update(value=None, visible=False),  # result_output
                    gr.update(value="No result returned", visible=True),  # result_text
                    gr.update(value=None, visible=False),  # download_json_btn
                    gr.update(visible=False),  # refresh_btn
                    gr.update(value="", visible=False)  # error_output
                )
        
        # Clear function
        def clear_all():
            """Clear all inputs and results."""
            return (
                "",  # api_key
                "",  # repo_url
                "",  # repo_name
                "",  # pr_id
                "",  # issue
                config.default_model,  # model
                "",  # base_url
                None,  # gt_file
                None,  # gen_file
                "",  # notes
                "",  # ground_truth_preview
                "",  # generated_preview
                "",  # score_cards
                "*Evaluation results will appear here after running an evaluation.*",  # result_summary
                None,  # result_output
                "",  # result_text
                None,  # download_json_btn
                gr.update(visible=False),  # refresh_btn
                ""  # error_output
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
                score_cards,
                result_summary,
                result_output,
                result_text,
                download_json_btn,
                refresh_btn,
                error_output
            ],
            show_progress=True
        )
        
        clear_btn.click(
            fn=clear_all,
            inputs=[],
            outputs=[
                api_key_input,
                repo_url_input,
                repo_name_input,
                pr_id_input,
                issue_statement,
                model_dropdown,
                base_url_input,
                ground_truth_upload,
                generated_upload,
                optional_notes,
                ground_truth_preview,
                generated_preview,
                score_cards,
                result_summary,
                result_output,
                result_text,
                download_json_btn,
                refresh_btn,
                error_output
            ]
        )
        
        def refresh_view():
            """Refresh the JSON view."""
            return gr.update()
        
        refresh_btn.click(
            fn=refresh_view,
            inputs=[],
            outputs=[result_output]
        )
        
        # Usage instructions
        with gr.Accordion("ℹ️ Usage Instructions & Information", open=False):
            gr.Markdown("""
            ### Quick Start Guide
            
            1. **Configure API**: Enter your API key (OpenAI or Anthropic) and select a model
            2. **Provide Context**: Enter the issue statement describing what the patch should fix
            3. **Upload Patches**: Upload both ground truth and generated patch files (.patch, .diff, or .txt)
            4. **Optional Settings**: Add repository information, notes, or custom API base URL if needed
            5. **Evaluate**: Click "🚀 Evaluate Patches" to run the evaluation
            
            ### Evaluation Criteria
            
            The tool evaluates patches on three key dimensions:
            
            - **Functional Correctness (0-5, 45% weight)**: Does the patch correctly address the root cause?
            - **Completeness & Coverage (0-5, 35% weight)**: Does it handle all required updates including tests?
            - **Behavioral Equivalence (0-5, 20% weight)**: How semantically similar is it to the ground truth?
            
            ### Score Interpretation
            
            - **0-1**: Unacceptable/Very Poor
            - **2**: Poor
            - **3**: Acceptable
            - **4**: Good
            - **5**: Excellent
            
            ### Verdicts
            
            - **PASS** ✅: All criteria meet high standards (A≥4, B≥4, C≥3) and overall_score≥70
            - **PARTIAL** ⚠️: Directionally correct but incomplete (A≥2, overall_score 31-69)
            - **FAIL** ❌: Fundamentally flawed (A≤1 or overall_score≤30)
            
            ### Tips
            
            - Use the preview feature to verify your patch files before evaluation
            - Provide detailed issue statements for better evaluation accuracy
            - Review the confidence score to understand evaluation reliability
            - Download JSON results for programmatic analysis
            """)
    
    return demo

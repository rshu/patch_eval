# Patch Evaluation Tool

An LLM-based application for comparing software patches. This tool evaluates a generated patch against a ground-truth patch across multiple dimensions including functional correctness, completeness, and behavioral equivalence.

## Features

- **Multi-model support**: Works with OpenAI (GPT-5.1, DeepSeek) and Anthropic (Claude) models
- **Comprehensive evaluation**: Scores patches on three key dimensions:
  - Functional Correctness (0-5)
  - Completeness & Coverage (0-5)
  - Behavioral Equivalence to Ground Truth (0-5)
- **User-friendly interface**: Simple Gradio-based web UI
- **Detailed analysis**: Provides structured JSON output with findings, differences, and recommendations
- **Professional architecture**: Modular design with proper separation of concerns
- **Logging**: Comprehensive logging for debugging and monitoring
- **Error handling**: Robust error handling with custom exceptions

## Project Structure

```
patch_eval/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── exceptions.py           # Custom exception classes
│   ├── evaluator.py            # Main evaluation logic
│   ├── api/                    # API client modules
│   │   ├── __init__.py
│   │   ├── base.py             # Base API client interface
│   │   ├── openai_client.py    # OpenAI API client
│   │   ├── anthropic_client.py # Anthropic API client
│   │   └── factory.py          # API client factory
│   ├── ui/                     # UI components
│   │   ├── __init__.py
│   │   └── gradio_ui.py        # Gradio interface
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── file_utils.py       # File operations
├── main.py                     # Main entry point
├── prompt_ref.txt              # Prompt template
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
└── README.md                   # This file
```

## Installation

### Option 1: Direct Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd patch_eval
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: Package Installation

```bash
pip install -e .
```

## Usage

### Starting the Application

1. Start the application:
```bash
python main.py
```

Or if installed as a package:
```bash
patch-eval
```

2. Open your browser and navigate to the URL shown (typically `http://127.0.0.1:7860`)

### Using the Interface

1. **Configuration**:
   - Enter your API key (OpenAI or Anthropic)
   - Optionally provide the repository URL
   - Select the model to use (gpt-5.1 or deepseek-v3-2)
   - Optionally provide a custom base URL for the API

2. **Input**:
   - Enter the PR issue statement describing what the patch should fix
   - Upload the ground truth patch file
   - Upload the generated patch file
   - Optionally add notes or constraints

3. **Evaluation**:
   - Click "Evaluate Patches" to get the comparison results

4. **Results**: Review the evaluation results, which include:
   - Overall verdict (PASS/PARTIAL/FAIL)
   - Detailed scores for each criterion
   - Key findings (strengths, weaknesses, risks)
   - Differences between patches
   - Recommended next steps

## Configuration

The application can be configured via environment variables:

- `SERVER_HOST`: Server host (default: `127.0.0.1`)
- `SERVER_PORT`: Server port (default: `7860`)
- `SHARE`: Enable Gradio sharing (default: `false`)
- `PROMPT_TEMPLATE_PATH`: Path to prompt template (default: `prompt_ref.txt`)

## File Format

Patch files should be in standard `.patch` or `.diff` format. The tool also accepts `.txt` files containing patch content.

## Evaluation Criteria

The tool evaluates patches based on the criteria defined in `prompt_ref.txt`:

- **Functional Correctness**: Does the patch correctly address the issue?
- **Completeness & Coverage**: Does it handle all required updates including tests?
- **Behavioral Equivalence**: How semantically similar is it to the ground truth?

## Development

### Running Tests

```bash
# Add tests when available
pytest
```

### Code Structure

The project follows a modular architecture:

- **API Clients** (`src/api/`): Abstracted API clients for different LLM providers
- **Evaluator** (`src/evaluator.py`): Core evaluation logic
- **UI** (`src/ui/`): Gradio interface components
- **Utils** (`src/utils/`): Utility functions for file operations
- **Config** (`src/config.py`): Configuration management

### Logging

The application logs to both console and `patch_eval.log` file. Log levels can be configured in `main.py`.

## Requirements

- Python 3.8+
- OpenAI API key OR Anthropic API key
- Dependencies listed in `requirements.txt`

## License

See LICENSE file for details.
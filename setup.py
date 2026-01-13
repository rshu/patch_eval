"""
Setup configuration for Patch Evaluation Tool.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="patch-eval",
    version="1.0.0",
    description="LLM-based application for comparing software patches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Patch Evaluation Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "gradio>=4.0.0",
        "openai>=1.0.0",
        "anthropic>=0.18.0",
    ],
    entry_points={
        "console_scripts": [
            "patch-eval=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

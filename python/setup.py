"""Setup script for cube-py."""

from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
readme = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="cube-py",
    version="1.1.0",
    description="Agent Cube CLI - Parallel LLM Coding Workflow Orchestrator",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Aetheron",
    url="https://github.com/aetheronhq/agent-cube",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "aiofiles>=23.0.0",
        "gitpython>=3.1.0",
        "typing-extensions>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cube-py=cube.cli:app",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)


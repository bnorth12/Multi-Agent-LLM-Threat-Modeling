"""
Pytest configuration for the test suite.
"""

import pathlib

import pytest
from dotenv import load_dotenv

# Load .env from the workspace root so GROK_API is available for llm_live tests
# regardless of how pytest is invoked (terminal, VS Code Test Explorer, CI).
load_dotenv(pathlib.Path(__file__).parent.parent / ".env", override=False)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "llm_live: marks tests that require a live LLM API key (excluded from CI with -m 'not llm_live')",
    )

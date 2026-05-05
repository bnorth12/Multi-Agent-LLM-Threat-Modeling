"""Base LLM adapter interface and fixture adapter."""

from __future__ import annotations

import json
from pathlib import Path


class LlmAdapter:
    """Abstract interface for LLM provider adapters."""

    def complete(self, system_prompt: str, user_message: str) -> str:
        raise NotImplementedError


class FixtureAdapter(LlmAdapter):
    """Returns a pre-recorded fixture response for the given agent stage.

    Used in automated tests and offline mode. No API key required.
    fixture_dir must contain files named ``agent_XX_output.json``.
    """

    def __init__(self, fixture_path: Path) -> None:
        self._fixture_path = fixture_path

    def complete(self, system_prompt: str, user_message: str) -> str:
        if not self._fixture_path.exists():
            raise FileNotFoundError(
                f"Fixture file not found: {self._fixture_path}"
            )
        return self._fixture_path.read_text(encoding="utf-8")

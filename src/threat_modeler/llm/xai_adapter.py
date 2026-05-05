"""xAI Grok LLM adapter using the OpenAI-compatible API endpoint."""

from __future__ import annotations

import os

from .base import LlmAdapter

_XAI_BASE_URL = "https://api.x.ai/v1"
_DEFAULT_MODEL = "grok-3-mini"


class XaiAdapter(LlmAdapter):
    """Calls the xAI Grok API using the OpenAI-compatible endpoint.

    API key is read from the ``GROK_API`` environment variable (repository secret).
    ``XAI_API_KEY`` is accepted as a local-development fallback.
    Never pass the key as a constructor argument.

    Usage::

        adapter = XaiAdapter()
        response = adapter.complete(system_prompt="...", user_message="...")
    """

    def __init__(self, model: str = _DEFAULT_MODEL) -> None:
        self._model = model

    def complete(self, system_prompt: str, user_message: str) -> str:
        api_key = os.environ.get("GROK_API") or os.environ.get("XAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROK_API environment variable is not set. "
                "Set GROK_API (or XAI_API_KEY for local dev) before using XaiAdapter "
                "or use FixtureAdapter for offline mode."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "The 'openai' package is required for XaiAdapter. "
                "Install it with: pip install openai"
            ) from exc

        client = OpenAI(api_key=api_key, base_url=_XAI_BASE_URL)
        response = client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""

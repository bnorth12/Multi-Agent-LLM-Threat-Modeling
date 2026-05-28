"""xAI Grok LLM adapter using the OpenAI-compatible API endpoint."""

from __future__ import annotations

from .base import LlmAdapter

_XAI_BASE_URL = "https://api.x.ai/v1"
_DEFAULT_MODEL = "grok-4"


class XaiAdapter(LlmAdapter):
    """Calls the xAI Grok API using the OpenAI-compatible endpoint.

    API key is supplied via constructor from run-scoped settings.

    Usage::

        adapter = XaiAdapter(api_key="...")
        response = adapter.complete(system_prompt="...", user_message="...")
    """

    def __init__(self, model: str = _DEFAULT_MODEL, api_key: str = "") -> None:
        self._model = model
        self._api_key = api_key.strip()

    def complete(self, system_prompt: str, user_message: str) -> str:
        if not self._api_key:
            raise EnvironmentError(
                "API key not found in run settings. Provide model.api_key before using XaiAdapter "
                "or use FixtureAdapter for offline mode."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "The 'openai' package is required for XaiAdapter. "
                "Install it with: pip install openai"
            ) from exc

        client = OpenAI(api_key=self._api_key, base_url=_XAI_BASE_URL)
        response = client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""

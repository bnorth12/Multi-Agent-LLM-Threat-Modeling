"""OpenAI-compatible adapter supporting completions and non-completions endpoints."""

from __future__ import annotations

import os
import json
from urllib import request
from urllib.error import HTTPError, URLError
from typing import Iterable

from .base import LlmAdapter


class OpenAiCompatibleAdapter(LlmAdapter):
    """Call an OpenAI-compatible API.

    Supports multiple endpoint styles so reasoning and multi-agent APIs that do
    not expose chat.completions can still be used.
    """

    def __init__(
        self,
        *,
        model: str,
        endpoint_mode: str = "chat_completions",
        base_url: str = "",
        api_key_env_candidates: Iterable[str] = (),
    ) -> None:
        self._model = model
        self._endpoint_mode = endpoint_mode
        self._base_url = base_url.strip()
        self._api_key_env_candidates = tuple(api_key_env_candidates)

    def _resolve_api_key(self) -> str:
        for name in self._api_key_env_candidates:
            value = os.environ.get(name, "").strip()
            if value:
                return value
        return ""

    def _post_json(self, path: str, payload: dict, api_key: str) -> dict:
        if not self._base_url:
            raise EnvironmentError(
                "No base URL configured for live provider. Set connection_url in Pipeline Configuration."
            )

        base = self._base_url.rstrip("/")
        url = f"{base}{path}"
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if exc.fp else str(exc)
            raise RuntimeError(f"Provider HTTP error {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Unable to reach provider endpoint: {exc.reason}") from exc

    def complete(self, system_prompt: str, user_message: str) -> str:
        api_key = self._resolve_api_key()
        if not api_key:
            joined = ", ".join(self._api_key_env_candidates) or "<no env vars configured>"
            raise EnvironmentError(f"API key not found. Set one of: {joined}")

        mode = self._endpoint_mode.lower().strip()
        if mode in ("responses", "multi_agent"):
            response = self._post_json(
                "/responses",
                {
                    "model": self._model,
                    "input": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                },
                api_key,
            )
            output_text = response.get("output_text", "")
            if output_text:
                return output_text

            # Fallback for response variants with nested content blocks.
            output = response.get("output", []) or []
            for item in output:
                content = item.get("content", []) or []
                for block in content:
                    text = block.get("text", "")
                    if text:
                        return text
            return ""

        response = self._post_json(
            "/chat/completions",
            {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            },
            api_key,
        )
        choices = response.get("choices", []) or []
        if not choices:
            return ""
        message = choices[0].get("message", {}) or {}
        return message.get("content", "") or ""

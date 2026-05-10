"""OpenAI-compatible adapter supporting completions and non-completions endpoints."""

from __future__ import annotations

import os
import json
import time
from urllib import request
from urllib.error import HTTPError, URLError
from typing import Iterable

from .base import LlmAdapter


DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_MAX_ATTEMPTS = 3


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
        timeout_seconds: int | None = None,
        max_attempts: int | None = None,
    ) -> None:
        self._model = model
        self._endpoint_mode = endpoint_mode
        self._base_url = base_url.strip()
        self._api_key_env_candidates = tuple(api_key_env_candidates)
        self._timeout_seconds = max(1, int(timeout_seconds)) if timeout_seconds is not None else None
        self._max_attempts = max(1, int(max_attempts)) if max_attempts is not None else None
        self._last_usage: dict[str, int | str] = {}

    @staticmethod
    def _coerce_positive_int(raw: str, default_value: int) -> int:
        try:
            return max(1, int(raw))
        except (TypeError, ValueError):
            return default_value

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

        last_error: Exception | None = None

        max_attempts = self._max_attempts
        if max_attempts is None:
            max_attempts = self._coerce_positive_int(
                os.environ.get("THREAT_MODELER_LLM_MAX_ATTEMPTS", str(DEFAULT_MAX_ATTEMPTS)),
                DEFAULT_MAX_ATTEMPTS,
            )

        timeout = self._timeout_seconds
        if timeout is None:
            timeout = self._coerce_positive_int(
                os.environ.get("THREAT_MODELER_LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)),
                DEFAULT_TIMEOUT_SECONDS,
            )

        for attempt in range(1, max_attempts + 1):
            try:
                with request.urlopen(req, timeout=timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace") if exc.fp else str(exc)
                retriable = exc.code in {429, 500, 502, 503, 504}
                last_error = RuntimeError(f"Provider HTTP error {exc.code}: {detail}")
                if not retriable or attempt == max_attempts:
                    raise last_error from exc
            except (URLError, TimeoutError) as exc:
                retriable = True
                last_error = exc
                if attempt == max_attempts:
                    if isinstance(exc, URLError):
                        raise RuntimeError(f"Unable to reach provider endpoint: {exc.reason}") from exc
                    raise RuntimeError(
                        f"Provider request timed out after {max_attempts} attempts "
                        f"(timeout={timeout}s, path={path}, model={self._model}, mode={self._endpoint_mode})"
                    ) from exc

            # Exponential backoff: 1s, 2s before final attempt.
            time.sleep(2 ** (attempt - 1))

        if last_error is not None:
            raise RuntimeError(f"Provider request failed: {last_error}") from last_error
        raise RuntimeError("Provider request failed with unknown error")

    @staticmethod
    def _normalise_usage(usage: dict) -> dict[str, int]:
        prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
        completion_tokens = int(usage.get("completion_tokens", 0) or 0)
        total_tokens = int(usage.get("total_tokens", 0) or 0)

        details = usage.get("completion_tokens_details", {}) or {}
        reasoning_tokens = int(details.get("reasoning_tokens", 0) or 0)

        prompt_details = usage.get("prompt_tokens_details", {}) or {}
        cached_tokens = int(prompt_details.get("cached_tokens", 0) or 0)

        if total_tokens <= 0:
            total_tokens = prompt_tokens + completion_tokens

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "reasoning_tokens": reasoning_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": total_tokens,
        }

    def usage_snapshot(self) -> dict[str, int | str]:
        return dict(self._last_usage)

    def complete(self, system_prompt: str, user_message: str) -> str:
        api_key = self._resolve_api_key()
        if not api_key:
            joined = ", ".join(self._api_key_env_candidates) or "<no env vars configured>"
            raise EnvironmentError(f"API key not found. Set one of: {joined}")

        mode = self._endpoint_mode.lower().strip()
        self._last_usage = {}
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
            usage = response.get("usage", {}) or {}
            self._last_usage = {
                "provider": "openai-compatible",
                "endpoint_mode": mode,
                "model": self._model,
                **self._normalise_usage(usage),
            }
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
        usage = response.get("usage", {}) or {}
        self._last_usage = {
            "provider": "openai-compatible",
            "endpoint_mode": mode,
            "model": self._model,
            **self._normalise_usage(usage),
        }
        choices = response.get("choices", []) or []
        if not choices:
            return ""
        message = choices[0].get("message", {}) or {}
        return message.get("content", "") or ""

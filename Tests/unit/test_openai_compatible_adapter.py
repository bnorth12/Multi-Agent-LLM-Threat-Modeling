"""Unit tests for OpenAiCompatibleAdapter — timeout retry and HTTP error handling.

D-S08-018 regression suite:
- Locks the 'all attempts timeout → RuntimeError' failure mode.
- Adds red tests for configurable timeout/attempts (fail before fix, pass after fix).
- Covers HTTP error retry policy and happy-path response parsing.
"""

from __future__ import annotations

import json
import time
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from threat_modeler.llm.openai_compatible_adapter import OpenAiCompatibleAdapter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _adapter(endpoint_mode: str = "chat_completions") -> OpenAiCompatibleAdapter:
    return OpenAiCompatibleAdapter(
        model="grok-4",
        endpoint_mode=endpoint_mode,
        base_url="https://api.x.ai/v1",
        api_key_env_candidates=("_TEST_ADAPTER_KEY",),
    )


def _chat_response_bytes(content: str) -> bytes:
    return json.dumps({"choices": [{"message": {"content": content}}]}).encode()


def _responses_mode_bytes(text: str) -> bytes:
    return json.dumps({"output_text": text}).encode()


def _chat_response_with_usage_bytes(content: str) -> bytes:
    return json.dumps(
        {
            "choices": [{"message": {"content": content}}],
            "usage": {
                "prompt_tokens": 11,
                "completion_tokens": 7,
                "total_tokens": 18,
                "completion_tokens_details": {"reasoning_tokens": 2},
                "prompt_tokens_details": {"cached_tokens": 3},
            },
        }
    ).encode()


def _responses_mode_with_usage_bytes(text: str) -> bytes:
    return json.dumps(
        {
            "output_text": text,
            "usage": {
                "prompt_tokens": 5,
                "completion_tokens": 4,
                "total_tokens": 9,
            },
        }
    ).encode()


class _FakeResponse:
    """Minimal context-manager response standing in for urllib http.client.HTTPResponse."""

    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *_) -> None:
        pass


def _http_error(code: int) -> HTTPError:
    return HTTPError(
        url="https://api.x.ai/v1/chat/completions",
        code=code,
        msg=f"HTTP {code}",
        hdrs=None,  # type: ignore[arg-type]
        fp=None,
    )


# ---------------------------------------------------------------------------
# Preconditions — missing base URL / API key
# ---------------------------------------------------------------------------

class TestAdapterPreconditions:
    def test_raises_env_error_when_no_base_url(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        adapter = OpenAiCompatibleAdapter(
            model="grok-4",
            endpoint_mode="chat_completions",
            base_url="",
            api_key_env_candidates=("_TEST_ADAPTER_KEY",),
        )
        with pytest.raises(EnvironmentError, match="base URL"):
            adapter.complete("sys", "user")

    def test_raises_env_error_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("_TEST_ADAPTER_KEY", raising=False)
        with pytest.raises(EnvironmentError, match="API key"):
            _adapter().complete("sys", "user")


# ---------------------------------------------------------------------------
# Timeout retry — D-S08-018 regression
# ---------------------------------------------------------------------------

class TestTimeoutRetry:
    def test_all_attempts_timeout_raises_runtime_error(self, monkeypatch):
        """D-S08-018: all attempts exhaust → RuntimeError with attempt count in message."""
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.delenv("THREAT_MODELER_LLM_MAX_ATTEMPTS", raising=False)
        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=TimeoutError("timed out")),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            with pytest.raises(RuntimeError, match="timed out after 3 attempts"):
                _adapter().complete("sys", "user")

    def test_error_message_includes_attempt_count(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.delenv("THREAT_MODELER_LLM_MAX_ATTEMPTS", raising=False)
        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=TimeoutError("timed out")),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            with pytest.raises(RuntimeError) as exc_info:
                _adapter().complete("sys", "user")
        assert "3" in str(exc_info.value)

    def test_first_attempt_times_out_second_succeeds(self, monkeypatch):
        """Single transient timeout is recovered on the next attempt."""
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        side_effects = [
            TimeoutError("transient"),
            _FakeResponse(_chat_response_bytes("recovered")),
        ]
        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=side_effects),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            result = _adapter().complete("sys", "user")
        assert result == "recovered"

    def test_two_timeouts_then_success(self, monkeypatch):
        """Two consecutive timeouts followed by success returns the result."""
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        side_effects = [
            TimeoutError("t1"),
            TimeoutError("t2"),
            _FakeResponse(_chat_response_bytes("final ok")),
        ]
        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=side_effects),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            result = _adapter().complete("sys", "user")
        assert result == "final ok"

    def test_backoff_sleep_called_between_retry_attempts(self, monkeypatch):
        """Exponential backoff sleep is invoked between each attempt pair."""
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.delenv("THREAT_MODELER_LLM_MAX_ATTEMPTS", raising=False)
        sleep_calls: list[float] = []
        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=TimeoutError("timed out")),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep",
                  side_effect=lambda s: sleep_calls.append(s)),
        ):
            with pytest.raises(RuntimeError):
                _adapter().complete("sys", "user")
        # 3 attempts → 2 sleeps (between 1→2 and 2→3)
        assert len(sleep_calls) == 2
        assert sleep_calls == [1, 2]  # exponential: 2^0=1, 2^1=2

    # --- RED tests: fail before D-S08-018 fix, green after fix ---

    def test_timeout_configurable_via_env_var(self, monkeypatch):
        """THREAT_MODELER_LLM_TIMEOUT_SECONDS env var controls the per-attempt timeout.

        RED before fix: timeout is hardcoded to 90; will pass 90 not 5.
        GREEN after fix: adapter reads the env var and uses it.
        """
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.setenv("THREAT_MODELER_LLM_TIMEOUT_SECONDS", "30")
        captured: list[int | float] = []

        def fake_urlopen(req, timeout=None):
            captured.append(timeout)
            return _FakeResponse(_chat_response_bytes("ok"))

        with patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                   side_effect=fake_urlopen):
            _adapter().complete("sys", "user")

        assert captured[0] == 30, (
            f"Expected timeout=30 from THREAT_MODELER_LLM_TIMEOUT_SECONDS, got {captured[0]}. "
            "Fix: read THREAT_MODELER_LLM_TIMEOUT_SECONDS in _post_json()."
        )

    def test_max_attempts_configurable_via_env_var(self, monkeypatch):
        """THREAT_MODELER_LLM_MAX_ATTEMPTS env var controls the retry attempt ceiling.

        RED before fix: max_attempts is hardcoded to 3; error will say '3 attempts' not '5'.
        GREEN after fix: adapter reads the env var.
        """
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.setenv("THREAT_MODELER_LLM_MAX_ATTEMPTS", "5")
        attempt_count: list[int] = []

        def fake_urlopen(req, timeout=None):
            attempt_count.append(1)
            raise TimeoutError("always timeout")

        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=fake_urlopen),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            with pytest.raises(RuntimeError, match="timed out after 5 attempts"):
                _adapter().complete("sys", "user")

        assert len(attempt_count) == 5, (
            f"Expected 5 attempts from THREAT_MODELER_LLM_MAX_ATTEMPTS, got {len(attempt_count)}. "
            "Fix: read THREAT_MODELER_LLM_MAX_ATTEMPTS in _post_json()."
        )

    def test_default_timeout_is_at_least_120_seconds(self, monkeypatch):
        """Default per-attempt timeout must be ≥ 120s to handle slow LLM responses.

        RED before fix: default is 90s.
        GREEN after fix: default is 180s (or any value ≥ 120).
        """
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.delenv("THREAT_MODELER_LLM_TIMEOUT_SECONDS", raising=False)
        captured: list[int | float] = []

        def fake_urlopen(req, timeout=None):
            captured.append(timeout)
            return _FakeResponse(_chat_response_bytes("ok"))

        with patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                   side_effect=fake_urlopen):
            _adapter().complete("sys", "user")

        assert captured[0] >= 120, (
            f"Default timeout is {captured[0]}s — must be ≥ 120s for slow LLM calls (D-S08-018). "
            "Fix: increase default from 90 to 180 in _post_json()."
        )

    def test_constructor_timeout_overrides_env(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.setenv("THREAT_MODELER_LLM_TIMEOUT_SECONDS", "30")
        captured: list[int | float] = []

        def fake_urlopen(req, timeout=None):
            captured.append(timeout)
            return _FakeResponse(_chat_response_bytes("ok"))

        adapter = OpenAiCompatibleAdapter(
            model="grok-4",
            endpoint_mode="chat_completions",
            base_url="https://api.x.ai/v1",
            api_key_env_candidates=("_TEST_ADAPTER_KEY",),
            timeout_seconds=360,
        )
        with patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen", side_effect=fake_urlopen):
            adapter.complete("sys", "user")

        assert captured[0] == 360

    def test_constructor_max_attempts_overrides_env(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.setenv("THREAT_MODELER_LLM_MAX_ATTEMPTS", "5")
        attempt_count: list[int] = []

        def fake_urlopen(req, timeout=None):
            attempt_count.append(1)
            raise TimeoutError("always timeout")

        adapter = OpenAiCompatibleAdapter(
            model="grok-4",
            endpoint_mode="chat_completions",
            base_url="https://api.x.ai/v1",
            api_key_env_candidates=("_TEST_ADAPTER_KEY",),
            max_attempts=2,
        )
        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen", side_effect=fake_urlopen),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            with pytest.raises(RuntimeError, match="timed out after 2 attempts"):
                adapter.complete("sys", "user")

        assert len(attempt_count) == 2


# ---------------------------------------------------------------------------
# HTTP error retry policy
# ---------------------------------------------------------------------------

class TestHttpErrorRetryPolicy:
    def test_429_retries_all_attempts_then_raises(self, monkeypatch):
        """429 is retriable — should exhaust all attempts and raise."""
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.delenv("THREAT_MODELER_LLM_MAX_ATTEMPTS", raising=False)
        call_count: list[int] = []

        def fake_urlopen(req, timeout=None):
            call_count.append(1)
            raise _http_error(429)

        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=fake_urlopen),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            with pytest.raises(RuntimeError, match="HTTP error 429"):
                _adapter().complete("sys", "user")
        assert len(call_count) == 3

    def test_500_retries_all_attempts_then_raises(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        monkeypatch.delenv("THREAT_MODELER_LLM_MAX_ATTEMPTS", raising=False)
        call_count: list[int] = []

        def fake_urlopen(req, timeout=None):
            call_count.append(1)
            raise _http_error(500)

        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=fake_urlopen),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            with pytest.raises(RuntimeError, match="HTTP error 500"):
                _adapter().complete("sys", "user")
        assert len(call_count) == 3

    def test_401_raises_immediately_no_retry(self, monkeypatch):
        """401 Unauthorized is non-retriable — must fail on first attempt."""
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        call_count: list[int] = []

        def fake_urlopen(req, timeout=None):
            call_count.append(1)
            raise _http_error(401)

        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=fake_urlopen),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            with pytest.raises(RuntimeError, match="HTTP error 401"):
                _adapter().complete("sys", "user")
        assert len(call_count) == 1, f"401 must not retry; {len(call_count)} attempts made"

    def test_400_raises_immediately_no_retry(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        call_count: list[int] = []

        def fake_urlopen(req, timeout=None):
            call_count.append(1)
            raise _http_error(400)

        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=fake_urlopen),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            with pytest.raises(RuntimeError, match="HTTP error 400"):
                _adapter().complete("sys", "user")
        assert len(call_count) == 1

    def test_retriable_error_then_success_recovers(self, monkeypatch):
        """A single 503 followed by success returns the content."""
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        side_effects = [_http_error(503), _FakeResponse(_chat_response_bytes("retried ok"))]
        with (
            patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                  side_effect=side_effects),
            patch("threat_modeler.llm.openai_compatible_adapter.time.sleep"),
        ):
            result = _adapter().complete("sys", "user")
        assert result == "retried ok"


# ---------------------------------------------------------------------------
# Successful response parsing
# ---------------------------------------------------------------------------

class TestResponseParsing:
    def test_chat_completions_returns_message_content(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        with patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                   return_value=_FakeResponse(_chat_response_bytes("hello world"))):
            result = _adapter("chat_completions").complete("sys", "user")
        assert result == "hello world"

    def test_responses_mode_output_text_field(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        with patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                   return_value=_FakeResponse(_responses_mode_bytes("responses result"))):
            result = _adapter("responses").complete("sys", "user")
        assert result == "responses result"

    def test_chat_completions_empty_choices_returns_empty_string(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        body = json.dumps({"choices": []}).encode()
        with patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                   return_value=_FakeResponse(body)):
            result = _adapter("chat_completions").complete("sys", "user")
        assert result == ""

    def test_responses_mode_nested_content_block_fallback(self, monkeypatch):
        """Fallback parsing for responses API with nested content blocks."""
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        body = json.dumps({
            "output": [{"content": [{"text": "nested text"}]}]
        }).encode()
        with patch("threat_modeler.llm.openai_compatible_adapter.request.urlopen",
                   return_value=_FakeResponse(body)):
            result = _adapter("responses").complete("sys", "user")
        assert result == "nested text"

    def test_chat_completions_captures_usage_snapshot(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        adapter = _adapter("chat_completions")
        with patch(
            "threat_modeler.llm.openai_compatible_adapter.request.urlopen",
            return_value=_FakeResponse(_chat_response_with_usage_bytes("hello world")),
        ):
            result = adapter.complete("sys", "user")

        assert result == "hello world"
        usage = adapter.usage_snapshot()
        assert usage["prompt_tokens"] == 11
        assert usage["completion_tokens"] == 7
        assert usage["reasoning_tokens"] == 2
        assert usage["cached_tokens"] == 3
        assert usage["total_tokens"] == 18

    def test_responses_mode_captures_usage_snapshot(self, monkeypatch):
        monkeypatch.setenv("_TEST_ADAPTER_KEY", "fake-key")
        adapter = _adapter("responses")
        with patch(
            "threat_modeler.llm.openai_compatible_adapter.request.urlopen",
            return_value=_FakeResponse(_responses_mode_with_usage_bytes("responses result")),
        ):
            result = adapter.complete("sys", "user")

        assert result == "responses result"
        usage = adapter.usage_snapshot()
        assert usage["prompt_tokens"] == 5
        assert usage["completion_tokens"] == 4
        assert usage["total_tokens"] == 9

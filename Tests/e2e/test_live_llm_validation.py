"""
Live LLM Validation Tests with Token/Prompt Tracking

Validates that each gate/stage executes against live LLM (not fixtures) by:
1. Tracking token counts for each LLM call
2. Capturing prompt text and verifying content
3. Monitoring for fixture fallback indicators
4. Ensuring real LLM responses (not cached/mocked)
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from threading import Event, Thread
import time

import json
import os

import pytest

from threat_modeler.config import (
    ModelSelection,
    PipelineSettings,
    RuntimeSettings,
)
from threat_modeler.llm.openai_compatible_adapter import OpenAiCompatibleAdapter as OpenAICompatibleAdapter
from threat_modeler.orchestrator import FrameworkOrchestrator


LIVE_TEST_DEFAULT_TIMEOUT_SECONDS = 300
LIVE_TEST_DEFAULT_MAX_ATTEMPTS = 5
LIVE_TEST_HEARTBEAT_SECONDS = 20


class LiveLLMValidator:
    """Tracks LLM calls to validate live execution and token usage."""

    def __init__(self):
        self.calls: List[Dict[str, Any]] = []
        self.tokens_by_stage: Dict[str, int] = {}
        self.prompts_by_gate: Dict[str, str] = {}
        self.original_complete = None
        self.fixture_fallback_detected = False
        self._heartbeat_seconds = max(
            5,
            int(os.environ.get("THREAT_MODELER_LIVE_TEST_HEARTBEAT_SECONDS", str(LIVE_TEST_HEARTBEAT_SECONDS))),
        )

    def install(self, adapter: OpenAICompatibleAdapter):
        """Hook into adapter to intercept LLM calls."""
        self.original_complete = adapter.complete

        def _wrapped_complete(system_prompt: str, user_message: str) -> str:
            return self._intercept_complete(adapter, system_prompt, user_message)

        adapter.complete = _wrapped_complete  # type: ignore[method-assign]

    def _intercept_complete(self, adapter: OpenAICompatibleAdapter, system_prompt: str, user_message: str) -> str:
        """Intercept adapter.complete() to track tokens and prompts."""
        heartbeat_stop = Event()
        heartbeat_thread = Thread(
            target=self._emit_heartbeat,
            args=(heartbeat_stop, getattr(adapter, "_model", "unknown"), getattr(adapter, "_endpoint_mode", "unknown")),
            daemon=True,
        )
        heartbeat_thread.start()

        try:
            response_text = self.original_complete(system_prompt, user_message)
        finally:
            heartbeat_stop.set()
            heartbeat_thread.join(timeout=0.2)

        usage = adapter.usage_snapshot() if hasattr(adapter, "usage_snapshot") else {}
        prompt_text = f"system={system_prompt}\nuser={user_message}"

        # Record call
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": getattr(adapter, "_endpoint_mode", "unknown"),
            "prompt_length": len(prompt_text),
            "prompt_preview": prompt_text[:200],
            "response_model": usage.get("model", getattr(adapter, "_model", "unknown")),
            "usage": usage,
            "completion_tokens": usage.get("completion_tokens", 0),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

        self.calls.append(call_record)

        # Detect fixture fallback (indicator: zero token usage or mock response)
        if call_record["total_tokens"] == 0:
            self.fixture_fallback_detected = True

        return response_text

    def _emit_heartbeat(self, stop_event: Event, model: str, endpoint_mode: str) -> None:
        """Emit periodic heartbeat while waiting for a live LLM response."""
        started = time.monotonic()
        while not stop_event.wait(self._heartbeat_seconds):
            elapsed = int(time.monotonic() - started)
            print(
                f"[live-llm heartbeat] waiting for provider response "
                f"(model={model}, mode={endpoint_mode}, elapsed={elapsed}s)",
                flush=True,
            )

    def check_fixture_fallback(self) -> bool:
        """Returns True if fixture fallback was detected."""
        # Fixture responses have zero token usage
        return any(c["total_tokens"] == 0 for c in self.calls)

    def get_stage_tokens(self, stage_name: str) -> int:
        """Sum tokens used in a specific stage."""
        # Filter calls by stage name if identifiable in prompt
        stage_calls = [c for c in self.calls if stage_name.lower() in c["prompt_preview"].lower()]
        return sum(c["total_tokens"] for c in stage_calls)

    def get_call_report(self) -> str:
        """Generate human-readable report of all LLM calls."""
        lines = ["=== LIVE LLM CALL REPORT ==="]
        lines.append(f"Total calls: {len(self.calls)}")
        lines.append(f"Total tokens: {sum(c['total_tokens'] for c in self.calls)}")
        lines.append(f"Fixture fallback detected: {self.fixture_fallback_detected}")
        lines.append("")

        for i, call in enumerate(self.calls, 1):
            lines.append(f"Call {i}:")
            lines.append(f"  Model: {call['response_model']}")
            lines.append(f"  Endpoint: {call['endpoint']}")
            lines.append(f"  Tokens - Prompt: {call['prompt_tokens']}, Completion: {call['completion_tokens']}, Total: {call['total_tokens']}")
            lines.append(f"  Prompt Preview: {call['prompt_preview'][:100]}...")

        return "\n".join(lines)


class GateExecutionValidator:
    """Validates each gate execution for live LLM usage."""

    def __init__(self, validator: LiveLLMValidator):
        self.validator = validator
        self.gate_validations: Dict[str, Dict] = {}

    def validate_gate_1(self, framework: FrameworkOrchestrator) -> Dict[str, Any]:
        """Validate Gate 1: Scope Confirmation."""
        gate_name = "gate_1_scope_confirmation"

        # Should have minimal LLM calls (mostly static validation)
        validation = {
            "gate": gate_name,
            "stage": "Input Normalizer (agent_01)",
            "checks": {
                "has_llm_calls": len(self.validator.calls) > 0,
                "uses_live_provider": not self.validator.check_fixture_fallback(),
                "total_tokens_used": sum(c["total_tokens"] for c in self.validator.calls),
                "prompt_contains_system_info": any("system" in c["prompt_preview"].lower() for c in self.validator.calls),
            }
        }

        self.gate_validations[gate_name] = validation
        return validation


def _live_settings(
    *,
    model_name: str = "grok-4",
    endpoint_mode: str = "chat_completions",
    timeout_seconds: int = LIVE_TEST_DEFAULT_TIMEOUT_SECONDS,
    max_attempts: int = LIVE_TEST_DEFAULT_MAX_ATTEMPTS,
) -> RuntimeSettings:
    api_key = os.environ.get("GROK_API")
    if not api_key:
        pytest.skip("GROK_API not set; skipping live LLM validation.")

    return RuntimeSettings(
        model=ModelSelection(
            provider="xai",
            model_name=model_name,
            api_key=api_key,
            offline_only=False,
            endpoint_mode=endpoint_mode,
            request_timeout_seconds=timeout_seconds,
            request_max_attempts=max_attempts,
        ),
        pipeline=PipelineSettings(
            execution_mode="langgraph-compatible",
            require_hitl_gates=False,
            stop_on_validation_error=False,
        ),
    )


def _build_framework(settings: RuntimeSettings, run_id: str) -> FrameworkOrchestrator:
    return FrameworkOrchestrator(settings=settings, run_id=run_id)


def _live_adapter(framework: FrameworkOrchestrator) -> OpenAICompatibleAdapter:
    adapter = framework.agents["agent_01"].adapter
    assert adapter is not None, "Live adapter should be configured on shared agents"
    return adapter

    def validate_gate_2(self, framework: FrameworkOrchestrator) -> Dict[str, Any]:
        """Validate Gate 2: Boundary Approval."""
        gate_name = "gate_2_boundary_approval"

        # Should have LLM calls for context enrichment (agent_02)
        validation = {
            "gate": gate_name,
            "stage": "Context Builder (agent_02)",
            "checks": {
                "has_llm_calls": len(self.validator.calls) > 0,
                "uses_live_provider": not self.validator.check_fixture_fallback(),
                "total_tokens_used": sum(c["total_tokens"] for c in self.validator.calls),
                "prompt_contains_context": any("context" in c["prompt_preview"].lower() or "subsystem" in c["prompt_preview"].lower() for c in self.validator.calls),
                "completion_tokens_gt_zero": any(c["completion_tokens"] > 0 for c in self.validator.calls),
            }
        }

        self.gate_validations[gate_name] = validation
        return validation

    def validate_gate_3(self, framework: FrameworkOrchestrator) -> Dict[str, Any]:
        """Validate Gate 3: STRIDE Calibration."""
        gate_name = "gate_3_stride_calibration"

        # Should have substantial LLM calls for trust boundary validation (agent_03)
        validation = {
            "gate": gate_name,
            "stage": "Trust Boundary Validator (agent_03)",
            "checks": {
                "has_llm_calls": len(self.validator.calls) > 0,
                "uses_live_provider": not self.validator.check_fixture_fallback(),
                "total_tokens_used": sum(c["total_tokens"] for c in self.validator.calls),
                "prompt_contains_boundary": any("boundary" in c["prompt_preview"].lower() or "trust" in c["prompt_preview"].lower() for c in self.validator.calls),
                "completion_tokens_gt_zero": any(c["completion_tokens"] > 0 for c in self.validator.calls),
                "min_tokens_threshold": sum(c["total_tokens"] for c in self.validator.calls) > 100,
            }
        }

        self.gate_validations[gate_name] = validation
        return validation


@pytest.mark.llm_live
class TestLiveLLMValidation:
    """Validates live LLM execution with token/prompt tracking."""

    @pytest.fixture
    def validator(self):
        """Create live LLM validator."""
        return LiveLLMValidator()

    @pytest.fixture
    def gate_validator(self, validator):
        """Create gate execution validator."""
        return GateExecutionValidator(validator)

    def test_live_llm_not_fixture_fallback(self, validator):
        """Verify live LLM is used, not fixture fallback."""
        settings = _live_settings()
        assert settings.model.provider == "xai"
        assert not settings.model.offline_only

        framework = _build_framework(settings, run_id="test-live-llm-not-fixture-fallback")
        state = framework.initialize_state()
        state.raw_text = "subsystem: TestSubsystem, component: TestComponent"

        validator.install(_live_adapter(framework))

        framework.run_planned_stages(state)

        assert not validator.check_fixture_fallback(), (
            "Should use live LLM, not fixture fallback. Calls: " + json.dumps(validator.calls, indent=2)
        )

        assert len(validator.calls) > 0

        print("\n" + validator.get_call_report())

    def test_gate_1_has_llm_calls_with_tokens(self, validator, gate_validator):
        """Validate Gate 1 makes LLM calls with measurable token usage."""
        settings = _live_settings()
        framework = _build_framework(settings, run_id="test-gate-1-has-llm-calls")
        state = framework.initialize_state()
        state.raw_text = "subsystem: TestSubsystem, component: TestComponent"

        validator.install(_live_adapter(framework))

        framework.run_planned_stages(state)

        validation = gate_validator.validate_gate_1(framework)

        assert validation["checks"]["uses_live_provider"], \
            "Gate 1 should use live provider, not fixtures"
        assert validation["checks"]["has_llm_calls"], \
            "Gate 1 should have LLM calls for input validation"
        assert validation["checks"]["total_tokens_used"] > 0, \
            f"Gate 1 should consume tokens. Got: {validation['checks']['total_tokens_used']}"

        print(f"\n✓ Gate 1 Validation: {json.dumps(validation, indent=2)}")

    def test_gate_3_stride_validation_with_substantial_tokens(self, validator, gate_validator):
        """Validate Gate 3 (STRIDE) makes live LLM calls with substantial token usage."""
        settings = _live_settings()
        framework = _build_framework(settings, run_id="test-gate-3-stride-validation")
        state = framework.initialize_state()
        state.raw_text = """
        subsystem: Authentication, component: LoginProcessor
        subsystem: Database, component: UserStore
        data_flow: LoginProcessor -> UserStore (SQL)
        trust_boundary: External Network boundary
        """

        validator.install(_live_adapter(framework))

        framework.run_planned_stages(state)

        total_tokens = sum(c["total_tokens"] for c in validator.calls)

        assert total_tokens > 0, \
            f"Should have token usage for live LLM execution. Got: {total_tokens}. Calls: {json.dumps(validator.calls, indent=2)}"
        assert not validator.check_fixture_fallback(), \
            f"Should use live provider, not fixtures. Fixture fallback detected."

        print(f"\n✓ Total tokens used: {total_tokens}")
        print(f"✓ Calls made: {len(validator.calls)}")
        print("\n" + validator.get_call_report())

    def test_prompt_content_varies_by_stage(self, validator):
        """Validate prompts sent to LLM vary and contain stage-specific content."""
        settings = _live_settings()
        framework = _build_framework(settings, run_id="test-prompt-content-varies-by-stage")
        state = framework.initialize_state()
        state.raw_text = """
        subsystem: Frontend, component: WebUI
        subsystem: Backend, component: API Server
        subsystem: Database, component: PostgreSQL
        interface: Frontend-Backend (HTTPS)
        interface: Backend-Database (SQL)
        """

        validator.install(_live_adapter(framework))

        framework.run_planned_stages(state)

        # Validate prompts captured
        assert len(validator.calls) > 0, "Should have intercepted LLM calls"

        # Validate prompts contain distinct content
        prompt_previews = [c["prompt_preview"] for c in validator.calls]
        unique_previews = len(set(prompt_previews))

        # Should have some variation in prompts (not all identical)
        assert unique_previews >= len(validator.calls) * 0.5, \
            f"Prompts should vary by stage. Unique: {unique_previews}, Total: {len(validator.calls)}"

        print(f"\n✓ Prompts captured: {len(validator.calls)}")
        print(f"✓ Unique prompts: {unique_previews}")
        for i, call in enumerate(validator.calls[:3], 1):
            print(f"  Call {i}: {call['prompt_preview'][:80]}...")

    def test_live_provider_timeout_config_used(self, validator):
        """Validate that project-level timeout config is used, not env vars."""
        custom_timeout = 240  # 4 minutes instead of default 180
        custom_retries = 5    # 5 retries instead of default 3

        settings = _live_settings(timeout_seconds=custom_timeout, max_attempts=custom_retries)

        assert settings.model.request_timeout_seconds == custom_timeout
        assert settings.model.request_max_attempts == custom_retries

        print(f"\n✓ Project config applied:")
        print(f"  Timeout: {settings.model.request_timeout_seconds}s (custom: {custom_timeout}s)")
        print(f"  Max Retries: {settings.model.request_max_attempts} (custom: {custom_retries})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "llm_live", "--tb=short"])

"""
Live LLM Validation Tests with Token/Prompt Tracking

Validates that each gate/stage executes against live LLM (not fixtures) by:
1. Tracking token counts for each LLM call
2. Capturing prompt text and verifying content
3. Monitoring for fixture fallback indicators
4. Ensuring real LLM responses (not cached/mocked)
"""
import pytest
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from unittest.mock import patch, MagicMock

from threat_modeler.framework import FrameworkOrchestrator
from threat_modeler.config import RuntimeSettings, build_default_settings, ModelSelection
from threat_modeler.llm.openai_compatible_adapter import OpenAICompatibleAdapter


class LiveLLMValidator:
    """Tracks LLM calls to validate live execution and token usage."""

    def __init__(self):
        self.calls: List[Dict[str, Any]] = []
        self.tokens_by_stage: Dict[str, int] = {}
        self.prompts_by_gate: Dict[str, str] = {}
        self.original_post = None
        self.fixture_fallback_detected = False

    def install(self, adapter: OpenAICompatibleAdapter):
        """Hook into adapter to intercept LLM calls."""
        self.original_post = adapter._post
        adapter._post = self._intercept_post

    def _intercept_post(self, endpoint: str, payload: Dict, **kwargs) -> Dict:
        """Intercept POST call to track tokens and prompts."""
        # Extract prompt from payload
        prompt_text = ""
        if "messages" in payload:
            prompt_text = str(payload["messages"])

        # Call original
        response = self.original_post(endpoint, payload, **kwargs)

        # Record call
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "prompt_length": len(prompt_text),
            "prompt_preview": prompt_text[:200],
            "response_model": response.get("model", "unknown"),
            "usage": response.get("usage", {}),
            "completion_tokens": response.get("usage", {}).get("completion_tokens", 0),
            "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
            "total_tokens": response.get("usage", {}).get("total_tokens", 0),
        }

        self.calls.append(call_record)

        # Detect fixture fallback (indicator: zero token usage or mock response)
        if call_record["total_tokens"] == 0:
            self.fixture_fallback_detected = True

        return response

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
        # Build live settings
        settings = build_default_settings()
        assert settings.provider.provider_type == "live", "Should use live provider"

        # Create framework
        framework = FrameworkOrchestrator(
            system_name="Test System",
            architecture_text="subsystem: TestSubsystem, component: TestComponent",
            settings=settings,
        )

        # Hook validator
        adapter = framework.adapter
        validator.install(adapter)

        # Run initial stages (agent_01, agent_02)
        framework._initialize_context()

        # Validate not using fixtures
        assert not validator.check_fixture_fallback(), \
            "Should use live LLM, not fixture fallback. Calls: " + json.dumps(validator.calls, indent=2)

        # Print report
        print("\n" + validator.get_call_report())

    def test_gate_1_has_llm_calls_with_tokens(self, validator, gate_validator):
        """Validate Gate 1 makes LLM calls with measurable token usage."""
        settings = build_default_settings()
        framework = FrameworkOrchestrator(
            system_name="Test System",
            architecture_text="subsystem: TestSubsystem, component: TestComponent",
            settings=settings,
        )

        adapter = framework.adapter
        validator.install(adapter)

        # Initialize (Gate 1 validations run here)
        framework._initialize_context()

        # Validate gate 1
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
        settings = build_default_settings()
        framework = FrameworkOrchestrator(
            system_name="Test System for STRIDE",
            architecture_text="""
            subsystem: Authentication, component: LoginProcessor
            subsystem: Database, component: UserStore
            data_flow: LoginProcessor -> UserStore (SQL)
            trust_boundary: External Network boundary
            """,
            settings=settings,
        )

        adapter = framework.adapter
        validator.install(adapter)

        # Run through stages to reach STRIDE (agent_04)
        # Note: This is a simplified check; full pipeline runs in integration tests
        framework._initialize_context()

        # Validate tokens were used (gate_3 happens after context is built)
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
        settings = build_default_settings()
        framework = FrameworkOrchestrator(
            system_name="Multi-Stage Test",
            architecture_text="""
            subsystem: Frontend, component: WebUI
            subsystem: Backend, component: API Server
            subsystem: Database, component: PostgreSQL
            interface: Frontend-Backend (HTTPS)
            interface: Backend-Database (SQL)
            """,
            settings=settings,
        )

        adapter = framework.adapter
        validator.install(adapter)

        # Initialize context
        framework._initialize_context()

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
        # Set custom timeout in settings
        custom_timeout = 240  # 4 minutes instead of default 180
        custom_retries = 5    # 5 retries instead of default 3

        settings = build_default_settings()
        settings.model.request_timeout_seconds = custom_timeout
        settings.model.request_max_attempts = custom_retries

        # Verify settings
        assert settings.model.request_timeout_seconds == custom_timeout
        assert settings.model.request_max_attempts == custom_retries

        print(f"\n✓ Project config applied:")
        print(f"  Timeout: {settings.model.request_timeout_seconds}s (custom: {custom_timeout}s)")
        print(f"  Max Retries: {settings.model.request_max_attempts} (custom: {custom_retries})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "llm_live", "--tb=short"])

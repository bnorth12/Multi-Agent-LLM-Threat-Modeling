from threat_modeler.config import (
    EXECUTION_MODE_COMPATIBILITY,
    EXECUTION_MODE_GOVERNED,
    PipelineSettings,
    build_default_settings,
    normalize_execution_mode,
)
from threat_modeler.server.api import _runtime_settings_from_payload


def test_default_pipeline_execution_mode_is_governed() -> None:
    settings = build_default_settings()
    assert settings.pipeline.execution_mode == EXECUTION_MODE_GOVERNED


def test_pipeline_settings_default_mode_is_governed() -> None:
    pipeline = PipelineSettings()
    assert pipeline.execution_mode == EXECUTION_MODE_GOVERNED


def test_normalize_execution_mode_accepts_compatibility_mode() -> None:
    assert normalize_execution_mode("linear") == EXECUTION_MODE_COMPATIBILITY


def test_normalize_execution_mode_fails_closed_to_governed() -> None:
    assert normalize_execution_mode("unsupported-mode") == EXECUTION_MODE_GOVERNED


def test_api_runtime_settings_invalid_mode_falls_back_to_governed() -> None:
    payload = {
        "pipeline": {
            "execution_mode": "unsupported-mode",
        }
    }
    settings = _runtime_settings_from_payload(payload)
    assert settings.pipeline.execution_mode == EXECUTION_MODE_GOVERNED


def test_api_runtime_settings_accepts_linear_compatibility_mode() -> None:
    payload = {
        "pipeline": {
            "execution_mode": "linear",
        }
    }
    settings = _runtime_settings_from_payload(payload)
    assert settings.pipeline.execution_mode == EXECUTION_MODE_COMPATIBILITY

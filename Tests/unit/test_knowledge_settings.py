"""GraphRAG Phase 0: KnowledgeSettings + Threat evidence contract tests."""

from __future__ import annotations

import json
from dataclasses import asdict

from threat_modeler.agents.deserialise import _dict_to_threat
from threat_modeler.backend.runtime_state import _deserialize_settings, _serialize_settings
from threat_modeler.config import (
    KnowledgeSettings,
    ModelSelection,
    RuntimeSettings,
    build_default_settings,
    default_knowledge_persist_path,
)
from threat_modeler.models.canonical import Threat


def test_default_settings_knowledge_disabled():
    settings = build_default_settings()
    assert isinstance(settings.knowledge, KnowledgeSettings)
    assert settings.knowledge.enabled is False
    assert settings.knowledge == KnowledgeSettings()


def test_runtime_settings_without_knowledge_arg_defaults_off():
    settings = RuntimeSettings(model=ModelSelection(provider="fixture", model_name="x"))
    assert settings.knowledge.enabled is False


def test_knowledge_defaults_match_contract():
    k = KnowledgeSettings()
    assert k.persist_path == ""
    assert k.snapshot_id is None
    assert k.embedding_profile == "chroma_default"
    assert k.max_hits_per_stage == 6
    assert k.egress_policy == "excerpts_only"
    assert default_knowledge_persist_path().endswith(".multi_agent_threat_modeler_kb")


def test_settings_round_trip_preserves_knowledge():
    base = build_default_settings()
    knowledge = KnowledgeSettings(
        enabled=True,
        persist_path="C:/kb",
        snapshot_id="snap-42",
        embedding_profile="bge_large_local",
        max_hits_per_stage=3,
        egress_policy="excerpts_only",
    )
    settings = RuntimeSettings(model=base.model, pipeline=base.pipeline, knowledge=knowledge)
    payload = json.loads(json.dumps(_serialize_settings(settings)))
    restored = _deserialize_settings(payload)
    assert restored is not None
    assert restored.knowledge == knowledge


def test_serialize_still_strips_api_key():
    base = build_default_settings()
    model = ModelSelection(provider="xai", model_name="grok-4", api_key="secret")
    payload = _serialize_settings(RuntimeSettings(model=model, pipeline=base.pipeline))
    assert payload["model"]["api_key"] == ""
    assert payload["knowledge"]["enabled"] is False


def test_legacy_payload_without_knowledge_uses_defaults():
    legacy = {
        "model": {"provider": "fixture", "model_name": "fixture-placeholder"},
        "pipeline": {"execution_mode": "langgraph-compatible"},
    }
    restored = _deserialize_settings(legacy)
    assert restored is not None
    assert restored.knowledge == KnowledgeSettings()


def test_malformed_knowledge_payload_falls_back_to_defaults():
    payload = {
        "model": {"provider": "fixture", "model_name": "fixture-placeholder"},
        "knowledge": "not-a-dict",
    }
    restored = _deserialize_settings(payload)
    assert restored is not None
    assert restored.knowledge == KnowledgeSettings()

    partial = {
        "model": {"provider": "fixture", "model_name": "fixture-placeholder"},
        "knowledge": {"enabled": True, "max_hits_per_stage": "bad"},
    }
    restored = _deserialize_settings(partial)
    assert restored.knowledge.enabled is True
    assert restored.knowledge.max_hits_per_stage == 6


def test_threat_evidence_round_trip():
    threat = Threat(name="t", description="d", source_ids=["doc-1", "doc-2"], confidence=0.75)
    restored = _dict_to_threat(json.loads(json.dumps(asdict(threat))))
    assert restored.source_ids == ["doc-1", "doc-2"]
    assert restored.confidence == 0.75
    assert restored == threat


def test_threat_without_evidence_fields_constructs():
    threat = Threat(name="t", description="d")
    assert threat.source_ids == []
    assert threat.confidence is None
    legacy = _dict_to_threat({"name": "t", "description": "d"})
    assert legacy.source_ids == []
    assert legacy.confidence is None


def test_threat_bad_evidence_values_coerced():
    t = _dict_to_threat({"name": "t", "description": "d", "source_ids": "doc-1", "confidence": "high"})
    assert t.source_ids == []
    assert t.confidence is None
    t = _dict_to_threat({"name": "t", "description": "d", "source_ids": ["a", 7], "confidence": "0.5"})
    assert t.source_ids == ["a", "7"]
    assert t.confidence == 0.5


def test_deserialize_knowledge_enabled_accepts_only_real_bools():
    """M1: only the exact bool objects survive; anything else falls back to False."""
    from threat_modeler.backend.runtime_state import _deserialize_knowledge

    for raw in ("false", "False", "0", "", "no", None, 0, 1, "true", [], {}):
        assert _deserialize_knowledge({"enabled": raw}).enabled is False, repr(raw)
    assert _deserialize_knowledge({"enabled": True}).enabled is True
    assert _deserialize_knowledge({"enabled": False}).enabled is False
    assert _deserialize_knowledge({}).enabled is False

def test_knowledge_enabled_string_false_round_trips_as_json_false():
    """M1: a persisted "false" string must come back off and be re-saved as JSON false."""
    from threat_modeler.backend.runtime_state import _deserialize_knowledge

    restored = _deserialize_knowledge({"enabled": "false"})
    settings = RuntimeSettings(
        model=ModelSelection(provider="fixture", model_name="x"), knowledge=restored
    )
    text = json.dumps(_serialize_settings(settings))
    assert json.loads(text)["knowledge"]["enabled"] is False
    assert '"enabled": false' in text
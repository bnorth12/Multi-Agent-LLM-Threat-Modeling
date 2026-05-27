from __future__ import annotations

from threat_modeler.models.canonical import (
    CanonicalThreatModelGraph,
    Component,
    Function,
    GraphMetadata,
    Interface,
    StrideAssessment,
    Subsystem,
    SystemContext,
    Threat,
)
from threat_modeler.state import FrameworkState
from threat_modeler.validation import CanonicalGraphValidator


def _build_valid_graph() -> CanonicalThreatModelGraph:
    return CanonicalThreatModelGraph(
        metadata=GraphMetadata(generation_timestamp="2026-05-22T00:00:00Z", model_level="system"),
        system=SystemContext(
            name="Validation Test System",
            description="Schema-focused validator test fixture.",
            mission_criticality="high",
            safety_criticality="high",
        ),
        subsystems=[
            Subsystem(
                id="ss_nav",
                name="Navigation",
                description="Navigation subsystem",
                parent_system="Validation Test System",
            )
        ],
        components=[
            Component(
                id="c_mc",
                name="Mission Computer",
                parent_subsystem="ss_nav",
                hardware="hosted",
                software_modules=["mc.core"],
                description="Main compute",
            )
        ],
        functions=[
            Function(
                id="f_nav",
                name="Nav compute",
                parent_component="c_mc",
                description="Computes fused nav state",
            )
        ],
        interfaces=[
            Interface(
                id="if_nav",
                name="Nav feed",
                description="Sensor feed to mission computer",
                from_node="c_sensor",
                to_node="c_mc",
                interface_type="component-component",
                protocol="ARINC-429",
                data_items=["position_fix"],
                trust_boundary_crossing=False,
                trust_boundary_name="",
                stride=StrideAssessment(S=1, T=1, R=1, I=1, D=1, E=1),
                threats=[
                    Threat(
                        name="Navigation spoofing",
                        description="Injected frames modify navigation state",
                        mitre_attack_technique=["ATT&CK:T0856 - Spoof Reporting Message"],
                        capec_id="CAPEC-148 - Content Spoofing",
                        cwe_id="CWE-290 - Authentication Bypass by Spoofing",
                        likelihood=3,
                        impact=4,
                    )
                ],
            )
        ],
    )


def test_validator_accepts_schema_aligned_graph() -> None:
    state = FrameworkState(canonical_graph=_build_valid_graph())
    result = CanonicalGraphValidator().validate(state)

    assert result.is_valid
    assert not result.has_critical


def test_validator_rejects_invalid_interface_type() -> None:
    graph = _build_valid_graph()
    graph.interfaces[0].interface_type = "unknown"

    state = FrameworkState(canonical_graph=graph)
    result = CanonicalGraphValidator().validate(state)

    assert result.has_critical
    assert any(issue.code == "INTERFACE_TYPE_INVALID" for issue in result.critical_issues)


def test_validator_rejects_out_of_range_likelihood() -> None:
    graph = _build_valid_graph()
    graph.interfaces[0].threats[0].likelihood = 8

    state = FrameworkState(canonical_graph=graph)
    result = CanonicalGraphValidator().validate(state)

    assert result.has_critical
    assert any(issue.code == "THREAT_LIKELIHOOD_OUT_OF_RANGE" for issue in result.critical_issues)


def test_validator_rejects_invalid_model_level() -> None:
    graph = _build_valid_graph()
    graph.metadata.model_level = "platform"

    state = FrameworkState(canonical_graph=graph)
    result = CanonicalGraphValidator().validate(state)

    assert result.has_critical
    assert any(issue.code == "MODEL_LEVEL_INVALID" for issue in result.critical_issues)

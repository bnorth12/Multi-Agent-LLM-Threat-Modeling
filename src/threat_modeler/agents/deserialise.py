"""Helpers for deserialising canonical graph JSON returned by LLM agents."""

from __future__ import annotations

import json
from typing import Any

from ..models.canonical import (
    CanonicalThreatModelGraph,
    Component,
    Function,
    GraphMetadata,
    Interface,
    Mitigation,
    Subsystem,
    StrideAssessment,
    SystemContext,
    Threat,
)


def _dict_to_stride(d: dict[str, Any]) -> StrideAssessment:
    return StrideAssessment(
        S=int(d.get("S", 0)),
        S_justification=d.get("S_justification", ""),
        T=int(d.get("T", 0)),
        T_justification=d.get("T_justification", ""),
        R=int(d.get("R", 0)),
        R_justification=d.get("R_justification", ""),
        I=int(d.get("I", 0)),
        I_justification=d.get("I_justification", ""),
        D=int(d.get("D", 0)),
        D_justification=d.get("D_justification", ""),
        E=int(d.get("E", 0)),
        E_justification=d.get("E_justification", ""),
    )


def _dict_to_mitigation(d: dict[str, Any]) -> Mitigation:
    return Mitigation(
        control_id=d.get("control_id", ""),
        title=d.get("title", ""),
        description=d.get("description", ""),
        residual_risk_after_control=int(d.get("residual_risk_after_control", 3)),
    )


def _dict_to_threat(d: dict[str, Any]) -> Threat:
    return Threat(
        name=d.get("name", ""),
        description=d.get("description", ""),
        mitre_attack_technique=d.get("mitre_attack_technique", []),
        capec_id=d.get("capec_id", ""),
        cwe_id=d.get("cwe_id", ""),
        likelihood=int(d.get("likelihood", 1)),
        impact=int(d.get("impact", 1)),
        mitigations_technical=[_dict_to_mitigation(m) for m in d.get("mitigations_technical", [])],
        mitigations_administrative=[_dict_to_mitigation(m) for m in d.get("mitigations_administrative", [])],
    )


def _dict_to_interface(d: dict[str, Any]) -> Interface:
    return Interface(
        id=d.get("id", ""),
        name=d.get("name", ""),
        description=d.get("description", ""),
        from_node=d.get("from_node", ""),
        to_node=d.get("to_node", ""),
        interface_type=d.get("interface_type", "unknown"),
        protocol=d.get("protocol", "unknown"),
        data_items=d.get("data_items", []),
        trust_boundary_crossing=bool(d.get("trust_boundary_crossing", False)),
        trust_boundary_name=d.get("trust_boundary_name", ""),
        stride=_dict_to_stride(d.get("stride", {})),
        threats=[_dict_to_threat(t) for t in d.get("threats", [])],
    )


def parse_graph_json(response: str) -> CanonicalThreatModelGraph | None:
    """Parse a JSON string (from LLM or fixture) into a CanonicalThreatModelGraph.

    Returns None if the response cannot be parsed. Callers should handle None
    by keeping the existing graph unchanged.
    """
    text = response.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    meta_d = data.get("metadata", {})
    sys_d = data.get("system", {})

    return CanonicalThreatModelGraph(
        metadata=GraphMetadata(
            generation_timestamp=meta_d.get("generation_timestamp", ""),
            model_level=meta_d.get("model_level", "system"),
        ),
        system=SystemContext(
            name=sys_d.get("name", ""),
            description=sys_d.get("description", ""),
            mission_criticality=sys_d.get("mission_criticality", "undetermined"),
            safety_criticality=sys_d.get("safety_criticality", "undetermined"),
        ),
        subsystems=[
            Subsystem(
                id=s.get("id", ""),
                name=s.get("name", ""),
                description=s.get("description", ""),
                parent_system=s.get("parent_system", ""),
            )
            for s in data.get("subsystems", [])
        ],
        components=[
            Component(
                id=c.get("id", ""),
                name=c.get("name", ""),
                parent_subsystem=c.get("parent_subsystem", ""),
                hardware=c.get("hardware", ""),
                software_modules=c.get("software_modules", []),
                description=c.get("description", ""),
            )
            for c in data.get("components", [])
        ],
        functions=[
            Function(
                id=f.get("id", ""),
                name=f.get("name", ""),
                parent_component=f.get("parent_component", ""),
                description=f.get("description", ""),
            )
            for f in data.get("functions", [])
        ],
        interfaces=[_dict_to_interface(i) for i in data.get("interfaces", data.get("data_flows", []))],
    )

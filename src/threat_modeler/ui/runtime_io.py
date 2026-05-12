"""SCR-007/008/009 runtime artifact export and snapshot restore helpers."""

from __future__ import annotations

import json
from io import StringIO
from dataclasses import asdict, is_dataclass
from typing import Any

from threat_modeler.agents.deserialise import parse_graph_json
from threat_modeler.state import FrameworkState


def _to_builtin(value: Any) -> Any:
    """Recursively convert dataclasses/objects into JSON-safe builtins."""
    if is_dataclass(value):
        return {k: _to_builtin(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_builtin(v) for v in value]
    return value


def framework_state_to_dict(state: FrameworkState | None) -> dict[str, Any]:
    """Serialize FrameworkState into dict for export/snapshot."""
    if state is None:
        return {}

    return {
        "raw_text": state.raw_text,
        "tables": _to_builtin(state.tables),
        "canonical_graph": _to_builtin(state.canonical_graph.to_dict() if state.canonical_graph else None),
        "messages": _to_builtin(state.messages),
        "stix_bundle": _to_builtin(state.stix_bundle),
        "mermaid_diagrams": _to_builtin(state.mermaid_diagrams),
        "final_report": state.final_report,
        "human_feedback": state.human_feedback,
        "next_stage_id": state.next_stage_id,
        "trust_boundary_review_needed": bool(state.trust_boundary_review_needed),
        "stride_complete": bool(state.stride_complete),
        "threats_generated": bool(state.threats_generated),
        "llm_usage_by_stage": _to_builtin(state.llm_usage_by_stage),
        "llm_attempts_by_stage": _to_builtin(state.llm_attempts_by_stage),
        "llm_prompts_by_stage": _to_builtin(state.llm_prompts_by_stage),
        "llm_prompt_history": _to_builtin(state.llm_prompt_history),
        "hitl_gate_checkpoint": _to_builtin(state.hitl_gate_checkpoint),
        "hitl_paused_at_gate": state.hitl_paused_at_gate,
        "hitl_rejected_at_gate": state.hitl_rejected_at_gate,
    }


def framework_state_from_dict(data: dict[str, Any]) -> FrameworkState:
    """Deserialize FrameworkState from snapshot dict."""
    graph_data = data.get("canonical_graph")
    graph = None
    if isinstance(graph_data, dict):
        graph = parse_graph_json(json.dumps(graph_data))

    return FrameworkState(
        raw_text=str(data.get("raw_text", "")),
        tables=list(data.get("tables", [])),
        canonical_graph=graph,
        messages=list(data.get("messages", [])),
        stix_bundle=data.get("stix_bundle"),
        mermaid_diagrams=dict(data.get("mermaid_diagrams", {})),
        final_report=data.get("final_report"),
        human_feedback=data.get("human_feedback"),
        next_stage_id=data.get("next_stage_id"),
        trust_boundary_review_needed=bool(data.get("trust_boundary_review_needed", False)),
        stride_complete=bool(data.get("stride_complete", False)),
        threats_generated=bool(data.get("threats_generated", False)),
        llm_usage_by_stage=dict(data.get("llm_usage_by_stage", {})),
        llm_attempts_by_stage=dict(data.get("llm_attempts_by_stage", {})),
        llm_prompts_by_stage=dict(data.get("llm_prompts_by_stage", {})),
        llm_prompt_history=list(data.get("llm_prompt_history", [])),
        hitl_gate_checkpoint=data.get("hitl_gate_checkpoint"),
        hitl_paused_at_gate=data.get("hitl_paused_at_gate"),
        hitl_rejected_at_gate=data.get("hitl_rejected_at_gate"),
    )


def build_snapshot_payload(
    run_id: str | None,
    pipeline_state: FrameworkState | None,
    gate_states: dict[str, Any] | None,
    markdown_edits: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build stable snapshot payload for save/restore workflows."""
    return {
        "schema_version": "s07-snapshot-v1",
        "run_id": run_id,
        "pipeline_state": framework_state_to_dict(pipeline_state),
        "gate_states": _to_builtin(gate_states or {}),
        "markdown_edits": _to_builtin(markdown_edits or {}),
    }


def snapshot_payload_to_json(payload: dict[str, Any]) -> str:
    """Serialize snapshot payload to pretty JSON."""
    return json.dumps(payload, indent=2, ensure_ascii=False)


def snapshot_payload_from_json(raw: str) -> dict[str, Any]:
    """Parse and validate snapshot JSON payload."""
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("Snapshot JSON must be an object.")
    if "pipeline_state" not in obj:
        raise ValueError("Snapshot payload missing 'pipeline_state'.")
    return obj


def export_canonical_json(state: FrameworkState | None) -> str:
    """Export canonical graph JSON artifact."""
    if state is None or state.canonical_graph is None:
        return "{}\n"
    return json.dumps(state.canonical_graph.to_dict(), indent=2, ensure_ascii=False) + "\n"


def export_stix_json(state: FrameworkState | None) -> str:
    """Export STIX bundle JSON artifact."""
    if state is None or state.stix_bundle is None:
        return "{}\n"
    return json.dumps(_to_builtin(state.stix_bundle), indent=2, ensure_ascii=False) + "\n"


def export_report_markdown(state: FrameworkState | None) -> str:
    """Export final report markdown artifact."""
    if state is None or not state.final_report:
        return "# Final Report\n\nNo report generated yet.\n"
    return state.final_report


def export_mermaid_markdown(state: FrameworkState | None) -> str:
    """Export all Mermaid diagrams as markdown sections."""
    if state is None or not state.mermaid_diagrams:
        return "# Mermaid Diagrams\n\nNo diagrams generated yet.\n"

    lines: list[str] = ["# Mermaid Diagrams", ""]
    for level, code in state.mermaid_diagrams.items():
        lines.append(f"## {level}")
        lines.append("```mermaid")
        lines.append(str(code).strip())
        lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def export_token_usage_json(state: FrameworkState | None) -> str:
    """Export per-stage and aggregate token usage as JSON."""
    if state is None:
        return "{}\n"

    payload = {
        "llm_usage_by_stage": _to_builtin(getattr(state, "llm_usage_by_stage", {})),
        "llm_attempts_by_stage": _to_builtin(getattr(state, "llm_attempts_by_stage", {})),
        "llm_prompts_by_stage": _to_builtin(getattr(state, "llm_prompts_by_stage", {})),
        "llm_prompt_history": _to_builtin(getattr(state, "llm_prompt_history", [])),
        "attempt_totals": _to_builtin(state.llm_attempt_totals() if hasattr(state, "llm_attempt_totals") else {}),
        "totals": _to_builtin(state.llm_usage_totals() if hasattr(state, "llm_usage_totals") else {}),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _stride_rows(state: FrameworkState | None) -> list[dict[str, Any]]:
    """Return flat STRIDE rows per interface from canonical graph state."""
    if state is None or state.canonical_graph is None:
        return []

    rows: list[dict[str, Any]] = []
    for interface in state.canonical_graph.interfaces:
        rows.append(
            {
                "interface_id": interface.id,
                "interface_name": interface.name,
                "from_node": interface.from_node,
                "to_node": interface.to_node,
                "S": interface.stride.S,
                "S_justification": interface.stride.S_justification,
                "T": interface.stride.T,
                "T_justification": interface.stride.T_justification,
                "R": interface.stride.R,
                "R_justification": interface.stride.R_justification,
                "I": interface.stride.I,
                "I_justification": interface.stride.I_justification,
                "D": interface.stride.D,
                "D_justification": interface.stride.D_justification,
                "E": interface.stride.E,
                "E_justification": interface.stride.E_justification,
                "threat_count": len(interface.threats),
            }
        )
    return rows


def export_stride_json(state: FrameworkState | None) -> str:
    """Export per-interface STRIDE artifact as JSON."""
    rows = _stride_rows(state)
    payload = {
        "rows": rows,
        "row_count": len(rows),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def export_stride_csv(state: FrameworkState | None) -> str:
    """Export per-interface STRIDE artifact as CSV."""
    rows = _stride_rows(state)
    if not rows:
        return "interface_id,interface_name,from_node,to_node,S,T,R,I,D,E,threat_count\n"

    fieldnames = [
        "interface_id",
        "interface_name",
        "from_node",
        "to_node",
        "S",
        "T",
        "R",
        "I",
        "D",
        "E",
        "threat_count",
    ]
    output = StringIO()
    output.write(",".join(fieldnames) + "\n")
    for row in rows:
        values = [str(row.get(name, "")).replace(",", " ") for name in fieldnames]
        output.write(",".join(values) + "\n")
    return output.getvalue()

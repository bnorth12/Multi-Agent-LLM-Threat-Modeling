"""
Report exporter — renders the final markdown threat model report.

When ``state.final_report`` is already set (populated by agent_09), it is
returned directly.  When it is absent, a minimal fallback report is generated
from the canonical graph so the exporter is always usable.
"""

from __future__ import annotations

from ..models import CanonicalThreatModelGraph
from ..state import FrameworkState


def export_report(state: FrameworkState) -> str:
    """Return the markdown threat model report.

    Prefers ``state.final_report`` (written by agent_09).  If unavailable,
    generates a minimal structured report from the canonical graph.

    Parameters
    ----------
    state:
        Pipeline state after all agents have run.

    Returns
    -------
    str
        Markdown-formatted threat model report.
    """
    if state.final_report:
        return state.final_report

    graph = state.canonical_graph
    if graph is None:
        return "# Threat Model Report\n\n*No canonical graph available.*\n"

    return _build_fallback_report(graph)


def _build_fallback_report(graph: CanonicalThreatModelGraph) -> str:
    lines: list[str] = [
        f"# Threat Model Report — {graph.system.name}",
        "",
        "## Executive Summary",
        "",
        graph.system.description or "_No system description available._",
        "",
        "## System Scope",
        "",
        f"- Mission criticality: {graph.system.mission_criticality}",
        f"- Safety criticality: {graph.system.safety_criticality}",
        f"- Subsystems: {len(graph.subsystems)}",
        f"- Components: {len(graph.components)}",
        f"- Interfaces: {len(graph.interfaces)}",
        "",
        "## Trust Boundaries",
        "",
    ]

    tb_interfaces = [i for i in graph.interfaces if i.trust_boundary_crossing]
    if tb_interfaces:
        for iface in tb_interfaces:
            lines.append(f"- **{iface.name}** ({iface.from_node} → {iface.to_node}): {iface.trust_boundary_name}")
    else:
        lines.append("_No trust boundary crossings identified._")

    lines += [
        "",
        "## Top Threats",
        "",
    ]

    threat_count = 0
    for iface in graph.interfaces:
        for threat in iface.threats:
            threat_count += 1
            lines.append(f"### {threat.name}")
            lines.append(f"- **Interface**: {iface.name}")
            lines.append(f"- **Likelihood**: {threat.likelihood} / 5")
            lines.append(f"- **Impact**: {threat.impact} / 5")
            lines.append(f"- {threat.description}")
            lines.append("")

    if threat_count == 0:
        lines.append("_No threats identified._")
        lines.append("")

    lines += [
        "## Mitigation Mapping",
        "",
    ]

    for iface in graph.interfaces:
        for threat in iface.threats:
            all_mit = list(threat.mitigations_technical) + list(threat.mitigations_administrative)
            if all_mit:
                lines.append(f"### Threat: {threat.name}")
                for m in all_mit:
                    lines.append(f"- **{m.control_id}** — {m.title}: {m.description}")
                lines.append("")

    return "\n".join(lines)

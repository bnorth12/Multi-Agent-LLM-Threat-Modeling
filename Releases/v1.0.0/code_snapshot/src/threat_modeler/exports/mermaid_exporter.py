"""
Mermaid diagram exporter — emits Mermaid diagram source from the canonical graph.

Produces a ``flowchart LR`` diagram showing system → subsystems → components
with trust-boundary-crossing interfaces annotated.
"""

from __future__ import annotations

from ..models import CanonicalThreatModelGraph


def export_mermaid(graph: CanonicalThreatModelGraph) -> str:
    """Return a Mermaid flowchart source string for the canonical graph.

    Nodes represent the system, each subsystem, and each component.
    Edges represent interfaces; trust-boundary-crossing interfaces are
    annotated with ``[TB]``.

    Parameters
    ----------
    graph:
        The canonical threat model graph to export.

    Returns
    -------
    str
        A multi-line Mermaid ``flowchart LR`` diagram source string.
    """
    lines: list[str] = ["flowchart LR"]

    # System node
    sys_id = _sanitize(graph.system.name or "system")
    lines.append(f'    {sys_id}["{graph.system.name}"]')

    # Subsystem nodes + edges from system
    sub_map: dict[str, str] = {}
    for sub in graph.subsystems:
        node_id = _sanitize(sub.id)
        sub_map[sub.id] = node_id
        lines.append(f'    {node_id}["{sub.name}"]')
        lines.append(f"    {sys_id} --> {node_id}")

    # Component nodes + edges from parent subsystem
    comp_map: dict[str, str] = {}
    for comp in graph.components:
        node_id = _sanitize(comp.id)
        comp_map[comp.id] = node_id
        lines.append(f'    {node_id}["{comp.name}"]')
        parent = sub_map.get(comp.parent_subsystem)
        if parent:
            lines.append(f"    {parent} --> {node_id}")

    # Interface edges
    for iface in graph.interfaces:
        from_id = _sanitize(iface.from_node)
        to_id = _sanitize(iface.to_node)
        label = f"[TB] {iface.name}" if iface.trust_boundary_crossing else iface.name
        lines.append(f'    {from_id} -->|"{label}"| {to_id}')

    return "\n".join(lines)


def _sanitize(text: str) -> str:
    """Convert arbitrary text into a valid Mermaid node identifier."""
    return "".join(c if c.isalnum() else "_" for c in text)

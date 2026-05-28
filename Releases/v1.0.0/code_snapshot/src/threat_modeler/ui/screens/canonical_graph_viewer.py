"""GUI-019 — Canonical Graph Viewer screen."""

from __future__ import annotations

from typing import Any

import streamlit as st

from threat_modeler.ui.execution import sync_execution_state_to_session


def _system_context_row(graph: Any) -> dict[str, str]:
    """Build a deterministic system context row for display/tests."""
    return {
        "System": graph.system.name,
        "Description": graph.system.description,
        "Mission Criticality": graph.system.mission_criticality,
        "Safety Criticality": graph.system.safety_criticality,
    }


def _component_rows(graph: Any, subsystem_id: str) -> list[dict[str, str]]:
    """Build component rows for a subsystem."""
    rows: list[dict[str, str]] = []
    for component in graph.components:
        if component.parent_subsystem != subsystem_id:
            continue
        rows.append(
            {
                "Component ID": component.id,
                "Name": component.name,
                "Hardware": component.hardware,
                "Description": component.description,
                "Software Modules": ", ".join(component.software_modules),
            }
        )
    return rows


def _function_rows(graph: Any, component_id: str) -> list[dict[str, str]]:
    """Build function rows for a component."""
    rows: list[dict[str, str]] = []
    for function in graph.functions:
        if function.parent_component != component_id:
            continue
        rows.append(
            {
                "Function ID": function.id,
                "Name": function.name,
                "Description": function.description,
            }
        )
    return rows


def _interface_rows(graph: Any) -> list[dict[str, Any]]:
    """Build interface rows including trust boundary metadata."""
    rows: list[dict[str, Any]] = []
    for interface in graph.interfaces:
        rows.append(
            {
                "Interface": interface.name,
                "ID": interface.id,
                "From": interface.from_node,
                "To": interface.to_node,
                "Type": interface.interface_type,
                "Protocol": interface.protocol,
                "Trust Boundary Crossing": interface.trust_boundary_crossing,
                "Trust Boundary": interface.trust_boundary_name,
                "Data Items": ", ".join(interface.data_items),
            }
        )
    return rows


def render() -> None:
    st.header("Canonical Graph Viewer")
    st.caption("GUI-019 — hierarchy and interface trust-boundary inspection")

    sync_execution_state_to_session()

    state = st.session_state.get("pipeline_state")
    if state is None or state.canonical_graph is None:
        st.warning("No canonical graph available. Complete a pipeline run first.")
        return

    graph = state.canonical_graph

    st.subheader("System Context")
    st.table([_system_context_row(graph)])

    st.subheader("Hierarchy")
    for subsystem in graph.subsystems:
        with st.expander(f"Subsystem: {subsystem.name} ({subsystem.id})", expanded=False):
            st.write(subsystem.description)
            component_rows = _component_rows(graph, subsystem.id)
            if component_rows:
                st.table(component_rows)
            for component in [c for c in graph.components if c.parent_subsystem == subsystem.id]:
                function_rows = _function_rows(graph, component.id)
                if function_rows:
                    st.caption(f"Functions for {component.name}")
                    st.table(function_rows)

    st.subheader("Interfaces and Trust Boundaries")
    st.table(_interface_rows(graph))

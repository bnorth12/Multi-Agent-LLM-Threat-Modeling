"""Integration tests for GUI-019 Canonical Graph Viewer display models."""

from threat_modeler.models.canonical import (
    CanonicalThreatModelGraph,
    Component,
    Function,
    Interface,
    Subsystem,
    SystemContext,
)
from threat_modeler.ui.screens.canonical_graph_viewer import (
    _component_rows,
    _function_rows,
    _interface_rows,
    _system_context_row,
)


def _graph() -> CanonicalThreatModelGraph:
    return CanonicalThreatModelGraph(
        system=SystemContext(name="SysA", description="Desc", mission_criticality="high", safety_criticality="medium"),
        subsystems=[Subsystem(id="sub-1", name="Sub1", description="S1", parent_system="SysA")],
        components=[
            Component(id="cmp-1", name="Comp1", parent_subsystem="sub-1", hardware="host", software_modules=["m1"], description="C1"),
        ],
        functions=[Function(id="fn-1", name="Fn1", parent_component="cmp-1", description="F1")],
        interfaces=[
            Interface(
                id="if-1",
                name="IF1",
                description="I1",
                from_node="a",
                to_node="b",
                interface_type="component-component",
                protocol="http",
                data_items=["d1", "d2"],
                trust_boundary_crossing=True,
                trust_boundary_name="tb-1",
            )
        ],
    )


def test_system_context_row_matches_graph_fields():
    row = _system_context_row(_graph())
    assert row["System"] == "SysA"
    assert row["Mission Criticality"] == "high"
    assert row["Safety Criticality"] == "medium"


def test_component_rows_match_expected_values():
    rows = _component_rows(_graph(), "sub-1")
    assert len(rows) == 1
    assert rows[0]["Component ID"] == "cmp-1"
    assert rows[0]["Software Modules"] == "m1"


def test_function_rows_match_expected_values():
    rows = _function_rows(_graph(), "cmp-1")
    assert len(rows) == 1
    assert rows[0]["Function ID"] == "fn-1"
    assert rows[0]["Name"] == "Fn1"


def test_interface_rows_include_trust_boundary_fields():
    rows = _interface_rows(_graph())
    assert len(rows) == 1
    assert rows[0]["Trust Boundary Crossing"] is True
    assert rows[0]["Trust Boundary"] == "tb-1"
    assert rows[0]["Data Items"] == "d1, d2"

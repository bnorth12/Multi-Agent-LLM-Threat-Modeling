"""Integration tests for GUI-021 STRIDE Viewer display models."""

from threat_modeler.models.canonical import (
    CanonicalThreatModelGraph,
    Interface,
    StrideAssessment,
    Threat,
)
from threat_modeler.state import FrameworkState
from threat_modeler.ui.screens.stride_viewer import _sorted_rows, _stride_rows


def _state() -> FrameworkState:
    graph = CanonicalThreatModelGraph(
        interfaces=[
            Interface(
                id="if-a",
                name="A",
                description="",
                from_node="x",
                to_node="y",
                stride=StrideAssessment(S=3, T=1, R=2, I=4, D=1, E=0),
                threats=[Threat(name="th-1", description="d")],
            ),
            Interface(
                id="if-b",
                name="B",
                description="",
                from_node="x2",
                to_node="y2",
                stride=StrideAssessment(S=1, T=5, R=1, I=1, D=2, E=3),
                threats=[Threat(name="th-2", description="d"), Threat(name="th-3", description="d")],
            ),
        ]
    )
    return FrameworkState(canonical_graph=graph)


def test_stride_rows_capture_scores_and_threat_counts():
    rows = _stride_rows(_state())
    assert len(rows) == 2
    by_id = {row["interface_id"]: row for row in rows}
    assert by_id["if-a"]["S"] == 3
    assert by_id["if-a"]["threat_count"] == 1
    assert by_id["if-b"]["T"] == 5
    assert by_id["if-b"]["threat_count"] == 2


def test_stride_rows_include_threat_names():
    rows = _stride_rows(_state())
    by_id = {row["interface_id"]: row for row in rows}
    assert "th-2" in by_id["if-b"]["threat_names"]
    assert "th-3" in by_id["if-b"]["threat_names"]


def test_stride_sorting_by_metric_descending():
    rows = _stride_rows(_state())
    sorted_rows = _sorted_rows(rows, "T", ascending=False)
    assert sorted_rows[0]["interface_id"] == "if-b"

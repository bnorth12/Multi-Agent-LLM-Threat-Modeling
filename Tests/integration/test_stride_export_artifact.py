"""Integration tests for GUI-022 STRIDE export artifacts."""

import json

from threat_modeler.models.canonical import CanonicalThreatModelGraph, Interface, StrideAssessment
from threat_modeler.state import FrameworkState
from threat_modeler.ui.runtime_io import export_stride_csv, export_stride_json


def _state() -> FrameworkState:
    graph = CanonicalThreatModelGraph(
        interfaces=[
            Interface(
                id="if-1",
                name="I1",
                description="",
                from_node="n1",
                to_node="n2",
                stride=StrideAssessment(S=2, T=3, R=1, I=4, D=0, E=5),
            )
        ]
    )
    return FrameworkState(canonical_graph=graph)


def test_export_stride_json_matches_expected_fields_and_values():
    payload = json.loads(export_stride_json(_state()))
    assert payload["row_count"] == 1
    row = payload["rows"][0]
    assert row["interface_id"] == "if-1"
    assert row["S"] == 2
    assert row["E"] == 5


def test_export_stride_csv_contains_expected_headers_and_values():
    csv_text = export_stride_csv(_state())
    assert "interface_id,interface_name,from_node,to_node,S,T,R,I,D,E,threat_count" in csv_text
    assert "if-1,I1,n1,n2,2,3,1,4,0,5" in csv_text

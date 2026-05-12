"""Integration tests for GUI-020 Mermaid Viewer display models."""

from threat_modeler.ui.screens.mermaid_viewer import _diagram_rows, _is_probably_valid_mermaid


def test_valid_mermaid_detection():
    assert _is_probably_valid_mermaid("flowchart LR\nA-->B") is True
    assert _is_probably_valid_mermaid("sequenceDiagram\nA->>B: hi") is True


def test_invalid_mermaid_detection():
    assert _is_probably_valid_mermaid("") is False
    assert _is_probably_valid_mermaid("not-mermaid") is False


def test_diagram_rows_report_expected_counts_and_validity():
    rows = _diagram_rows({"level_1": "flowchart LR\nA-->B", "level_2": "invalid source"})
    assert len(rows) == 2
    by_level = {row["level"]: row for row in rows}
    assert by_level["level_1"]["line_count"] == 2
    assert by_level["level_1"]["is_valid"] is True
    assert by_level["level_2"]["is_valid"] is False

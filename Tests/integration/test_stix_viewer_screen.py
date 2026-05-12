"""Integration tests for GUI-018: STIX Threat Model Viewer."""

from threat_modeler.ui.screens.stix_viewer import (
    _extract_stix_objects,
    _filter_objects,
    _group_objects_by_type,
    _summary_rows,
)


def _sample_bundle() -> dict:
    return {
        "type": "bundle",
        "id": "bundle--1234",
        "objects": [
            {
                "type": "attack-pattern",
                "id": "attack-pattern--a1",
                "name": "Spoofed telemetry",
                "description": "Threat on telemetry path",
            },
            {
                "type": "course-of-action",
                "id": "course-of-action--c1",
                "name": "Mutual TLS",
                "description": "Apply mTLS on interface",
            },
            {
                "type": "relationship",
                "id": "relationship--r1",
                "relationship_type": "mitigates",
                "source_ref": "course-of-action--c1",
                "target_ref": "attack-pattern--a1",
            },
        ],
    }


def test_extract_stix_objects_from_bundle():
    objects = _extract_stix_objects(_sample_bundle())
    assert len(objects) == 3
    assert all(isinstance(obj, dict) for obj in objects)


def test_extract_stix_objects_handles_missing_objects_key():
    assert _extract_stix_objects({"type": "bundle"}) == []
    assert _extract_stix_objects(None) == []


def test_group_objects_by_type_counts_correctly():
    grouped = _group_objects_by_type(_extract_stix_objects(_sample_bundle()))
    assert set(grouped.keys()) == {"attack-pattern", "course-of-action", "relationship"}
    assert len(grouped["attack-pattern"]) == 1
    assert len(grouped["course-of-action"]) == 1
    assert len(grouped["relationship"]) == 1


def test_filter_objects_by_type():
    objects = _extract_stix_objects(_sample_bundle())
    filtered = _filter_objects(objects, {"attack-pattern"}, "")
    assert len(filtered) == 1
    assert filtered[0]["type"] == "attack-pattern"


def test_filter_objects_by_search_text_name():
    objects = _extract_stix_objects(_sample_bundle())
    filtered = _filter_objects(objects, set(), "telemetry")
    assert len(filtered) == 1
    assert filtered[0]["id"] == "attack-pattern--a1"


def test_filter_objects_by_search_text_id():
    objects = _extract_stix_objects(_sample_bundle())
    filtered = _filter_objects(objects, set(), "r1")
    assert len(filtered) == 1
    assert filtered[0]["id"] == "relationship--r1"


def test_summary_rows_contains_expected_columns():
    rows = _summary_rows(_extract_stix_objects(_sample_bundle()))
    assert len(rows) == 3
    assert set(rows[0].keys()) == {
        "Type",
        "ID",
        "Name",
        "Relationship",
        "Source",
        "Target",
        "Description",
    }


def test_summary_rows_truncates_long_description():
    objects = [
        {
            "type": "attack-pattern",
            "id": "attack-pattern--x",
            "name": "X",
            "description": "a" * 200,
        }
    ]
    rows = _summary_rows(objects)
    assert rows[0]["Description"].endswith("...")

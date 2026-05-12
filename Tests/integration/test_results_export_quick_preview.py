"""Integration tests for GUI-023 Results Export quick preview data correctness."""

from threat_modeler.models.canonical import CanonicalThreatModelGraph, Interface
from threat_modeler.state import FrameworkState
from threat_modeler.ui.runtime_io import (
    export_canonical_json,
    export_mermaid_markdown,
    export_report_markdown,
    export_stride_json,
    export_stix_json,
    export_token_usage_json,
)
from threat_modeler.ui.version_governance import (
    generate_component_file_inventory,
    generate_component_version_manifest,
    inventory_to_json,
    manifest_to_json,
)


def _state() -> FrameworkState:
    state = FrameworkState(
        canonical_graph=CanonicalThreatModelGraph(
            interfaces=[Interface(id="if-1", name="I1", description="", from_node="a", to_node="b")]
        ),
        stix_bundle={"type": "bundle", "objects": [{"type": "attack-pattern", "id": "attack-pattern--1"}]},
        mermaid_diagrams={"level_1": "flowchart LR\nA-->B"},
        final_report="# Report\n\nContent",
    )
    return state


def test_quick_preview_artifacts_contain_current_state_data():
    state = _state()
    assert '"id": "if-1"' in export_canonical_json(state)
    assert '"type": "bundle"' in export_stix_json(state)
    assert "flowchart LR" in export_mermaid_markdown(state)
    assert "# Report" in export_report_markdown(state)
    assert '"row_count": 1' in export_stride_json(state)
    assert '"llm_usage_by_stage"' in export_token_usage_json(state)


def test_version_governance_preview_payloads_have_expected_shape():
    manifest = generate_component_version_manifest()
    inventory = generate_component_file_inventory()
    manifest_json = manifest_to_json(manifest)
    inventory_json = inventory_to_json(inventory)

    assert '"components"' in manifest_json
    assert '"project_version"' in manifest_json
    assert '"files"' in inventory_json
    assert inventory["row_count"] == len(inventory["files"])

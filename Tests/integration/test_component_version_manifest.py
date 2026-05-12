"""Integration tests for PRJ-021 component version manifest."""

from threat_modeler.ui.version_governance import generate_component_version_manifest


def test_component_manifest_contains_expected_components_and_version():
    manifest = generate_component_version_manifest()
    components = manifest.get("components", [])
    component_names = {item["component"] for item in components}

    assert manifest.get("manifest_version") == "s09-component-version-v1"
    assert manifest.get("project_version")
    assert {"ui", "agents", "models", "orchestrator", "validation", "exports"}.issubset(component_names)


def test_component_manifest_file_counts_are_non_negative():
    manifest = generate_component_version_manifest()
    for component in manifest.get("components", []):
        assert component["file_count"] >= 0

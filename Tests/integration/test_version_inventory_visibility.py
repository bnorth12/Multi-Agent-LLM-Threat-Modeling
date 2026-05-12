"""Integration tests for GUI-024 version inventory visibility payloads."""

from threat_modeler.ui.version_governance import (
    generate_component_file_inventory,
    generate_component_version_manifest,
)


def test_visibility_payloads_are_non_empty_and_consistent():
    manifest = generate_component_version_manifest()
    inventory = generate_component_file_inventory()

    assert manifest.get("components")
    assert inventory.get("files") is not None
    assert inventory.get("row_count") == len(inventory.get("files", []))


def test_every_inventory_component_exists_in_manifest():
    manifest = generate_component_version_manifest()
    inventory = generate_component_file_inventory()

    manifest_components = {row["component"] for row in manifest.get("components", [])}
    inventory_components = {row["component"] for row in inventory.get("files", [])}
    assert inventory_components.issubset(manifest_components)

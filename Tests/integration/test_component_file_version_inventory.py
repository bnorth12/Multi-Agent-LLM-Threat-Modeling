"""Integration tests for PRJ-022 component-file version inventory."""

from threat_modeler.ui.version_governance import generate_component_file_inventory


def test_inventory_contains_deterministic_file_rows_with_hashes():
    inventory = generate_component_file_inventory()
    assert inventory.get("inventory_version") == "s09-component-file-inventory-v1"
    assert inventory.get("row_count") == len(inventory.get("files", []))

    if inventory["files"]:
        row = inventory["files"][0]
        assert row["component"]
        assert row["path"].startswith("src/threat_modeler/")
        assert len(row["sha256"]) == 64
        assert row["size_bytes"] >= 0


def test_inventory_is_sorted_by_component_then_path():
    inventory = generate_component_file_inventory()
    keys = [(row["component"], row["path"]) for row in inventory.get("files", [])]
    assert keys == sorted(keys)

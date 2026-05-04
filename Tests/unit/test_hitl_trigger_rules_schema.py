"""Unit tests for HITL trigger rules schema and default fixture validity."""

import json
import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _validate(instance, schema, path="$"):
    schema_type = schema.get("type")
    if schema_type == "object":
        assert isinstance(instance, dict), f"{path} must be an object"
        required = schema.get("required", [])
        for key in required:
            assert key in instance, f"{path}.{key} is required"

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                assert key in properties, f"{path}.{key} is not allowed"

        for key, sub_schema in properties.items():
            if key in instance:
                _validate(instance[key], sub_schema, f"{path}.{key}")
        return

    if schema_type == "string":
        assert isinstance(instance, str), f"{path} must be a string"
        if "pattern" in schema:
            assert re.match(schema["pattern"], instance), f"{path} does not match required pattern"
        if "enum" in schema:
            assert instance in schema["enum"], f"{path} must be one of {schema['enum']}"
        return

    if schema_type == "boolean":
        assert isinstance(instance, bool), f"{path} must be a boolean"
        return

    if schema_type == "integer":
        assert isinstance(instance, int) and not isinstance(instance, bool), f"{path} must be an integer"
        if "minimum" in schema:
            assert instance >= schema["minimum"], f"{path} must be >= {schema['minimum']}"
        if "maximum" in schema:
            assert instance <= schema["maximum"], f"{path} must be <= {schema['maximum']}"
        return

    if schema_type == "number":
        assert isinstance(instance, (int, float)) and not isinstance(instance, bool), f"{path} must be a number"
        if "minimum" in schema:
            assert instance >= schema["minimum"], f"{path} must be >= {schema['minimum']}"
        if "maximum" in schema:
            assert instance <= schema["maximum"], f"{path} must be <= {schema['maximum']}"
        return

    raise AssertionError(f"Unsupported schema type at {path}: {schema_type}")


def test_trigger_rules_fixture_matches_schema():
    repo = _repo_root()
    schema_path = repo / "docs" / "schemas" / "hitl_trigger_rules.schema.json"
    fixture_path = repo / "Tests" / "fixtures" / "inputs" / "hitl" / "trigger_rules_default.json"

    with schema_path.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    with fixture_path.open("r", encoding="utf-8") as f:
        fixture = json.load(f)

    _validate(fixture, schema)


def test_trigger_rules_invalid_fixture_fails_with_clear_message():
    repo = _repo_root()
    schema_path = repo / "docs" / "schemas" / "hitl_trigger_rules.schema.json"
    fixture_path = repo / "Tests" / "fixtures" / "inputs" / "hitl" / "trigger_rules_invalid_missing_required.json"

    with schema_path.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    with fixture_path.open("r", encoding="utf-8") as f:
        fixture = json.load(f)

    with pytest.raises(AssertionError) as exc_info:
        _validate(fixture, schema)

    # Ensure the failure message points to the missing required gate key.
    assert "$.gates.export_consistency is required" in str(exc_info.value)

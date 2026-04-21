"""Validation seams for the runtime skeleton."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import json
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .models import CanonicalThreatModelGraph
from .state import FrameworkState


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    location: str = ""


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)


class CanonicalGraphValidator:
    def __init__(self, schema_path: Path | None = None) -> None:
        self.schema_path = schema_path or self._default_schema_path()
        self.schema = self._load_schema(self.schema_path)
        self.validator = Draft202012Validator(self.schema)

    def _default_schema_path(self) -> Path:
        return Path(__file__).resolve().parents[2] / "docs" / "schemas" / "canonical_graph.schema.json"

    def _load_schema(self, schema_path: Path) -> dict[str, Any]:
        with schema_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def validate_graph(self, graph: CanonicalThreatModelGraph | dict[str, Any] | None) -> ValidationResult:
        if graph is None:
            return ValidationResult(
                is_valid=False,
                issues=[
                    ValidationIssue(
                        code="CANONICAL_GRAPH_MISSING",
                        message="Canonical graph has not been produced yet.",
                        location="canonical_graph",
                    )
                ],
            )

        if isinstance(graph, CanonicalThreatModelGraph):
            graph_payload = graph.to_dict()
        elif isinstance(graph, dict):
            graph_payload = graph
        else:
            return ValidationResult(
                is_valid=False,
                issues=[
                    ValidationIssue(
                        code="CANONICAL_GRAPH_TYPE_INVALID",
                        message="Canonical graph must use the typed canonical model or a schema-shaped dictionary.",
                        location="canonical_graph",
                    )
                ],
            )

        schema_errors = sorted(self.validator.iter_errors(graph_payload), key=lambda error: list(error.absolute_path))
        issues = [self._issue_from_schema_error(error) for error in schema_errors]
        return ValidationResult(is_valid=not issues, issues=issues)

    def validate(self, state: FrameworkState) -> ValidationResult:
        return self.validate_graph(state.canonical_graph)

    def _issue_from_schema_error(self, error: ValidationError) -> ValidationIssue:
        location = ".".join(str(part) for part in error.absolute_path)
        if not location:
            location = "canonical_graph"

        code = f"SCHEMA_{error.validator.upper()}"
        return ValidationIssue(code=code, message=error.message, location=location)

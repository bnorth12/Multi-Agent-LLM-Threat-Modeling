"""Validation seams for the runtime skeleton."""

from dataclasses import dataclass, field

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
    def validate(self, state: FrameworkState) -> ValidationResult:
        graph = state.canonical_graph

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

        issues: list[ValidationIssue] = []

        if not isinstance(graph, CanonicalThreatModelGraph):
            issues.append(
                ValidationIssue(
                    code="CANONICAL_GRAPH_TYPE_INVALID",
                    message="Canonical graph must use the typed canonical model.",
                    location="canonical_graph",
                )
            )
        else:
            if not graph.metadata.model_level:
                issues.append(
                    ValidationIssue(
                        code="MODEL_LEVEL_MISSING",
                        message="Canonical graph metadata model level is required.",
                        location="metadata.model_level",
                    )
                )

            if not graph.system.name:
                issues.append(
                    ValidationIssue(
                        code="SYSTEM_NAME_MISSING",
                        message="Canonical graph system name is required.",
                        location="system.name",
                    )
                )

            if graph.data_flows is None:
                issues.append(
                    ValidationIssue(
                        code="DATA_FLOWS_MISSING",
                        message="Canonical graph data flows collection is required.",
                        location="data_flows",
                    )
                )

        # TODO: Replace this placeholder with schema-backed validation against
        # docs/schemas/canonical_graph.schema.json once model contracts are wired.
        return ValidationResult(is_valid=not issues, issues=issues)

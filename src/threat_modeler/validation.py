"""Validation seams for the runtime skeleton."""

from dataclasses import dataclass, field
from enum import Enum

from .models import CanonicalThreatModelGraph
from .state import FrameworkState


class ValidationSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    location: str = ""
    severity: ValidationSeverity = ValidationSeverity.CRITICAL


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def critical_issues(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]

    @property
    def has_critical(self) -> bool:
        return any(i.severity == ValidationSeverity.CRITICAL for i in self.issues)


class ValidationHaltError(Exception):
    """Raised when a critical validation failure halts downstream stage execution."""

    def __init__(self, result: ValidationResult, stage_id: str) -> None:
        self.result = result
        self.stage_id = stage_id
        codes = ", ".join(i.code for i in result.critical_issues)
        super().__init__(
            f"Validation halt after stage '{stage_id}': critical issues [{codes}]"
        )


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

"""Validation seams for the runtime skeleton."""

from dataclasses import dataclass, field

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
        if not state.canonical_graph:
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

        # TODO: Replace this placeholder with schema-backed validation against
        # docs/schemas/canonical_graph.schema.json once model contracts are wired.
        return ValidationResult(is_valid=True)

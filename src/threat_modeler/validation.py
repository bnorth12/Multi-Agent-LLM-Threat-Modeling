"""Validation seams for the runtime skeleton."""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

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
    def __init__(self) -> None:
        self._schema = self._load_schema()

    def _load_schema(self) -> dict[str, Any] | None:
        schema_path = Path(__file__).resolve().parents[2] / "docs" / "schemas" / "canonical_graph.schema.json"
        try:
            return json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def _is_int_in_range(value: Any, minimum: int, maximum: int) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum

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
            graph_dict = graph.to_dict()

            if self._schema:
                required_top_level = self._schema.get("required", [])
                for key in required_top_level:
                    if key not in graph_dict:
                        issues.append(
                            ValidationIssue(
                                code="SCHEMA_REQUIRED_FIELD_MISSING",
                                message=f"Canonical graph is missing required top-level field '{key}'.",
                                location=key,
                            )
                        )

            if not graph.metadata.model_level:
                issues.append(
                    ValidationIssue(
                        code="MODEL_LEVEL_MISSING",
                        message="Canonical graph metadata model level is required.",
                        location="metadata.model_level",
                    )
                )
            elif graph.metadata.model_level not in {"system", "subsystem", "component"}:
                issues.append(
                    ValidationIssue(
                        code="MODEL_LEVEL_INVALID",
                        message="Canonical graph metadata model level must be one of: system, subsystem, component.",
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

            valid_interface_types = {
                "component-component",
                "subsystem-subsystem",
                "function-function",
                "external-component",
                "component-external",
                "external-subsystem",
                "subsystem-external",
                "function-component",
                "component-function",
                "human-component",
                "component-human",
            }
            for index, interface in enumerate(graph.interfaces):
                iface_location = f"interfaces[{index}]"
                if interface.interface_type not in valid_interface_types:
                    issues.append(
                        ValidationIssue(
                            code="INTERFACE_TYPE_INVALID",
                            message=(
                                "Interface type must match the canonical schema enumeration."
                            ),
                            location=f"{iface_location}.interface_type",
                        )
                    )

                stride = interface.stride
                for category in ("S", "T", "R", "I", "D", "E"):
                    score = getattr(stride, category, None)
                    if not self._is_int_in_range(score, 0, 5):
                        issues.append(
                            ValidationIssue(
                                code="STRIDE_SCORE_OUT_OF_RANGE",
                                message=f"STRIDE {category} score must be an integer in range [0, 5].",
                                location=f"{iface_location}.stride.{category}",
                            )
                        )

                for threat_index, threat in enumerate(interface.threats):
                    threat_location = f"{iface_location}.threats[{threat_index}]"
                    if not self._is_int_in_range(threat.likelihood, 1, 5):
                        issues.append(
                            ValidationIssue(
                                code="THREAT_LIKELIHOOD_OUT_OF_RANGE",
                                message="Threat likelihood must be an integer in range [1, 5].",
                                location=f"{threat_location}.likelihood",
                            )
                        )
                    if not self._is_int_in_range(threat.impact, 1, 5):
                        issues.append(
                            ValidationIssue(
                                code="THREAT_IMPACT_OUT_OF_RANGE",
                                message="Threat impact must be an integer in range [1, 5].",
                                location=f"{threat_location}.impact",
                            )
                        )

                    for mitigation_index, mitigation in enumerate(threat.mitigations_technical):
                        if not self._is_int_in_range(mitigation.residual_risk_after_control, 1, 5):
                            issues.append(
                                ValidationIssue(
                                    code="TECHNICAL_MITIGATION_RISK_OUT_OF_RANGE",
                                    message="Technical mitigation residual risk must be an integer in range [1, 5].",
                                    location=(
                                        f"{threat_location}.mitigations_technical[{mitigation_index}]"
                                        ".residual_risk_after_control"
                                    ),
                                )
                            )

                    for mitigation_index, mitigation in enumerate(threat.mitigations_administrative):
                        if not self._is_int_in_range(mitigation.residual_risk_after_control, 1, 5):
                            issues.append(
                                ValidationIssue(
                                    code="ADMIN_MITIGATION_RISK_OUT_OF_RANGE",
                                    message="Administrative mitigation residual risk must be an integer in range [1, 5].",
                                    location=(
                                        f"{threat_location}.mitigations_administrative[{mitigation_index}]"
                                        ".residual_risk_after_control"
                                    ),
                                )
                            )

        return ValidationResult(is_valid=not issues, issues=issues)

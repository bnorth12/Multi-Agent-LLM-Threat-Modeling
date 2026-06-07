#!/usr/bin/env python3
"""Local independent repository review.

Traceability evaluation order (authoritative):
1. Establish actual traceability by **content analysis starting from source code**
   (src/, scripts/, frontend/src/, Tests/) to docs/Requirements/Tests/ etc. This ensures
   implemented code is traced and provides the root "ground truth".
2. Evaluate traces **between the other artifacts** (capability hierarchy, functional decomp,
   architecture baselines, design specs, requirement specs, test plans/steps, verification
   artifacts) based on **content** (ID mentions, section references, prose/tables, explicit
   relationships) — independent of the external traceability matrices.
3. Reconcile the external traceability matrices (04/16/Capability_Function_..., etc.)
   against the verified actual traceability from steps 1+2.
All of the above is reported in a **single** independent review (md+json) per run context.

The canonical pair in independent_reviews/latest/ (independent_review_<sprint>_<context>.md + .json)
is tracked and will cause a dirty tree after pre-push/push runs. This is the known, documented
exception (see independent_reviews/README.md and hook install scripts). The is_allowed_generated_review_change
filter and retention policy exist to enforce the single-file + known-churn contract.

Phase 3+ features:
- tighter requirement/issue parsing to reduce false positives
- severity policy thresholds
- branch-awareness with merge-base risk evaluation
- conceptual vs as-built architecture/design gap classification
- trend snapshots and deltas across runs
- optional local GitHub issue reconciliation (explicit opt-in)
- health-based remediation readiness output for sprint planning intake
- source-first + content-inter-artifact + matrix-vs-ground-truth traceability (this file)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from sprint_naming import parse_sprint_token

REQ_ID_CANDIDATE_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]{2,})+)\b")
ISSUE_ID_PATTERN = re.compile(r"^(D-S\d{2}-\d{3}|S\d{2}-\d{3})$")
GITHUB_ISSUE_PATTERN = re.compile(r"#\d+|github\.com/.*/issues/\d+", re.IGNORECASE)
GITHUB_URL_PATTERN = re.compile(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", re.IGNORECASE)
CODE_PATH_PATTERN = re.compile(r"\b(?:src/|frontend/src/|scripts/|Tests/)[\w\-./]+")
TEST_EVIDENCE_PATTERN = re.compile(
    r"\b(?:Tests/|pytest|test_[\w\-./]+\.py|[\w\-./]+(?:\.test|\.spec)\.(?:ts|tsx|js|jsx|py))\b",
    re.IGNORECASE,
)
TEST_FILE_PATH_PATTERN = re.compile(
    r"(?:^|/)(?:test_[\w\-./]+\.py|[\w\-.]+(?:\.test|\.spec)\.(?:ts|tsx|js|jsx|py))$",
    re.IGNORECASE,
)
ARCH_DESIGN_PATH_PATTERN = re.compile(r"\bdocs/(?:architecture|design)/[\w\-./]+")

SOURCE_CODE_GLOBS = [
    "src/**/*.py",
    "scripts/**/*.py",
    "frontend/src/**/*.ts",
    "frontend/src/**/*.tsx",
    "frontend/src/**/*.js",
    "frontend/src/**/*.jsx",
]

TEST_CODE_GLOBS = [
    "Tests/**/*.py",
    "src/**/test_*.py",
    "src/**/*.test.ts",
    "src/**/*.spec.ts",
    "src/**/*.test.tsx",
    "src/**/*.spec.tsx",
    "src/**/*.test.js",
    "src/**/*.spec.js",
    "src/**/*.test.jsx",
    "src/**/*.spec.jsx",
    "frontend/src/**/*.test.ts",
    "frontend/src/**/*.spec.ts",
    "frontend/src/**/*.test.tsx",
    "frontend/src/**/*.spec.tsx",
    "frontend/src/**/*.test.js",
    "frontend/src/**/*.spec.js",
    "frontend/src/**/*.test.jsx",
    "frontend/src/**/*.spec.jsx",
]

ALLOWED_REQ_PREFIXES = {
    "ADM",
    "GUI",
    "HITL",
    "INT",
    "PRJ",
    "PRM",
    "RHMI",
    "RIC",
    "SCR",
    "VS",
}

EXPECTED_PATHS = [
    Path("README.md"),
    Path("requirements.txt"),
    Path("pyproject.toml"),
    Path("src"),
    Path("Requirements"),
    Path("planning"),
    Path("planning/issues"),
    Path("docs/architecture"),
    Path("docs/design"),
    Path("scripts"),
    Path("Tests"),
]

REQUIRED_TRACEABILITY_ARTIFACTS = [
    Path("docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md"),
    Path("docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md"),
    Path("Requirements/15_End_To_End_Traceability_Attributes_Registry.md"),
]

MATRIX_TRACEABILITY_ARTIFACTS = [
    Path("Requirements/04_Traceability_Matrix.md"),
    Path("Requirements/16_Active_Sprint_Traceability_Matrix.md"),
    Path("Requirements/17_Implementation_Trace_Normalization.md"),
    Path("docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md"),
]

TRACEABILITY_BASELINE_ARTIFACTS = [
    Path("Requirements/15_End_To_End_Traceability_Attributes_Registry.md"),
    Path("Requirements/18_Traceability_Governance_Operating_Model.md"),
]

REVIEW_SCHEMA_VERSION = 2
TRACEABILITY_BASELINE_MODE = "matrix-and-ground-truth-v2"
RELATIONSHIP_DIRECTION_MODE = "documentation_vs_ground_truth"
TREND_EPOCH = "taxonomy-direction-v2"

# Governance meta-requirements whose primary "implementation" and "verification" are now the
# CI-enforced governance automation (verify_*.py scripts, governance_autoflow, hooks, the
# independent review itself, populated annexes in design/req docs, and hierarchy backfills).
# These should no longer be treated as "leaf feature requirements missing code".
GOVERNANCE_META_REQUIREMENT_IDS = {
    "ADM-GOV-CONTROLS-L1",
    "C01-ORCH-002-CAP",
    "C01-ORCH-003-CAP",
    "C11-LLM-004-CAP",
    "HITL-TRACEABILITY-L1",
    "INT-TRACEABILITY-L1",
    # Add others that represent control-plane definitions rather than deliverable features.
}

TREND_HISTORY_FILE = Path("independent_reviews/history/snapshot_index.json")
POLICY_PROFILES_FILE = Path("config/independent_review_policy_profiles.json")
REPORT_ARCHIVE_DIR = Path("independent_reviews/history/reports")
REPORT_CONTEXT_ARCHIVE_DIR = Path("independent_reviews/history/reports/by_context")
EXCEPTION_REGISTRY_FILE = Path("config/independent_review_exception_registry.json")


@dataclass
class SeverityPolicy:
    req_impl_threshold: float
    req_verify_threshold: float
    req_arch_threshold: float
    issue_quality_threshold: float
    max_planned_missing_requirement: int


@dataclass
class PolicyProfileConfig:
    profile_name: str
    policy_file: str
    enforce_on: List[str] = field(default_factory=list)
    remediation_health_floor: float = 85.0


@dataclass
class SeveritySummary:
    critical: List[str] = field(default_factory=list)
    major: List[str] = field(default_factory=list)
    minor: List[str] = field(default_factory=list)
    informational: List[str] = field(default_factory=list)


@dataclass
class BranchAwareness:
    current_branch: str
    head_commit: str
    merge_base_with_origin_main: str
    ahead_of_origin_main: int
    behind_origin_main: int
    working_tree_dirty: bool
    merge_risk: str
    merge_risk_reason: str


@dataclass
class IssueRow:
    tracker_file: str
    issue_id: str
    github_ref: str
    status: str
    requirement_ids: Set[str] = field(default_factory=set)
    has_requirement_column: bool = False


@dataclass
class ConceptualAsBuiltGapSummary:
    conceptual_planned_arch_only: List[str] = field(default_factory=list)
    planned_missing_arch_design_trace: List[str] = field(default_factory=list)
    as_built_missing_arch_design_trace: List[str] = field(default_factory=list)


@dataclass
class HierarchyGovernanceSummary:
    sprint_issue_files_total: int = 0
    sprint_issue_files_with_complete_hierarchy: int = 0
    hierarchy_coverage_ratio: float = 0.0
    unique_parent_capability_ids: int = 0
    unique_parent_function_ids: int = 0
    unique_child_function_ids: int = 0
    decomposition_level_counts: Dict[str, int] = field(default_factory=dict)
    phase_counts: Dict[str, int] = field(default_factory=dict)
    parent_capability_fanout: Dict[str, int] = field(default_factory=dict)
    parent_function_fanout: Dict[str, int] = field(default_factory=dict)
    missing_field_rows: List[str] = field(default_factory=list)


@dataclass
class TrendSnapshot:
    timestamp: str
    sprint: str
    score: float
    critical_count: int
    major_count: int
    minor_count: int
    informational_count: int
    req_impl_ratio: float = 0.0
    req_verify_ratio: float = 0.0
    req_arch_ratio: float = 0.0
    full_chain_ratio: float = 0.0
    issue_quality_ratio: float = 0.0
    review_schema_version: int = 1
    traceability_baseline_mode: str = "legacy-line-scan"
    relationship_direction_mode: str = "none"
    trend_epoch: str = "legacy"


@dataclass
class TrendDelta:
    previous_timestamp: str
    score_delta: float
    critical_delta: int
    major_delta: int
    minor_delta: int
    informational_delta: int


@dataclass
class TrendDashboardEntry:
    timestamp: str
    score: float
    critical_count: int
    major_count: int
    minor_count: int
    informational_count: int
    direction: str


@dataclass
class TrendDashboardSummary:
    window: int
    overall_trend: str
    entries: List[TrendDashboardEntry] = field(default_factory=list)


@dataclass
class GitHubIssueReconciliation:
    issue_id: str
    github_ref: str
    github_repo: str
    github_number: str
    local_status: str
    remote_state: str
    status_match: bool
    remote_url: str
    detail: str


@dataclass
class GitHubReconciliationSummary:
    enabled: bool
    checked_count: int
    matched_count: int
    mismatched_count: int
    unresolved_count: int
    unresolved_details: List[str] = field(default_factory=list)


@dataclass
class RemediationTheme:
    title: str = ""
    priority: str = ""
    rationale: str = ""
    dependency_order: str = ""
    starter_actions: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    representative_items: List[str] = field(default_factory=list)
    prefix_breakdown: List[str] = field(default_factory=list)


@dataclass
class RemediationStrategy:
    required: bool = False
    planning_readiness: str = "planning-ready"
    health_floor: float = 85.0
    trigger_reasons: List[str] = field(default_factory=list)
    summary_notes: List[str] = field(default_factory=list)
    themes: List[RemediationTheme] = field(default_factory=list)


@dataclass
class HumanQualityAssessment:
    artifact_set_scores: Dict[str, float] = field(default_factory=dict)
    artifact_set_linkage_notes: Dict[str, List[str]] = field(default_factory=dict)
    onboarding_intuition_score: float = 0.0
    findings: List[str] = field(default_factory=list)
    additional_review_dimensions: List[str] = field(default_factory=list)


@dataclass
class MatrixTruthAlignmentSummary:
    matrix_files: List[str] = field(default_factory=list)
    baseline_truth_sources: List[str] = field(default_factory=list)
    requirement_legs_evaluated: int = 0
    leg_mismatch_count: int = 0
    alignment_ratio: float = 0.0
    declared_impl_without_truth: List[str] = field(default_factory=list)
    declared_verify_without_truth: List[str] = field(default_factory=list)
    declared_arch_without_truth: List[str] = field(default_factory=list)
    truth_impl_missing_matrix: List[str] = field(default_factory=list)
    truth_verify_missing_matrix: List[str] = field(default_factory=list)
    truth_arch_missing_matrix: List[str] = field(default_factory=list)


@dataclass
class ExecutedTestSignal:
    report_path: str = ""
    status: str = "unknown"
    passed: bool = False
    observed_at: str = "unknown"
    age_days: Optional[float] = None
    details: List[str] = field(default_factory=list)


@dataclass
class ReviewResult:
    generated_at: str
    sprint: str
    run_context: str
    review_schema_version: int
    traceability_baseline_mode: str
    relationship_direction_mode: str
    trend_epoch: str
    requirement_descriptions: Dict[str, str]
    requirement_traceability: Dict[str, Dict[str, List[str]]]
    full_trace_chain_count: int
    full_trace_chain_gap_ids: List[str]
    structure_missing: List[str]
    requirement_total: int
    req_with_impl: int
    req_without_impl: List[str]
    req_with_verification: int
    req_without_verification: List[str]
    req_with_arch_design_trace: int
    req_without_arch_design_trace: List[str]
    req_with_aux_verification_only: int
    req_aux_verification_only: List[str]
    issue_rows_total: int
    issue_rows_without_requirements: List[str]
    issue_rows_without_github_ref: List[str]
    planned_rows_missing_requirement: List[str]
    required_traceability_artifacts: List[str]
    traceability_artifact_status: Dict[str, Dict[str, object]]
    traceability_artifacts_missing: List[str]
    traceability_artifacts_unreferenced: List[str]
    full_remediation_complete: bool
    branch_awareness: BranchAwareness
    conceptual_as_built_gaps: ConceptualAsBuiltGapSummary
    hierarchy_governance: HierarchyGovernanceSummary
    policy_profile: PolicyProfileConfig
    severity_policy: SeverityPolicy
    severity_summary: SeveritySummary
    trend_snapshot: TrendSnapshot
    trend_delta: Optional[TrendDelta]
    trend_dashboard: TrendDashboardSummary
    github_reconciliation_summary: GitHubReconciliationSummary
    github_reconciliation_rows: List[GitHubIssueReconciliation]
    matrix_truth_alignment: MatrixTruthAlignmentSummary
    notes: List[str]
    overall_score: float
    issue_quality_ratio: float
    confidence_caps_applied: List[str] = field(default_factory=list)
    executed_test_signal: ExecutedTestSignal = field(default_factory=ExecutedTestSignal)
    health_breakdown: Dict[str, Any] = field(default_factory=dict)
    kpi_delta: Dict[str, float] = field(default_factory=dict)
    remediation_strategy: RemediationStrategy = field(default_factory=RemediationStrategy)
    human_quality: HumanQualityAssessment = field(default_factory=HumanQualityAssessment)
    remediation_obligations: List[RemediationObligationItem] = field(default_factory=list)

    # New fields for Independent Engineering Review Model (holistic per-class + cross-cutting)
    engineering_artifact_classes: Dict[str, Any] = field(default_factory=dict)  # class_name -> {maturity, health, quality, key_findings, scores, ...}
    interface_to_function_decomposition_mappings: List[Dict[str, Any]] = field(default_factory=list)
    documentation_relationship_health: Dict[str, Any] = field(default_factory=dict)
    traceability_matrix_audit: Dict[str, Any] = field(default_factory=dict)
    overall_engineering_health_score: float = 0.0
    engineering_class_summary: Dict[str, float] = field(default_factory=dict)  # class -> maturity or health score


@dataclass
class RemediationObligationItem:
    rule_id: str
    level: str
    finding: str
    owning_plan: str
    due_sprint: str
    rationale: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def run_command(cwd: Path, args: List[str]) -> Tuple[bool, str]:
    proc = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, check=False)
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if proc.returncode != 0:
        return False, err or out
    return True, out


def run_git(root: Path, args: List[str]) -> Tuple[bool, str]:
    return run_command(root, ["git", *args])


def normalize_sprint(raw: str) -> Tuple[str, str]:
    token = parse_sprint_token(raw)
    return token.dash, token.underscore


def load_policy_profiles(root: Path) -> Dict[str, Dict[str, float]]:
    path = root / POLICY_PROFILES_FILE
    if not path.exists():
        raise ValueError(f"Missing policy profile file: {path.as_posix()}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    profiles = raw.get("profiles", {})
    if not profiles:
        raise ValueError(f"Policy profile file has no profiles: {path.as_posix()}")
    return profiles


def build_policy_from_profile(
    root: Path,
    profile_name: str,
    req_impl_threshold: Optional[float],
    req_verify_threshold: Optional[float],
    req_arch_threshold: Optional[float],
    issue_quality_threshold: Optional[float],
    max_planned_missing_requirement: Optional[int],
) -> Tuple[SeverityPolicy, PolicyProfileConfig]:
    profiles = load_policy_profiles(root)
    if profile_name not in profiles:
        available = ", ".join(sorted(profiles.keys()))
        raise ValueError(f"Unknown policy profile '{profile_name}'. Available: {available}")

    base = profiles[profile_name]
    policy = SeverityPolicy(
        req_impl_threshold=float(base.get("req_impl_threshold", 0.70)),
        req_verify_threshold=float(base.get("req_verify_threshold", 0.60)),
        req_arch_threshold=float(base.get("req_arch_threshold", 0.70)),
        issue_quality_threshold=float(base.get("issue_quality_threshold", 0.90)),
        max_planned_missing_requirement=int(base.get("max_planned_missing_requirement", 0)),
    )

    if req_impl_threshold is not None:
        policy.req_impl_threshold = req_impl_threshold
    if req_verify_threshold is not None:
        policy.req_verify_threshold = req_verify_threshold
    if req_arch_threshold is not None:
        policy.req_arch_threshold = req_arch_threshold
    if issue_quality_threshold is not None:
        policy.issue_quality_threshold = issue_quality_threshold
    if max_planned_missing_requirement is not None:
        policy.max_planned_missing_requirement = max_planned_missing_requirement

    profile_meta = PolicyProfileConfig(
        profile_name=profile_name,
        policy_file=POLICY_PROFILES_FILE.as_posix(),
        enforce_on=[str(x).lower() for x in base.get("enforce_on", [])],
        remediation_health_floor=float(base.get("remediation_health_floor", 85.0)),
    )
    return policy, profile_meta


def enforcement_levels_from_mode(
    enforcement_mode: str,
    profile_meta: PolicyProfileConfig,
    manual_levels: str,
) -> List[str]:
    allowed = {"critical", "major", "minor", "informational"}
    if enforcement_mode == "off":
        return []
    if enforcement_mode == "auto":
        return [lvl for lvl in profile_meta.enforce_on if lvl in allowed]
    levels = [item.strip().lower() for item in manual_levels.split(",") if item.strip()]
    return [lvl for lvl in levels if lvl in allowed]


def count_enforcement_violations(severity: SeveritySummary, levels: List[str]) -> int:
    count = 0
    if "critical" in levels:
        count += len(severity.critical)
    if "major" in levels:
        count += len(severity.major)
    if "minor" in levels:
        count += len(severity.minor)
    if "informational" in levels:
        count += len(severity.informational)
    return count


def load_exception_registry(root: Path, path: str) -> Dict[str, Any]:
    registry_path = root / path
    if not registry_path.exists():
        return {"default_enabled": False, "rules": []}
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return {"default_enabled": False, "rules": []}
    if not isinstance(raw, dict):
        return {"default_enabled": False, "rules": []}
    return {
        "default_enabled": bool(raw.get("default_enabled", True)),
        "rules": list(raw.get("rules", [])),
    }


def _level_items(severity: SeveritySummary, level: str) -> List[str]:
    if level == "critical":
        return severity.critical
    if level == "major":
        return severity.major
    if level == "minor":
        return severity.minor
    if level == "informational":
        return severity.informational
    return []


def _rule_applies(rule: Dict[str, Any], level: str, sprint: str, run_context: str) -> bool:
    if not bool(rule.get("enabled", True)):
        return False

    levels = [str(item).lower() for item in rule.get("levels", []) if str(item).strip()]
    if levels and level not in levels:
        return False

    contexts = {str(item) for item in rule.get("contexts", []) if str(item).strip()}
    if contexts and run_context not in contexts:
        return False

    sprints = {str(item).replace("_", "-") for item in rule.get("sprints", []) if str(item).strip()}
    if sprints and sprint.replace("_", "-") not in sprints:
        return False

    return True


def _rule_matches_finding(rule: Dict[str, Any], finding: str) -> bool:
    needles = [str(item) for item in rule.get("contains_any", []) if str(item).strip()]
    if not needles:
        return False
    return any(needle in finding for needle in needles)


def count_enforcement_violations_with_exceptions(
    severity: SeveritySummary,
    levels: List[str],
    registry: Dict[str, Any],
    sprint: str,
    run_context: str,
) -> Tuple[int, int]:
    if not bool(registry.get("default_enabled", True)):
        return count_enforcement_violations(severity, levels), 0

    rules = registry.get("rules", [])
    violations = 0
    excepted = 0
    for level in levels:
        for finding in _level_items(severity, level):
            matched = False
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                if not _rule_applies(rule, level, sprint, run_context):
                    continue
                if _rule_matches_finding(rule, finding):
                    matched = True
                    excepted += 1
                    break
            if not matched:
                violations += 1
    return violations, excepted


def evaluate_enforcement_with_exceptions(
    severity: SeveritySummary,
    levels: List[str],
    registry: Dict[str, Any],
    sprint: str,
    run_context: str,
) -> Tuple[int, List[RemediationObligationItem]]:
    if not bool(registry.get("default_enabled", True)):
        return count_enforcement_violations(severity, levels), []

    rules = registry.get("rules", [])
    violations = 0
    obligations: List[RemediationObligationItem] = []

    for level in levels:
        for finding in _level_items(severity, level):
            matched_rule: Optional[Dict[str, Any]] = None
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                if not _rule_applies(rule, level, sprint, run_context):
                    continue
                if _rule_matches_finding(rule, finding):
                    matched_rule = rule
                    break

            if matched_rule is None:
                violations += 1
                continue

            obligations.append(
                RemediationObligationItem(
                    rule_id=str(matched_rule.get("id", "unlabeled-exception")),
                    level=level,
                    finding=finding,
                    owning_plan=str(
                        matched_rule.get("owning_plan")
                        or matched_rule.get("remediation_plan")
                        or "unspecified"
                    ),
                    due_sprint=str(matched_rule.get("due_sprint", "unspecified")),
                    rationale=str(matched_rule.get("rationale", "No rationale provided.")),
                )
            )

    return violations, obligations


def collect_open_exception_obligations(
    severity: SeveritySummary,
    registry: Dict[str, Any],
    sprint: str,
    run_context: str,
) -> List[RemediationObligationItem]:
    if not bool(registry.get("default_enabled", True)):
        return []

    rules = registry.get("rules", [])
    obligations: List[RemediationObligationItem] = []
    all_levels = ["critical", "major", "minor", "informational"]

    for level in all_levels:
        for finding in _level_items(severity, level):
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                if not _rule_applies(rule, level, sprint, run_context):
                    continue
                if not _rule_matches_finding(rule, finding):
                    continue
                obligations.append(
                    RemediationObligationItem(
                        rule_id=str(rule.get("id", "unlabeled-exception")),
                        level=level,
                        finding=finding,
                        owning_plan=str(
                            rule.get("owning_plan")
                            or rule.get("remediation_plan")
                            or "unspecified"
                        ),
                        due_sprint=str(rule.get("due_sprint", "unspecified")),
                        rationale=str(rule.get("rationale", "No rationale provided.")),
                    )
                )
                break

    return obligations


def remediation_obligation_report_paths(
    out_dir: Path,
    sprint: str,
    run_context: str,
    report_mode: str,
) -> Tuple[Path, Path]:
    if report_mode == "archive":
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        return (
            out_dir / f"remediation_obligations_{sprint}_{run_context}_{stamp}.md",
            out_dir / f"remediation_obligations_{sprint}_{run_context}_{stamp}.json",
        )
    return (
        out_dir / f"remediation_obligations_{sprint}_{run_context}.md",
        out_dir / f"remediation_obligations_{sprint}_{run_context}.json",
    )


def write_remediation_obligation_report(
    out_dir: Path,
    result: ReviewResult,
    obligations: List[RemediationObligationItem],
    review_md_path: Path,
    review_json_path: Path,
    report_mode: str,
) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path, json_path = remediation_obligation_report_paths(
        out_dir=out_dir,
        sprint=result.sprint,
        run_context=result.run_context,
        report_mode=report_mode,
    )

    lines: List[str] = []
    lines.append("# Remediation Obligation Report")
    lines.append("")
    lines.append(f"- Generated: {result.generated_at}")
    lines.append(f"- Sprint Scope: {result.sprint}")
    lines.append(f"- Run Context: {result.run_context}")
    lines.append("- Source Independent Review (Markdown): " + review_md_path.as_posix())
    lines.append("- Source Independent Review (JSON): " + review_json_path.as_posix())
    lines.append(f"- Open Exception Obligations: {len(obligations)}")
    lines.append("")
    lines.append("## Open Exceptions Queue")
    if obligations:
        lines.append("| Rule ID | Severity | Due Sprint | Owning Plan | Finding |")
        lines.append("|---|---|---|---|---|")
        for item in obligations:
            finding = item.finding.replace("|", "\\|")
            owning_plan = item.owning_plan.replace("|", "\\|")
            lines.append(
                f"| {item.rule_id} | {item.level} | {item.due_sprint} | {owning_plan} | {finding} |"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Rationale Notes")
    if obligations:
        rationale_by_rule: Dict[str, str] = {}
        for item in obligations:
            rationale_by_rule.setdefault(item.rule_id, item.rationale)
        for rule_id, rationale in sorted(rationale_by_rule.items()):
            lines.append(f"- {rule_id}: {rationale}")
    else:
        lines.append("- No exception obligations are currently open for this run.")

    payload = {
        "generated_at": result.generated_at,
        "sprint": result.sprint,
        "run_context": result.run_context,
        "source_independent_review_markdown": review_md_path.as_posix(),
        "source_independent_review_json": review_json_path.as_posix(),
        "open_exception_obligations": [asdict(item) for item in obligations],
    }

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return md_path, json_path


def summarize_requirement_prefixes(items: Iterable[str], limit: int = 3) -> List[str]:
    counts: Counter[str] = Counter()
    examples: Dict[str, List[str]] = {}

    for item in items:
        ids = sorted(extract_requirement_ids(item))
        if not ids:
            continue
        req_id = ids[0]
        prefix = req_id.split("-")[0]
        counts[prefix] += 1
        examples.setdefault(prefix, [])
        if req_id not in examples[prefix]:
            examples[prefix].append(req_id)

    lines: List[str] = []
    for prefix, count in counts.most_common(limit):
        sample = ", ".join(examples.get(prefix, [])[:3])
        lines.append(f"{prefix}: {count} item(s)" + (f"; examples: {sample}" if sample else ""))
    return lines


def representative_requirement_ids(items: Iterable[str], limit: int = 5) -> List[str]:
    ids: Set[str] = set()
    for item in items:
        ids.update(extract_requirement_ids(item))
    return sorted(ids)[:limit]


def is_likely_requirement_id(token: str) -> bool:
    if ISSUE_ID_PATTERN.fullmatch(token):
        return False
    parts = token.split("-")
    prefix = parts[0]
    if prefix in ALLOWED_REQ_PREFIXES:
        return True
    if re.fullmatch(r"C\d{2}", prefix):
        return len(parts) >= 3
    return False


def extract_requirement_ids(text: str) -> Set[str]:
    ids: Set[str] = set()
    for token in REQ_ID_CANDIDATE_PATTERN.findall(text):
        if is_likely_requirement_id(token):
            ids.add(token)
    return ids


def extract_requirement_description_from_line(line: str, rid: str) -> str:
    compact = " ".join(line.strip().split())
    if not compact:
        return ""

    if compact.startswith("|") and compact.endswith("|"):
        cells = split_markdown_row(compact)
        for idx, cell in enumerate(cells):
            if rid in cell:
                if idx + 2 < len(cells):
                    requirement_text = cells[idx + 2].strip(" :-")
                    if requirement_text and requirement_text != rid:
                        return requirement_text
                if idx + 1 < len(cells):
                    candidate = cells[idx + 1].strip(" :-")
                    if candidate and candidate != rid:
                        return candidate
                break

    candidate = compact
    candidate = re.sub(rf"\b{re.escape(rid)}\b", "", candidate)
    candidate = candidate.strip(" :-|\t")
    return candidate


def build_requirement_descriptions(root: Path, requirement_ids: Set[str]) -> Dict[str, str]:
    descriptions: Dict[str, str] = {}
    scores: Dict[str, int] = {}
    requirement_files = sorted((root / "Requirements").glob("**/*.md"))

    for path in requirement_files:
        text = read_text(path)
        for line in text.splitlines():
            scoped = extract_requirement_ids(line).intersection(requirement_ids)
            if not scoped:
                continue
            for rid in sorted(scoped):
                candidate = extract_requirement_description_from_line(line, rid)
                if len(candidate) < 8:
                    continue

                score = 0
                lowered = candidate.lower()
                if "shall" in lowered:
                    score += 6
                if compact_line := " ".join(line.strip().split()):
                    if compact_line.startswith("|") and compact_line.endswith("|"):
                        score += 3
                    if compact_line.startswith(">"):
                        score -= 4
                if len(candidate) >= 40:
                    score += 2
                if candidate.lower().startswith("see "):
                    score -= 2

                if score >= scores.get(rid, -999):
                    descriptions[rid] = candidate
                    scores[rid] = score

    return descriptions


def humanize_requirement_reference(item: str, descriptions: Dict[str, str]) -> str:
    ids = sorted(extract_requirement_ids(item))
    if not ids:
        return item

    rid = ids[0]
    description = descriptions.get(rid, "").strip()
    if not description:
        return item

    if item.strip() == rid:
        return f"{rid}: {description}"
    return f"{item} ({description})"


def scan_requirement_corpus(root: Path) -> Dict[str, Set[str]]:
    result: Dict[str, Set[str]] = {}
    for path in sorted((root / "Requirements").glob("**/*.md")):
        for rid in extract_requirement_ids(read_text(path)):
            result.setdefault(rid, set()).add(path.as_posix())
    return result


def scan_evidence_files(root: Path) -> List[Path]:
    candidates = [
        root / "Requirements/04_Traceability_Matrix.md",
        root / "Requirements/15_End_To_End_Traceability_Attributes_Registry.md",
        root / "Requirements/16_Active_Sprint_Traceability_Matrix.md",
        root / "Requirements/17_Implementation_Trace_Normalization.md",
        root / "planning/Traceability_Delta_Appendix_Sprint_2026_11.md",
    ]
    candidates.extend(sorted((root / "planning").glob("Traceability_Delta_Appendix_*.md")))
    candidates.extend(sorted((root / "planning/issues").glob("Sprint_*_Issue_Tracker.md")))
    return [p for p in candidates if p.exists()]


def scan_matrix_traceability_files(root: Path) -> List[Path]:
    return [root / path for path in MATRIX_TRACEABILITY_ARTIFACTS if (root / path).exists()]


def build_requirement_traceability(
    root: Path,
    requirements: Set[str],
    requirement_index: Dict[str, Set[str]],
    files: Iterable[Path],
) -> Dict[str, Dict[str, List[str]]]:
    trace: Dict[str, Dict[str, List[str]]] = {
        rid: {
            "source_refs": sorted(requirement_index.get(rid, set())),
            "architecture_refs": [],
            "implementation_refs": [],
            "verification_refs": [],
            "implementation_repo_refs": [],
            "implementation_aux_refs": [],
            "verification_executable_refs": [],
            "verification_aux_refs": [],
        }
        for rid in sorted(requirements)
    }

    for path in files:
        text = read_text(path)
        for line in text.splitlines():
            scoped_ids = extract_requirement_ids(line).intersection(requirements)
            if not scoped_ids:
                continue

            code_refs = CODE_PATH_PATTERN.findall(line)
            test_refs = TEST_EVIDENCE_PATTERN.findall(line)
            arch_refs = ARCH_DESIGN_PATH_PATTERN.findall(line)

            # Treat test/spec source paths as verification evidence even when they
            # are listed under frontend/src or src path prefixes.
            for ref in code_refs:
                if TEST_FILE_PATH_PATTERN.search(ref):
                    test_refs.append(ref)

            for rid in scoped_ids:
                if code_refs:
                    trace[rid]["implementation_refs"].extend(code_refs)
                if test_refs:
                    trace[rid]["verification_refs"].extend(test_refs)
                if arch_refs:
                    trace[rid]["architecture_refs"].extend(arch_refs)

    for path in sorted((root / "docs/architecture").glob("**/*.md")):
        scoped = extract_requirement_ids(read_text(path)).intersection(requirements)
        for rid in scoped:
            trace[rid]["architecture_refs"].append(path.as_posix())

    for path in sorted((root / "docs/design").glob("**/*.md")):
        scoped = extract_requirement_ids(read_text(path)).intersection(requirements)
        for rid in scoped:
            trace[rid]["architecture_refs"].append(path.as_posix())

    for rid in trace:
        for key in [
            "source_refs",
            "architecture_refs",
            "implementation_refs",
            "verification_refs",
            "implementation_repo_refs",
            "implementation_aux_refs",
            "verification_executable_refs",
            "verification_aux_refs",
        ]:
            trace[rid][key] = sorted(set(trace[rid][key]))

    return trace


def evaluate_matrix_truth_alignment(
    requirements: Set[str],
    matrix_traceability: Dict[str, Dict[str, List[str]]],
    ground_truth_traceability: Dict[str, Dict[str, List[str]]],
    matrix_files: List[Path],
) -> MatrixTruthAlignmentSummary:
    declared_impl_without_truth: List[str] = []
    declared_verify_without_truth: List[str] = []
    declared_arch_without_truth: List[str] = []
    truth_impl_missing_matrix: List[str] = []
    truth_verify_missing_matrix: List[str] = []
    truth_arch_missing_matrix: List[str] = []

    mismatch_count = 0
    evaluated_legs = len(requirements) * 3

    for rid in sorted(requirements):
        matrix_trace = matrix_traceability.get(rid, {})
        truth_trace = ground_truth_traceability.get(rid, {})

        declared_impl = bool(matrix_trace.get("implementation_refs"))
        declared_verify = bool(matrix_trace.get("verification_refs"))
        declared_arch = bool(matrix_trace.get("architecture_refs"))

        truth_impl = bool(truth_trace.get("implementation_repo_refs"))
        truth_verify = bool(truth_trace.get("verification_executable_refs"))
        truth_arch = bool(truth_trace.get("architecture_refs"))

        if declared_impl != truth_impl:
            mismatch_count += 1
            if declared_impl and not truth_impl:
                declared_impl_without_truth.append(rid)
            elif truth_impl and not declared_impl:
                truth_impl_missing_matrix.append(rid)

        if declared_verify != truth_verify:
            mismatch_count += 1
            if declared_verify and not truth_verify:
                declared_verify_without_truth.append(rid)
            elif truth_verify and not declared_verify:
                truth_verify_missing_matrix.append(rid)

        if declared_arch != truth_arch:
            mismatch_count += 1
            if declared_arch and not truth_arch:
                declared_arch_without_truth.append(rid)
            elif truth_arch and not declared_arch:
                truth_arch_missing_matrix.append(rid)

    ratio = 1.0
    if evaluated_legs > 0:
        ratio = max(0.0, 1.0 - (mismatch_count / evaluated_legs))

    return MatrixTruthAlignmentSummary(
        matrix_files=[path.as_posix() for path in matrix_files],
        baseline_truth_sources=[item.as_posix() for item in TRACEABILITY_BASELINE_ARTIFACTS]
        + [
            "Requirements/**/*.md",
            "docs/architecture/**/*.md",
            "docs/design/**/*.md",
            "src/**, scripts/**, frontend/src/**",
            "Tests/** and executable test/spec files",
        ],
        requirement_legs_evaluated=evaluated_legs,
        leg_mismatch_count=mismatch_count,
        alignment_ratio=round(ratio, 4),
        declared_impl_without_truth=sorted(declared_impl_without_truth),
        declared_verify_without_truth=sorted(declared_verify_without_truth),
        declared_arch_without_truth=sorted(declared_arch_without_truth),
        truth_impl_missing_matrix=sorted(truth_impl_missing_matrix),
        truth_verify_missing_matrix=sorted(truth_verify_missing_matrix),
        truth_arch_missing_matrix=sorted(truth_arch_missing_matrix),
    )


def apply_matrix_truth_alignment_findings(
    severity: SeveritySummary,
    matrix_alignment: MatrixTruthAlignmentSummary,
) -> None:
    if matrix_alignment.declared_impl_without_truth:
        severity.major.append(
            "Matrix declares implementation links not backed by repository implementation artifacts: "
            f"{len(matrix_alignment.declared_impl_without_truth)} requirement(s)."
        )

    if matrix_alignment.declared_verify_without_truth:
        severity.major.append(
            "Matrix declares verification links not backed by executable test artifacts: "
            f"{len(matrix_alignment.declared_verify_without_truth)} requirement(s)."
        )

    if matrix_alignment.declared_arch_without_truth:
        severity.minor.append(
            "Matrix declares architecture/design links that are not found in scanned architecture/design evidence: "
            f"{len(matrix_alignment.declared_arch_without_truth)} requirement(s)."
        )

    if matrix_alignment.truth_impl_missing_matrix:
        severity.minor.append(
            "Implementation ground truth exists but is missing from matrix declarations: "
            f"{len(matrix_alignment.truth_impl_missing_matrix)} requirement(s)."
        )

    if matrix_alignment.truth_verify_missing_matrix:
        severity.minor.append(
            "Executable verification ground truth exists but is missing from matrix declarations: "
            f"{len(matrix_alignment.truth_verify_missing_matrix)} requirement(s)."
        )

    if matrix_alignment.truth_arch_missing_matrix:
        severity.informational.append(
            "Architecture/design ground truth exists but is missing from matrix declarations: "
            f"{len(matrix_alignment.truth_arch_missing_matrix)} requirement(s)."
        )

    if matrix_alignment.alignment_ratio < 0.90:
        severity.major.append(
            "Matrix-to-ground-truth alignment ratio is below 0.90: "
            f"{matrix_alignment.alignment_ratio:.2f}."
        )
    elif matrix_alignment.alignment_ratio < 0.97:
        severity.minor.append(
            "Matrix-to-ground-truth alignment ratio is below 0.97: "
            f"{matrix_alignment.alignment_ratio:.2f}."
        )


def format_requirement_chain_line(rid: str, result: "ReviewResult") -> str:
    trace = result.requirement_traceability.get(
        rid,
        {
            "source_refs": [],
            "architecture_refs": [],
            "implementation_refs": [],
            "verification_refs": [],
        },
    )
    desc = result.requirement_descriptions.get(rid, "").strip()

    missing: List[str] = []
    if not trace.get("source_refs"):
        missing.append("source")
    if not trace.get("architecture_refs"):
        missing.append("architecture/design")
    if not trace.get("implementation_repo_refs"):
        missing.append("implementation")
    if not trace.get("verification_executable_refs"):
        missing.append("verification")

    source_preview = ", ".join(trace.get("source_refs", [])[:1]) or "none"
    arch_preview = ", ".join(trace.get("architecture_refs", [])[:2]) or "none"
    impl_preview = ", ".join(trace.get("implementation_repo_refs", [])[:2]) or "none"
    verify_preview = ", ".join(trace.get("verification_executable_refs", [])[:2]) or "none"

    head = f"{rid}: {desc}" if desc else rid
    return (
        f"{head} | missing: {', '.join(missing) if missing else 'none'}"
        f" | source: {source_preview}"
        f" | arch: {arch_preview}"
        f" | impl(repo): {impl_preview}"
        f" | verify(executable): {verify_preview}"
    )


def classify_repo_evidence(
    root: Path,
    requirements: Set[str],
    requirement_traceability: Dict[str, Dict[str, List[str]]],
) -> Tuple[Set[str], Set[str], Set[str]]:
    impl: Set[str] = set()
    verify: Set[str] = set()
    verify_aux_only: Set[str] = set()

    root_abs = root.resolve()
    for rid in sorted(requirements):
        trace = requirement_traceability.get(rid, {})
        impl_refs = trace.get("implementation_refs", [])
        verify_refs = trace.get("verification_refs", [])

        for ref in impl_refs:
            candidate = ref.strip().lstrip("./")
            full = (root / Path(candidate)).resolve()
            if full.exists() and full.is_file() and str(full).startswith(str(root_abs)):
                rel = full.relative_to(root_abs).as_posix()
                if TEST_FILE_PATH_PATTERN.search(rel):
                    trace.setdefault("verification_executable_refs", []).append(rel)
                    verify.add(rid)
                elif Path(rel).suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx"} and (
                    rel.startswith("src/")
                    or rel.startswith("scripts/")
                    or rel.startswith("frontend/src/")
                ):
                    trace.setdefault("implementation_repo_refs", []).append(rel)
                    impl.add(rid)
                else:
                    trace.setdefault("implementation_aux_refs", []).append(ref)
            else:
                trace.setdefault("implementation_aux_refs", []).append(ref)

        for ref in verify_refs:
            candidate = ref.strip().lstrip("./")
            full = (root / Path(candidate)).resolve()
            if (
                full.exists()
                and full.is_file()
                and str(full).startswith(str(root_abs))
                and TEST_FILE_PATH_PATTERN.search(candidate)
            ):
                rel = full.relative_to(root_abs).as_posix()
                trace.setdefault("verification_executable_refs", []).append(rel)
                verify.add(rid)
            else:
                trace.setdefault("verification_aux_refs", []).append(ref)

    for glob in SOURCE_CODE_GLOBS:
        for path in sorted(root.glob(glob)):
            if not path.is_file():
                continue
            text = read_text(path)
            scoped = extract_requirement_ids(text).intersection(requirements)
            if not scoped:
                continue
            rel = path.resolve().relative_to(root_abs).as_posix()
            for rid in scoped:
                requirement_traceability[rid].setdefault("implementation_repo_refs", []).append(rel)
                impl.add(rid)

    for glob in TEST_CODE_GLOBS:
        for path in sorted(root.glob(glob)):
            if not path.is_file():
                continue
            text = read_text(path)
            scoped = extract_requirement_ids(text).intersection(requirements)
            if not scoped:
                continue
            rel = path.resolve().relative_to(root_abs).as_posix()
            for rid in scoped:
                requirement_traceability[rid].setdefault("verification_executable_refs", []).append(rel)
                verify.add(rid)

    for rid in sorted(requirements):
        trace = requirement_traceability.get(rid, {})
        for key in [
            "implementation_repo_refs",
            "implementation_aux_refs",
            "verification_executable_refs",
            "verification_aux_refs",
        ]:
            trace[key] = sorted(set(trace.get(key, [])))
        if trace.get("verification_aux_refs") and not trace.get("verification_executable_refs"):
            verify_aux_only.add(rid)

    return impl, verify, verify_aux_only


def collect_requirement_evidence(root: Path, requirements: Set[str], files: Iterable[Path]) -> Tuple[Set[str], Set[str], Set[str]]:
    impl: Set[str] = set()
    verify: Set[str] = set()
    arch_design: Set[str] = set()

    for path in files:
        text = read_text(path)
        for line in text.splitlines():
            scoped_ids = extract_requirement_ids(line).intersection(requirements)
            if not scoped_ids:
                continue
            if CODE_PATH_PATTERN.search(line):
                impl.update(scoped_ids)
            if TEST_EVIDENCE_PATTERN.search(line):
                verify.update(scoped_ids)
            if ARCH_DESIGN_PATH_PATTERN.search(line):
                arch_design.update(scoped_ids)

    for path in sorted((root / "docs/architecture").glob("**/*.md")):
        arch_design.update(extract_requirement_ids(read_text(path)).intersection(requirements))
    for path in sorted((root / "docs/design").glob("**/*.md")):
        arch_design.update(extract_requirement_ids(read_text(path)).intersection(requirements))

    return impl, verify, arch_design


def split_markdown_row(line: str) -> List[str]:
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    return [cell.strip() for cell in raw.split("|")]


def is_divider_row(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and all(ch in "|-: " for ch in stripped)


def parse_issue_tracker_rows(path: Path, known_requirements: Set[str]) -> List[IssueRow]:
    lines = read_text(path).splitlines()
    rows: List[IssueRow] = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not (line.startswith("|") and line.endswith("|")):
            i += 1
            continue

        if i + 1 >= len(lines) or not is_divider_row(lines[i + 1]):
            i += 1
            continue

        headers = [h.lower() for h in split_markdown_row(lines[i])]
        header_map = {name: idx for idx, name in enumerate(headers)}

        id_idx = header_map.get("id")
        github_idx = header_map.get("github issue")
        status_idx = header_map.get("status")
        req_idx = header_map.get("related requirements")

        has_min_columns = id_idx is not None and github_idx is not None and status_idx is not None
        if not has_min_columns:
            i += 1
            continue

        has_requirement_column = req_idx is not None

        i += 2
        while i < len(lines):
            row_line = lines[i].strip()
            if not (row_line.startswith("|") and row_line.endswith("|")):
                break
            if is_divider_row(row_line):
                i += 1
                continue

            cells = split_markdown_row(row_line)
            if id_idx >= len(cells) or github_idx >= len(cells) or status_idx >= len(cells):
                i += 1
                continue

            issue_id = cells[id_idx]
            if not ISSUE_ID_PATTERN.fullmatch(issue_id):
                i += 1
                continue

            github_ref = cells[github_idx]
            status = cells[status_idx]
            reqs: Set[str] = set()
            if has_requirement_column and req_idx is not None and req_idx < len(cells):
                reqs = extract_requirement_ids(cells[req_idx]).intersection(known_requirements)

            rows.append(
                IssueRow(
                    tracker_file=path.as_posix(),
                    issue_id=issue_id,
                    github_ref=github_ref,
                    status=status,
                    requirement_ids=reqs,
                    has_requirement_column=has_requirement_column,
                )
            )
            i += 1

    return rows


def compute_score(
    structure_ok_ratio: float,
    req_impl_ratio: float,
    req_verify_ratio: float,
    req_arch_ratio: float,
    issue_quality_ratio: float,
    confidence_cap: Optional[float] = None,
    governance_penalty: float = 0.0,
) -> float:
    weighted = (
        0.1 * structure_ok_ratio
        + 0.3 * req_impl_ratio
        + 0.35 * req_verify_ratio
        + 0.15 * req_arch_ratio
        + 0.1 * issue_quality_ratio
    )
    score = (weighted * 100.0) - max(0.0, governance_penalty)
    if confidence_cap is not None:
        score = min(score, confidence_cap)
    return round(max(0.0, min(100.0, score)), 1)


def compute_governance_penalty(severity: "SeveritySummary", issue_rows_total: int) -> float:
    penalty = 0.0
    penalty += len(severity.critical) * 20.0
    penalty += len(severity.major) * 10.0
    penalty += len(severity.minor) * 2.0
    penalty += len(severity.informational) * 0.5
    if issue_rows_total == 0:
        # No parsed tracker rows means issue-governance checks are effectively blind.
        penalty += 5.0
    return min(penalty, 40.0)


def compute_health_breakdown(
    structure_ok_ratio: float,
    req_impl_ratio: float,
    req_verify_ratio: float,
    req_arch_ratio: float,
    issue_quality_ratio: float,
    confidence_cap: Optional[float],
    confidence_caps_applied: List[str],
    severity: "SeveritySummary",
    issue_rows_total: int,
) -> Dict[str, Any]:
    component_points = {
        "structure_integrity": round(0.1 * structure_ok_ratio * 100.0, 2),
        "implementation_coverage": round(0.3 * req_impl_ratio * 100.0, 2),
        "verification_executable_coverage": round(0.35 * req_verify_ratio * 100.0, 2),
        "architecture_design_traceability": round(0.15 * req_arch_ratio * 100.0, 2),
        "issue_governance_quality": round(0.1 * issue_quality_ratio * 100.0, 2),
    }
    base_score = round(sum(component_points.values()), 2)
    penalty_components = {
        "critical_findings": round(len(severity.critical) * 20.0, 2),
        "major_findings": round(len(severity.major) * 10.0, 2),
        "minor_findings": round(len(severity.minor) * 2.0, 2),
        "informational_findings": round(len(severity.informational) * 0.5, 2),
        "no_tracker_rows": 5.0 if issue_rows_total == 0 else 0.0,
    }
    raw_penalty = round(sum(penalty_components.values()), 2)
    penalty_capped = round(min(raw_penalty, 40.0), 2)
    final_uncapped = round(max(0.0, min(100.0, base_score - penalty_capped)), 1)
    final_score = final_uncapped
    if confidence_cap is not None:
        final_score = round(min(final_uncapped, confidence_cap), 1)
    return {
        "component_points": component_points,
        "base_score": base_score,
        "penalty_components": penalty_components,
        "penalty_raw": raw_penalty,
        "penalty_capped": penalty_capped,
        "confidence_cap": confidence_cap,
        "confidence_caps_applied": confidence_caps_applied,
        "final_uncapped": final_uncapped,
        "final_score": final_score,
    }


# =============================================================================
# Independent Engineering Review Model helpers (new holistic analysis per model doc)
# =============================================================================

ENGINEERING_ARTIFACT_CLASS_FILES = {
    "Capability Hierarchy": ["docs/architecture/Capability_Hierarchy_Baseline.md"],
    "Functional Decomposition": [
        "docs/architecture/Multi_Agent_Functional_Decomposition.md",
        "docs/architecture/Function_Hierarchy_Registry.md",
    ],
    "Architecture": [
        "docs/architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md",
        "docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md",
    ],
    "Design": [
        "docs/design/software/Runtime_And_Orchestration_Design_Specification.md",
        "docs/design/software/Agent_Subsystem_Design_Specification.md",
        "docs/design/software/Export_And_Evidence_Packaging_Design_Specification.md",
        "docs/design/software/Model_Configuration_Design_Specification.md",
        "docs/design/software/Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md",
        "docs/design/system/External_Interface_And_Integration_Design_Package.md",
        "docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md",
        "docs/design/system/System_Deployment_And_Operating_Modes_Design.md",
    ],
    "Requirements": [
        "Requirements/01_Project_Requirements.md",
        "Requirements/02_Interface_Requirements.md",
        "Requirements/03_HITL_Requirements.md",
        "Requirements/05_Verification_Strategy.md",
        "Requirements/06_Project_Administration_Requirements.md",
        "Requirements/10_GUI_Requirements.md",
        "Requirements/13_Runtime_State_And_Input_Contract_Requirements.md",
        "Requirements/14_Prompt_Requirements_Baseline.md",
    ],
    "Interfaces & ICDs": [
        "docs/architecture/Multi_Agent_Interface_Control_Document.md",
        "docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md",
        "docs/design/system/External_Interface_And_Integration_Design_Package.md",
    ],
    "Implementation": [],  # analyzed via cross-refs in annexes + source globs
    "Verification & Evidence": [
        "Requirements/05_Verification_Strategy.md",
        "Tests/Formal_Qualification_Test_Plan.md",
    ],
}

def _count_populated_annex_sections(text: str) -> Dict[str, int]:
    """Count non-_None sections in a Traceability Annex."""
    sections = ["Derived From", "Allocated To", "Refines", "Satisfied By", "Verified By", "Depends On",
                "Satisfies", "Realizes", "Provides / Requires", "Implemented By"]
    populated = 0
    empty = 0
    for sec in sections:
        if f"### {sec}" in text:
            # Look for the next _None after the header
            idx = text.find(f"### {sec}")
            following = text[idx:idx+400] if idx != -1 else ""
            if "_None recorded._" in following:
                empty += 1
            else:
                populated += 1
    total = populated + empty
    return {
        "populated": populated,
        "empty": empty,
        "total_sections_found": total,
        "fidelity_ratio": round(populated / max(1, total), 3),
    }

def analyze_engineering_annexes(root: Path) -> Dict[str, Any]:
    """Analyze populated annex content for documentation relationships (INCOSE)."""
    analysis: Dict[str, Any] = {}
    for class_name, files in ENGINEERING_ARTIFACT_CLASS_FILES.items():
        class_data = {"files_analyzed": [], "annex_fidelity": {}, "populated_relationships": 0, "empty_relationships": 0, "key_examples": []}
        for f in files:
            p = root / f
            if p.exists():
                txt = read_text(p)
                if "## Traceability Annex" in txt:
                    class_data["files_analyzed"].append(f)
                    sec_stats = _count_populated_annex_sections(txt)
                    class_data["annex_fidelity"][f] = sec_stats
                    class_data["populated_relationships"] += sec_stats.get("populated", 0)
                    class_data["empty_relationships"] += sec_stats.get("empty", 0)
                    # crude extraction of non-None lines for examples
                    for line in txt.splitlines():
                        if "Satisfies" in line or "Realizes" in line or "Implemented By" in line or "Verified By" in line:
                            if "_None" not in line and len(line) > 10:
                                class_data["key_examples"].append(line.strip()[:120])
                                break
        if class_data["files_analyzed"]:
            total_rel = class_data["populated_relationships"] + class_data["empty_relationships"]
            class_data["overall_fidelity"] = round(class_data["populated_relationships"] / max(1, total_rel), 3)
            analysis[class_name] = class_data
    return analysis

def analyze_interface_function_decomposition_mappings(root: Path) -> List[Dict[str, Any]]:
    """Map interfaces (from ICD + data flow) to functional decomposition abstraction levels (L0-L4)."""
    mappings: List[Dict[str, Any]] = []
    icd_path = root / "docs/architecture/Multi_Agent_Interface_Control_Document.md"
    flow_path = root / "docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md"
    decomp_path = root / "docs/architecture/Multi_Agent_Functional_Decomposition.md"

    decomp_text = read_text(decomp_path) if decomp_path.exists() else ""
    l_levels = ["L0", "L1", "L2", "L3", "L4"]
    function_ids = re.findall(r"\b(F-L0|F[0-9]{3}|F-L[0-9]|M[0-9]|F2[0-9]{2})\b", decomp_text)

    for p, label in [(icd_path, "ICD"), (flow_path, "Data Flow Package")]:
        if p.exists():
            txt = read_text(p)
            for lvl in l_levels:
                if lvl in txt:
                    # crude association: nearby function or interface mention
                    mappings.append({
                        "source": label,
                        "abstraction_level": lvl,
                        "example_context": [line.strip() for line in txt.splitlines() if lvl in line][:2],
                        "linked_functions": [fid for fid in function_ids if fid in txt][:5],
                    })
    # dedup / enrich
    seen = set()
    unique = []
    for m in mappings:
        key = (m["source"], m["abstraction_level"])
        if key not in seen:
            seen.add(key)
            unique.append(m)
    return unique

def compute_documentation_relationship_health(annex_analysis: Dict[str, Any]) -> Dict[str, Any]:
    total_pop = sum(d.get("populated_relationships", 0) for d in annex_analysis.values())
    total_empty = sum(d.get("empty_relationships", 0) for d in annex_analysis.values())
    ratio = round(total_pop / max(1, total_pop + total_empty), 3)
    return {
        "overall_populated_relationships": total_pop,
        "overall_empty_relationships": total_empty,
        "documentation_relationship_fidelity": ratio,
        "classes_with_strong_annexes": [k for k, v in annex_analysis.items() if v.get("overall_fidelity", 0) > 0.6],
        "classes_needing_annex_improvement": [k for k, v in annex_analysis.items() if v.get("overall_fidelity", 0) <= 0.6],
    }

def perform_traceability_matrix_audit_vs_engineering(
    annex_analysis: Dict[str, Any],
    existing_matrix_alignment: "MatrixTruthAlignmentSummary",
    root: Path,
) -> Dict[str, Any]:
    """Audit matrices against actual annex content + engineering reality (beyond old ground-truth)."""
    engineering_gaps = []
    for class_name, data in annex_analysis.items():
        if data.get("empty_relationships", 0) > data.get("populated_relationships", 0):
            engineering_gaps.append(f"{class_name}: more empty than populated annex relationships (documentation gap)")
    matrix_gaps = {
        "impl_under_documented_in_matrices": len(getattr(existing_matrix_alignment, "truth_impl_missing_matrix", [])),
        "verify_under_documented_in_matrices": len(getattr(existing_matrix_alignment, "truth_verify_missing_matrix", [])),
    }
    return {
        "engineering_gaps_identified": engineering_gaps[:10],
        "matrix_vs_engineering_discrepancies": matrix_gaps,
        "recommendation": "Prioritize populating remaining annex relationships and syncing matrices to actual documentation/impl/verify content.",
        "alignment_ratio_from_model": existing_matrix_alignment.alignment_ratio if hasattr(existing_matrix_alignment, "alignment_ratio") else 0.0,
    }


def generate_suggested_matrix_additions(
    annex_analysis: Dict[str, Any],
    requirement_traceability: Dict[str, Dict[str, List[str]]],
    root: Path,
    under_documented_impl: List[str],
    under_documented_verify: List[str],
) -> Dict[str, List[Dict[str, str]]]:
    """
    Generate suggested row additions for key traceability matrices based on annex content + source analysis.
    Focuses on items that have good ground truth (populated annexes + real impl/verify) but are under-documented in matrices.
    Returns suggestions grouped by target matrix.
    """
    suggestions: Dict[str, List[Dict[str, str]]] = {
        "Capability_Function_Architecture_Traceability_Matrix.md": [],
        "15_End_To_End_Traceability_Attributes_Registry.md": [],
        "16_Active_Sprint_Traceability_Matrix.md": [],
    }

    # Use annex_analysis for classes with good fidelity
    for class_name, data in annex_analysis.items():
        fidelity = data.get("overall_fidelity", 0.0)
        if fidelity < 0.7:
            continue  # only suggest for well-populated annex classes

        key_examples = data.get("key_examples", [])
        files = data.get("files_analyzed", [])
        populated = data.get("populated_relationships", 0)

        # Heuristic: for governance classes, suggest to Capability matrix and 15_
        if "Capability" in class_name or "ORCH" in class_name or "HITL" in class_name or "LLM" in class_name or "INT" in class_name or "ADM" in class_name:
            for ex in key_examples[:3]:
                # Parse rough cap/func/req from example or class
                cap_id = "C01-ORCH-001" if "ORCH" in class_name else ("C12-HITL-001" if "HITL" in class_name else ("C11-LLM-001" if "LLM" in class_name else "C18-ADM-001" if "ADM" in class_name else "C15-INT-001"))
                func_level = "L2"
                func_id = "F-ORCH-STATE-TRANSITIONS" if "ORCH" in class_name else "F-HITL-GATE-CONTROL" if "HITL" in class_name else "F-C11_LLM_004-TRACE-L2" if "LLM" in class_name else "F-ADM-GOV-CONTROLS-L2"
                arch_elem = "Orchestrator runtime control plane / " + files[0] if files else "See annex"
                gov_reqs = "C01-ORCH-001, INT-005" if "ORCH" in class_name else "HITL-001, HITL-009, GUI-032"

                suggestions["Capability_Function_Architecture_Traceability_Matrix.md"].append({
                    "Capability ID": cap_id,
                    "Function Level": func_level,
                    "Function ID": func_id,
                    "Architecture Element(s)": arch_elem,
                    "Governing Requirement IDs": gov_reqs,
                    "Notes": f"Suggested from annex analysis (fidelity {fidelity:.2f}, {populated} populated rels). Source: {ex[:80]}... Ground truth in annex + {files[0] if files else 'code'}. Add to matrix to close impl-doc-gap.",
                })

            # Suggest to 15_ for full chain
            suggestions["15_End_To_End_Traceability_Attributes_Registry.md"].append({
                "Slice ID": "SUGGESTED-FROM-ANNEX-" + class_name.replace(" ", "-")[:20],
                "Capability ID": cap_id,
                "Function ID": func_id,
                "Requirement ID": gov_reqs.split(",")[0].strip(),
                "Architecture Artifact": files[0] if files else "docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md",
                "Design Artifact": "docs/design/software/Runtime_And_Orchestration_Design_Specification.md",
                "Source File Path": "scripts/independent_repo_review.py" if "review" in str(files) else (files[0] if files else "src/threat_modeler/orchestrator.py"),
                "Verification Artifact": "Tests/integration/test_validation_gates.py; independent_reviews/latest/independent_review_*.md (annex analysis)",
                "Test Artifact ID": "TST-SUGGESTED-ANNEX",
                "Test Level": "Governance",
                "Audit Rationale": f"Ground truth from populated annex in {class_name} (fidelity {fidelity:.2f}). Implementation and verification exist in code + tests + annex content. Matrix was missing this; add to close 'Ground Truth Present But Missing In Matrix' gap.",
            })

    # Also suggest for specific under-documented feature items (from previous gaps like GUI, PRJ, INT)
    for rid in under_documented_impl[:5] + under_documented_verify[:5]:
        if "GUI" in rid or "PRJ" in rid or "INT" in rid or "RHMI" in rid:
            suggestions["16_Active_Sprint_Traceability_Matrix.md"].append({
                "Slice ID": "SUGGESTED-" + rid[:30],
                "Capability ID": "C13-UI-001" if "GUI" in rid or "RHMI" in rid else "C16-PRJ-001",
                "Function ID": "F-S12-xxx" if "GUI" in rid else "F-PRJ-xxx",
                "Requirement ID": rid.split(":")[0] if ":" in rid else rid,
                "Architecture Artifact": "docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md",
                "Design Artifact": "docs/design/software/Agent_Subsystem_Design_Specification.md or Runtime_And_Orchestration_Design_Specification.md",
                "Source File Path": "frontend/src/App.tsx or src/threat_modeler/..." ,
                "Verification Artifact": "Tests/e2e/test_browser_run_validation.py or Tests/integration/test_results_export_quick_preview.py",
                "Audit Rationale": f"Ground truth (annex + source impl + tests) exists for {rid}. Not in active sprint matrix. Suggested addition based on annex + source scan to close under-documented gap.",
            })

    return suggestions


def compute_confidence_caps(
    requirement_total: int,
    req_with_verification: int,
    req_with_aux_verification_only: int,
    executed_test_signal: ExecutedTestSignal,
) -> Tuple[Optional[float], List[str]]:
    total = max(requirement_total, 1)
    caps: List[float] = []
    reasons: List[str] = []

    if req_with_verification == 0 and requirement_total > 0:
        caps.append(79.0)
        reasons.append(
            "No executable verification evidence was discovered in repo test artifacts; score capped at 79.0."
        )

    aux_only_ratio = req_with_aux_verification_only / total
    if aux_only_ratio > 0.20:
        caps.append(89.0)
        reasons.append(
            "More than 20% of requirements have only auxiliary planning verification references; score capped at 89.0."
        )

    if executed_test_signal.status == "unknown":
        caps.append(89.0)
        reasons.append(
            "No direct executed-test signal was found (missing structured test_report.json); score capped at 89.0."
        )
    elif not executed_test_signal.passed:
        caps.append(79.0)
        reasons.append(
            "Latest structured executed-test signal is not passing; score capped at 79.0."
        )
    elif executed_test_signal.age_days is not None and executed_test_signal.age_days > 14.0:
        caps.append(89.0)
        reasons.append(
            "Latest structured executed-test signal is older than 14 days; score capped at 89.0."
        )

    if not caps:
        return None, []
    return min(caps), reasons


def evaluate_human_quality(
    root: Path,
    requirement_total: int,
    req_with_impl: int,
    req_with_verification: int,
    req_with_arch_design_trace: int,
    issue_quality_ratio: float,
    hierarchy: HierarchyGovernanceSummary,
    requirement_descriptions: Dict[str, str],
) -> HumanQualityAssessment:
    total = max(requirement_total, 1)
    desc_coverage = min(1.0, len(requirement_descriptions) / total)
    impl_ratio = req_with_impl / total
    verify_ratio = req_with_verification / total
    arch_ratio = req_with_arch_design_trace / total

    docs_index_exists = (root / "docs/INDEX.md").exists()
    readme_exists = (root / "README.md").exists()
    trace_matrix_exists = (root / "Requirements/04_Traceability_Matrix.md").exists()
    issue_tracker_dir_exists = (root / "planning/issues").exists()
    nav_ratio = (
        sum([docs_index_exists, readme_exists, trace_matrix_exists, issue_tracker_dir_exists]) / 4.0
    )

    onboarding_score = (
        0.20 * nav_ratio
        + 0.20 * desc_coverage
        + 0.20 * arch_ratio
        + 0.20 * impl_ratio
        + 0.10 * verify_ratio
        + 0.05 * issue_quality_ratio
        + 0.05 * hierarchy.hierarchy_coverage_ratio
    ) * 100.0
    onboarding_score = round(max(0.0, min(100.0, onboarding_score)), 1)

    artifact_set_scores = {
        "requirements_source_quality": round((0.6 * desc_coverage + 0.4 * arch_ratio) * 100.0, 1),
        "architecture_design_linkage_quality": round(arch_ratio * 100.0, 1),
        "implementation_linkage_quality": round(impl_ratio * 100.0, 1),
        "verification_linkage_quality": round(verify_ratio * 100.0, 1),
        "planning_governance_quality": round(
            (0.6 * issue_quality_ratio + 0.4 * hierarchy.hierarchy_coverage_ratio) * 100.0, 1
        ),
        "repo_onboarding_intuition": onboarding_score,
    }

    artifact_set_linkage_notes = {
        "requirements": [
            f"Requirement descriptions available for {len(requirement_descriptions)}/{requirement_total} IDs.",
            f"Architecture/design-linked requirement ratio: {arch_ratio * 100:.1f}%.",
        ],
        "architecture_design": [
            f"Requirements with architecture/design linkage: {req_with_arch_design_trace}/{requirement_total}.",
        ],
        "implementation": [
            f"Requirements with implementation evidence linkage: {req_with_impl}/{requirement_total}.",
        ],
        "verification": [
            f"Requirements with executable verification evidence linkage: {req_with_verification}/{requirement_total}.",
        ],
        "planning_governance": [
            f"Issue quality ratio: {issue_quality_ratio * 100:.1f}%.",
            "Hierarchy coverage ratio: "
            f"{hierarchy.hierarchy_coverage_ratio * 100:.1f}% ({hierarchy.sprint_issue_files_with_complete_hierarchy}/{hierarchy.sprint_issue_files_total}).",
        ],
    }

    findings: List[str] = []
    if onboarding_score >= 85.0:
        findings.append("Repository onboarding quality appears strong for new contributors.")
    elif onboarding_score >= 70.0:
        findings.append("Repository onboarding quality is acceptable but should be tightened for faster newcomer ramp-up.")
    else:
        findings.append("Repository onboarding quality is weak; documentation and trace navigation need immediate clarity improvements.")

    if not docs_index_exists:
        findings.append("Missing docs/INDEX.md weakens top-down navigation through architecture/design evidence.")
    if desc_coverage < 0.75:
        findings.append("Many requirement IDs lack clear human-readable descriptions in source artifacts.")
    if issue_quality_ratio < 0.90:
        findings.append("Issue metadata quality is below target, reducing intuitive story-to-requirement comprehension.")

    additional_review_dimensions = [
        "Evidence freshness and staleness windows (last verified timestamps per artifact family).",
        "Owner clarity and bus-factor metadata for high-risk architecture/design artifacts.",
        "Terminology consistency checks (glossary drift across requirements, architecture, and tests).",
        "Reproducibility quality (single-command path from requirements to verification replay).",
    ]

    return HumanQualityAssessment(
        artifact_set_scores=artifact_set_scores,
        artifact_set_linkage_notes=artifact_set_linkage_notes,
        onboarding_intuition_score=onboarding_score,
        findings=findings,
        additional_review_dimensions=additional_review_dimensions,
    )


def parse_porcelain_paths(status_output: str) -> List[str]:
    paths: List[str] = []
    for raw in status_output.splitlines():
        line = raw.rstrip()
        if len(line) < 4:
            continue
        payload = line[3:].strip()
        if not payload:
            continue
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1].strip()
        payload = payload.strip('"').replace("\\", "/")
        paths.append(payload)
    return paths


def is_allowed_generated_review_change(path: str) -> bool:
    normalized = path.replace("\\", "/")
    if not normalized.startswith("independent_reviews/latest/"):
        return False
    name = Path(normalized).name
    if not name.startswith("independent_review_"):
        return False
    return name.endswith(".md") or name.endswith(".json")


def load_latest_executed_test_signal(root: Path) -> ExecutedTestSignal:
    candidates: List[Path] = []
    for base in [root / "Tests/test_reports", root / "test_reports"]:
        if base.exists():
            candidates.extend(sorted(base.glob("**/test_report.json")))

    if not candidates:
        return ExecutedTestSignal(details=["No structured test_report.json found under Tests/test_reports or test_reports."])

    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except Exception as exc:
        return ExecutedTestSignal(
            report_path=latest.as_posix(),
            status="parse-error",
            passed=False,
            details=[f"Unable to parse structured test report: {exc}"],
        )

    status = str(payload.get("status", "unknown"))
    run_stamp = str(payload.get("run_stamp", "")).strip()
    observed = "unknown"
    age_days: Optional[float] = None

    if run_stamp:
        try:
            observed_dt = dt.datetime.strptime(run_stamp, "%Y%m%d_%H%M%S")
            observed = observed_dt.isoformat(timespec="seconds")
            age_days = round((dt.datetime.now() - observed_dt).total_seconds() / 86400.0, 2)
        except ValueError:
            observed = "unknown"

    if age_days is None:
        observed_dt = dt.datetime.fromtimestamp(latest.stat().st_mtime)
        observed = observed_dt.isoformat(timespec="seconds")
        age_days = round((dt.datetime.now() - observed_dt).total_seconds() / 86400.0, 2)

    normalized = status.upper()
    passed = any(token in normalized for token in ["OK", "PASS", "SUCCESS"])

    details = [
        f"Latest structured test report: {latest.as_posix()}",
        f"Status: {status}",
        f"Observed timestamp: {observed}",
        f"Age days: {age_days}",
    ]
    if "result_line" in payload:
        details.append(f"Result line: {payload.get('result_line')}")

    return ExecutedTestSignal(
        report_path=latest.as_posix(),
        status=status,
        passed=passed,
        observed_at=observed,
        age_days=age_days,
        details=details,
    )


def get_branch_awareness(root: Path) -> BranchAwareness:
    ok_branch, branch = run_git(root, ["branch", "--show-current"])
    ok_head, head = run_git(root, ["rev-parse", "--short", "HEAD"])
    ok_merge_base, merge_base = run_git(root, ["merge-base", "HEAD", "origin/main"])
    ok_counts, counts = run_git(root, ["rev-list", "--left-right", "--count", "HEAD...origin/main"])
    ok_status, status = run_git(root, ["status", "--porcelain"])

    current_branch = branch if ok_branch and branch else "DETACHED"
    head_commit = head if ok_head else "unknown"
    merge_base_value = merge_base if ok_merge_base else "unknown"

    ahead = 0
    behind = 0
    if ok_counts and counts:
        parts = counts.split()
        if len(parts) == 2:
            ahead = int(parts[0])
            behind = int(parts[1])

    dirty = True
    only_review_churn = False
    if ok_status:
        changed_paths = parse_porcelain_paths(status)
        non_review_changes = [p for p in changed_paths if not is_allowed_generated_review_change(p)]
        dirty = bool(non_review_changes)
        only_review_churn = bool(changed_paths) and not non_review_changes
        if only_review_churn:
            # Expected: the single canonical independent review pair (md+json) for the run context.
            # This is the known exception; the tree is "dirty" only because governance autoflow
            # on pre-push/push always regenerates the live review evidence.
            pass

    if current_branch == "main" and ahead == 0 and behind == 0:
        risk = "LOW"
        reason = "Branch is main and fully aligned with origin/main."
    elif ahead > 0 and behind > 0:
        risk = "HIGH"
        reason = "Branch has diverged from origin/main (both ahead and behind)."
    elif behind > 0:
        risk = "MAJOR"
        reason = "Branch is behind origin/main and should be rebased/merged before integration."
    elif current_branch == "DETACHED":
        risk = "HIGH"
        reason = "Detached HEAD state increases merge/integration risk."
    elif ahead > 0:
        risk = "MODERATE"
        reason = "Branch is ahead of origin/main; integration impact must be reviewed."
    else:
        risk = "MODERATE"
        reason = "Branch state requires manual review."

    return BranchAwareness(
        current_branch=current_branch,
        head_commit=head_commit,
        merge_base_with_origin_main=merge_base_value,
        ahead_of_origin_main=ahead,
        behind_origin_main=behind,
        working_tree_dirty=dirty,
        merge_risk=risk,
        merge_risk_reason=reason,
    )


def status_is_planned_like(status: str) -> bool:
    lowered = status.lower()
    return any(k in lowered for k in ["proposed", "planned", "in progress", "in review"])


def maturity_tag_for_requirement(status: str, has_arch_design_trace: bool, is_as_built: bool) -> str:
    if is_as_built:
        return "implementation-ready"
    if has_arch_design_trace and any(k in status.lower() for k in ["in progress", "in review"]):
        return "implementation-ready"
    if has_arch_design_trace:
        return "design-ready"
    return "concept"


def classify_conceptual_vs_as_built(rows: List[IssueRow], impl: Set[str], arch_design: Set[str]) -> ConceptualAsBuiltGapSummary:
    conceptual_planned_arch_only: Set[str] = set()
    planned_missing_arch_design_trace: Set[str] = set()

    for row in rows:
        if not row.has_requirement_column or not status_is_planned_like(row.status):
            continue
        for rid in row.requirement_ids:
            if rid in arch_design and rid not in impl:
                maturity = maturity_tag_for_requirement(row.status, has_arch_design_trace=True, is_as_built=False)
                conceptual_planned_arch_only.add(f"[{maturity}] {row.issue_id}: {rid}")
            if rid not in arch_design:
                maturity = maturity_tag_for_requirement(row.status, has_arch_design_trace=False, is_as_built=False)
                planned_missing_arch_design_trace.add(f"[{maturity}] {row.issue_id}: {rid}")

    as_built_missing_arch_design_trace = sorted(f"[implementation-ready] {rid}" for rid in (impl - arch_design))

    return ConceptualAsBuiltGapSummary(
        conceptual_planned_arch_only=sorted(conceptual_planned_arch_only),
        planned_missing_arch_design_trace=sorted(planned_missing_arch_design_trace),
        as_built_missing_arch_design_trace=as_built_missing_arch_design_trace,
    )


def evaluate_traceability_artifact_status(root: Path, sprint_dash: str, sprint_us: str) -> Tuple[Dict[str, Dict[str, object]], List[str], List[str]]:
    status: Dict[str, Dict[str, object]] = {}

    planning_files: List[Path] = []
    planning_files.extend(sorted((root / "planning").glob("Sprint_Remediation_*.md")))
    planning_files.extend(sorted((root / "planning").glob(f"Sprint_{sprint_us}_Remediation_*.md")))
    planning_files.extend(sorted((root / "planning/issues").glob(f"issue_{sprint_us}_*.md")))
    planning_files.extend(sorted((root / "planning/issues").glob(f"issue_{sprint_dash}_*.md")))
    planning_files.extend(
        [
            root / f"planning/issues/Sprint_{sprint_us}_Issue_Tracker.md",
            root / f"planning/issues/Sprint_{sprint_dash}_Issue_Tracker.md",
        ]
    )

    references_by_file: Dict[str, str] = {
        path.as_posix(): read_text(path)
        for path in planning_files
        if path.exists()
    }

    missing: List[str] = []
    unreferenced: List[str] = []

    for artifact in REQUIRED_TRACEABILITY_ARTIFACTS:
        artifact_path = artifact.as_posix()
        exists = (root / artifact).exists()
        referenced_in = [
            file_path
            for file_path, text in references_by_file.items()
            if artifact_path in text
        ]
        planning_reference_count = len(referenced_in)

        if not exists:
            missing.append(artifact_path)
        elif planning_reference_count == 0:
            unreferenced.append(artifact_path)

        status[artifact_path] = {
            "exists": exists,
            "planning_reference_count": planning_reference_count,
            "referenced_in": referenced_in,
            "planning_reference_status": "missing"
            if not exists
            else ("present-not-referenced" if planning_reference_count == 0 else "present-and-referenced"),
        }

    return status, missing, unreferenced


def is_full_remediation_complete(root: Path) -> bool:
    index_path = root / "independent_reviews/latest/issue_design_disposition_index.json"
    if not index_path.exists():
        legacy_path = root / "local_reviews/latest/issue_design_disposition_index.json"
        if legacy_path.exists():
            index_path = legacy_path
    if not index_path.exists():
        return False
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception:
        return False

    plans = payload.get("plans", [])
    if not plans:
        return False

    for plan in plans:
        if plan.get("missing_legs"):
            return False
    return True


def evaluate_hierarchy_governance(root: Path, sprint_dash: str, sprint_us: str) -> HierarchyGovernanceSummary:
    issues_dir = root / "planning" / "issues"
    if not issues_dir.exists():
        return HierarchyGovernanceSummary()

    required_fields = {
        "Parent Capability ID": re.compile(r"(?im)^\s*Parent Capability ID\s*:\s*(.+)$"),
        "Parent Function ID": re.compile(r"(?im)^\s*Parent Function ID\s*:\s*(.+)$"),
        "Child Function ID": re.compile(r"(?im)^\s*Child Function ID\s*:\s*(.+)$"),
        "Decomposition Level": re.compile(r"(?im)^\s*Decomposition Level\s*:\s*(.+)$"),
        "Allocated Component/Module": re.compile(r"(?im)^\s*Allocated Component/Module\s*:\s*(.+)$"),
        "Verification Method": re.compile(r"(?im)^\s*Verification Method\s*:\s*(.+)$"),
    }
    phase_pattern = re.compile(r"(?im)^\s*Remediation Phase\s*:\s*(.+)$")
    issue_heading_pattern = re.compile(r"(?im)^#\s*([^\n]+)$")

    issue_files: Set[Path] = set(issues_dir.glob(f"issue_{sprint_us}_*.md"))
    issue_files.update(issues_dir.glob(f"issue_{sprint_dash}_*.md"))
    ordered_files = sorted(issue_files)

    parent_caps: Set[str] = set()
    parent_fns: Set[str] = set()
    child_fns: Set[str] = set()
    level_counts: Counter[str] = Counter()
    phase_counts: Counter[str] = Counter()
    cap_to_children: Dict[str, Set[str]] = {}
    fn_to_children: Dict[str, Set[str]] = {}
    missing_rows: List[str] = []
    complete = 0

    for issue_file in ordered_files:
        text = read_text(issue_file)
        heading_match = issue_heading_pattern.search(text)
        issue_label = heading_match.group(1).strip() if heading_match else issue_file.stem

        captured: Dict[str, str] = {}
        missing: List[str] = []
        for field_name, pattern in required_fields.items():
            match = pattern.search(text)
            if not match or not match.group(1).strip():
                missing.append(field_name)
            else:
                captured[field_name] = match.group(1).strip()

        phase_match = phase_pattern.search(text)
        if phase_match and phase_match.group(1).strip():
            phase_counts[phase_match.group(1).strip()] += 1

        if missing:
            missing_rows.append(f"{issue_label} -> missing [{', '.join(missing)}] ({issue_file.as_posix()})")
            continue

        complete += 1
        parent_cap = captured["Parent Capability ID"]
        parent_fn = captured["Parent Function ID"]
        child_fn = captured["Child Function ID"]
        level = captured["Decomposition Level"]

        parent_caps.add(parent_cap)
        parent_fns.add(parent_fn)
        child_fns.add(child_fn)
        level_counts[level] += 1

        cap_to_children.setdefault(parent_cap, set()).add(child_fn)
        fn_to_children.setdefault(parent_fn, set()).add(child_fn)

    total = len(ordered_files)
    coverage = (complete / total) if total else 0.0

    return HierarchyGovernanceSummary(
        sprint_issue_files_total=total,
        sprint_issue_files_with_complete_hierarchy=complete,
        hierarchy_coverage_ratio=round(coverage, 4),
        unique_parent_capability_ids=len(parent_caps),
        unique_parent_function_ids=len(parent_fns),
        unique_child_function_ids=len(child_fns),
        decomposition_level_counts=dict(sorted(level_counts.items())),
        phase_counts=dict(sorted(phase_counts.items())),
        parent_capability_fanout={k: len(v) for k, v in sorted(cap_to_children.items())},
        parent_function_fanout={k: len(v) for k, v in sorted(fn_to_children.items())},
        missing_field_rows=sorted(missing_rows),
    )


def evaluate_severity(
    policy: SeverityPolicy,
    structure_missing: List[str],
    req_impl_ratio: float,
    req_verify_ratio: float,
    req_arch_ratio: float,
    issue_quality_ratio: float,
    planned_missing_reqs: List[str],
    traceability_artifacts_missing: List[str],
    traceability_artifacts_unreferenced: List[str],
    full_remediation_complete: bool,
    branch: BranchAwareness,
    conceptual_gaps: ConceptualAsBuiltGapSummary,
    hierarchy: HierarchyGovernanceSummary,
    human_quality: HumanQualityAssessment,
) -> SeveritySummary:
    summary = SeveritySummary()

    if structure_missing:
        summary.critical.append(f"Missing required repository paths: {', '.join(structure_missing)}")

    if req_verify_ratio < max(policy.req_verify_threshold - 0.2, 0.0):
        summary.critical.append(
            f"Executable verification coverage ratio {req_verify_ratio:.2f} is critically below threshold {policy.req_verify_threshold:.2f}."
        )
    elif req_verify_ratio < policy.req_verify_threshold:
        summary.major.append(
            f"Executable verification coverage ratio {req_verify_ratio:.2f} is below threshold {policy.req_verify_threshold:.2f}."
        )

    if req_impl_ratio < max(policy.req_impl_threshold - 0.2, 0.0):
        summary.critical.append(
            f"Implementation coverage ratio {req_impl_ratio:.2f} is critically below threshold {policy.req_impl_threshold:.2f}."
        )
    elif req_impl_ratio < policy.req_impl_threshold:
        summary.major.append(
            f"Implementation coverage ratio {req_impl_ratio:.2f} is below threshold {policy.req_impl_threshold:.2f}."
        )

    if req_arch_ratio < policy.req_arch_threshold:
        summary.major.append(
            f"Architecture/design trace ratio {req_arch_ratio:.2f} is below threshold {policy.req_arch_threshold:.2f}."
        )

    if issue_quality_ratio < policy.issue_quality_threshold:
        summary.major.append(
            f"Issue governance quality ratio {issue_quality_ratio:.2f} is below threshold {policy.issue_quality_threshold:.2f}."
        )

    if hierarchy.sprint_issue_files_total > 0 and hierarchy.missing_field_rows:
        severity_bucket = summary.major if hierarchy.hierarchy_coverage_ratio < 0.95 else summary.minor
        severity_bucket.append(
            "Hierarchy governance fields are incomplete in sprint issue artifacts: "
            f"{len(hierarchy.missing_field_rows)}/{hierarchy.sprint_issue_files_total} issue file(s) missing required fields."
        )

    if hierarchy.sprint_issue_files_total > 0 and hierarchy.parent_capability_fanout:
        if max(hierarchy.parent_capability_fanout.values()) <= 1 and hierarchy.sprint_issue_files_total >= 10:
            summary.informational.append(
                "Hierarchy taxonomy signal: no parent capability currently fans out to multiple child functions; "
                "consider planned abstraction consolidation in a follow-on remediation phase."
            )

    if len(planned_missing_reqs) > policy.max_planned_missing_requirement:
        summary.minor.append(
            "Planned/proposed issue rows exceed requirement-link policy threshold: "
            f"{len(planned_missing_reqs)} > {policy.max_planned_missing_requirement}."
        )

    if conceptual_gaps.planned_missing_arch_design_trace:
        summary.minor.append(
            "Planned requirements missing architecture/design trace found: "
            f"{len(conceptual_gaps.planned_missing_arch_design_trace)} item(s)."
        )

    if traceability_artifacts_missing:
        message = (
            "Required traceability artifacts are missing: "
            + ", ".join(traceability_artifacts_missing)
        )
        if full_remediation_complete:
            summary.critical.append(message)
        else:
            summary.informational.append("Non-blocking until full remediation complete: " + message)

    if traceability_artifacts_unreferenced:
        message = (
            "Required traceability artifacts are present but not referenced by planning/remediation artifacts: "
            + ", ".join(traceability_artifacts_unreferenced)
        )
        if full_remediation_complete:
            summary.major.append(message)
        else:
            summary.informational.append("Non-blocking until full remediation complete: " + message)

    if branch.merge_risk in {"HIGH"}:
        summary.critical.append(f"Branch merge risk is {branch.merge_risk}: {branch.merge_risk_reason}")
    elif branch.merge_risk in {"MAJOR"}:
        summary.major.append(f"Branch merge risk is {branch.merge_risk}: {branch.merge_risk_reason}")
    else:
        summary.informational.append(f"Branch merge risk is {branch.merge_risk}: {branch.merge_risk_reason}")

    if branch.working_tree_dirty:
        summary.minor.append("Working tree has local modifications; governance review may not represent committed state.")
    # Note: modifications limited to independent_reviews/latest/independent_review_*.{md,json}
    # are filtered by is_allowed_generated_review_change and represent expected single-review churn
    # from the pre-push/push governance step (the known exception for these two files).

    if human_quality.onboarding_intuition_score < 70.0:
        summary.major.append(
            "Human-quality onboarding score is below 70.0; repository comprehension and navigation are likely too hard for new contributors."
        )
    elif human_quality.onboarding_intuition_score < 80.0:
        summary.minor.append(
            "Human-quality onboarding score is below 80.0; improve readability and navigability before closeout."
        )

    return summary


def build_remediation_strategy(result: "ReviewResult") -> RemediationStrategy:
    health_floor = result.policy_profile.remediation_health_floor
    required = (
        result.overall_score < health_floor
        or bool(result.severity_summary.critical)
        or bool(result.severity_summary.major)
        or bool(result.planned_rows_missing_requirement)
    )
    planning_readiness = "not planning-ready" if required else "planning-ready"

    trigger_reasons: List[str] = []
    if result.overall_score < health_floor:
        trigger_reasons.append(
            f"Health score {result.overall_score:.1f}% is below remediation floor {health_floor:.1f}%.")
    if result.severity_summary.critical:
        trigger_reasons.append(f"{len(result.severity_summary.critical)} critical finding(s) remain open.")
    if result.severity_summary.major:
        trigger_reasons.append(f"{len(result.severity_summary.major)} major finding(s) remain open.")
    if result.planned_rows_missing_requirement:
        trigger_reasons.append(
            f"{len(result.planned_rows_missing_requirement)} planned/proposed issue row(s) lack requirement linkage."
        )

    themes: List[RemediationTheme] = []

    if result.req_without_impl:
        themes.append(
            RemediationTheme(
                title="Close implementation evidence gaps",
                priority="P0",
                rationale=(
                    f"{len(result.req_without_impl)} requirement ID(s) still lack implementation evidence; "
                    f"implementation coverage is {result.req_with_impl}/{result.requirement_total}."
                ),
                dependency_order="Implement first, then attach verification and traceability evidence.",
                starter_actions=[
                    "Group missing IDs by prefix to create work packages sized for one sprint chunk each.",
                    "Assign one owner per work package and identify the code or script location that will carry the change.",
                    "Update the requirement artifacts and implementation evidence links in the same change set.",
                ],
                acceptance_criteria=[
                    "Every targeted requirement ID has a concrete implementation artifact link.",
                    "The implementation ratio reaches the active policy threshold.",
                    "No new planned item is introduced without a requirement ID.",
                ],
                representative_items=representative_requirement_ids(result.req_without_impl),
                prefix_breakdown=summarize_requirement_prefixes(result.req_without_impl),
            )
        )

    if result.req_without_verification:
        themes.append(
            RemediationTheme(
                title="Close verification evidence gaps",
                priority="P0",
                rationale=(
                    f"{len(result.req_without_verification)} requirement ID(s) still lack executable verification evidence; "
                    f"executable verification coverage is {result.req_with_verification}/{result.requirement_total}."
                ),
                dependency_order="Verify after implementation exists; keep verification artifacts paired with the change.",
                starter_actions=[
                    "Create or update tests that exercise the implemented behavior for the missing requirements.",
                    "Attach pytest or test-path references directly to the requirement evidence.",
                    "Prefer one verification bundle per requirement cluster rather than one-off test edits.",
                ],
                acceptance_criteria=[
                    "Every targeted requirement ID has a verification artifact or test reference.",
                    "The verification ratio reaches the active policy threshold.",
                    "Blocking findings do not reappear in the next trend snapshot.",
                ],
                representative_items=representative_requirement_ids(result.req_without_verification),
                prefix_breakdown=summarize_requirement_prefixes(result.req_without_verification),
            )
        )

    if result.req_without_arch_design_trace:
        themes.append(
            RemediationTheme(
                title="Backfill architecture and design traceability",
                priority="P1",
                rationale=(
                    f"{len(result.req_without_arch_design_trace)} requirement ID(s) still lack architecture/design trace; "
                    f"traceability coverage is {result.req_with_arch_design_trace}/{result.requirement_total}."
                ),
                dependency_order="Traceability can run in parallel with implementation once the target scope is stable.",
                starter_actions=[
                    "Map each missing requirement to the relevant docs/architecture or docs/design artifact.",
                    "For as-built items, confirm whether the artifact is missing or the requirement needs reclassification.",
                    "For planned items, decide whether the work belongs in the current sprint or a future architecture slice.",
                ],
                acceptance_criteria=[
                    "Every targeted requirement ID has an architecture or design reference.",
                    "The architecture/design trace ratio reaches the active policy threshold.",
                    "Planned items that are not ready are explicitly reclassified or deferred.",
                ],
                representative_items=representative_requirement_ids(result.req_without_arch_design_trace),
                prefix_breakdown=summarize_requirement_prefixes(result.req_without_arch_design_trace),
            )
        )

    if result.traceability_artifacts_missing or result.traceability_artifacts_unreferenced:
        themes.append(
            RemediationTheme(
                title="Enforce traceability artifact baseline",
                priority="P0" if result.traceability_artifacts_missing else "P1",
                rationale=(
                    "Required decomposition/data-flow/metadata traceability artifacts must exist, be referenced in remediation planning, "
                    "and be verified during execution closeout."
                ),
                dependency_order="Populate missing artifacts first, then reference and verify them in active remediation slices.",
                starter_actions=[
                    "Create missing required traceability artifact files using repository templates.",
                    "Reference required artifacts in remediation plan evidence targets and issue-scoped disposition files.",
                    "Record execution-time verification status for each required artifact in remediation outputs.",
                ],
                acceptance_criteria=[
                    "All required traceability artifacts exist in the repository.",
                    "All required traceability artifacts are referenced in active planning/remediation artifacts.",
                    "Execution evidence records whether each required artifact was populated or verified.",
                ],
                representative_items=(result.traceability_artifacts_missing + result.traceability_artifacts_unreferenced)[:5],
            )
        )

    if result.conceptual_as_built_gaps.planned_missing_arch_design_trace or result.conceptual_as_built_gaps.as_built_missing_arch_design_trace:
        combined = result.conceptual_as_built_gaps.planned_missing_arch_design_trace + result.conceptual_as_built_gaps.as_built_missing_arch_design_trace
        themes.append(
            RemediationTheme(
                title="Resolve conceptual versus as-built mismatches",
                priority="P1",
                rationale=(
                    "The report distinguishes planned concepts from as-built items; unresolved mismatches will cause sprint "
                    "plans to oversubscribe unfinished architecture work."
                ),
                dependency_order="Confirm whether each item is concept, design-ready, or implementation-ready before committing sprint scope.",
                starter_actions=[
                    "Review each planned item and decide whether it needs architecture trace, implementation, or deferral.",
                    "Move implementation-ready items into the candidate delivery bucket and keep concept items out of execution scope.",
                    "Use maturity tags to prevent design-only items from being scheduled as if they were implementation work.",
                ],
                acceptance_criteria=[
                    "Every planned or implementation-ready item has an explicit maturity tag and correct execution status.",
                    "No concept item is scheduled without design trace and a named implementation owner.",
                    "The conceptual/as-built split is stable enough to seed sprint stories.",
                ],
                representative_items=combined[:5],
                prefix_breakdown=summarize_requirement_prefixes(combined),
            )
        )

    if result.issue_rows_without_requirements or result.planned_rows_missing_requirement:
        scope = result.issue_rows_without_requirements + result.planned_rows_missing_requirement
        themes.append(
            RemediationTheme(
                title="Fix issue tracker governance metadata",
                priority="P1",
                rationale=(
                    f"{len(scope)} issue row(s) are missing requirement linkage, which blocks dependable sprint decomposition."
                ),
                dependency_order="Repair tracker metadata before converting findings into sprint stories.",
                starter_actions=[
                    "Patch the tracker rows so every planned/proposed item has requirement linkage.",
                    "Confirm the GitHub reference and status columns are populated for each row.",
                    "Use the corrected tracker as the source of truth for story extraction.",
                ],
                acceptance_criteria=[
                    "Every active, proposed, or in-review row includes requirement IDs.",
                    "Planned/proposed rows that lack requirement linkage are reduced to zero.",
                    "Tracker rows can be converted into sprint stories without manual reconstruction.",
                ],
                representative_items=scope[:5],
            )
        )

    summary_notes = [
        "Remediation should be organized by prefix cluster and evidence type, not by raw list order.",
        "The highest-priority work is the set that removes critical and major findings first.",
        "Detailed sprint planning can start once the remediation gate is no longer required and the remaining work is advisory.",
    ]

    return RemediationStrategy(
        required=required,
        planning_readiness=planning_readiness,
        health_floor=health_floor,
        trigger_reasons=trigger_reasons,
        summary_notes=summary_notes,
        themes=themes,
    )


def build_trend_snapshot(result: "ReviewResult") -> TrendSnapshot:
    total = max(result.requirement_total, 1)
    return TrendSnapshot(
        timestamp=result.generated_at,
        sprint=result.sprint,
        score=result.overall_score,
        critical_count=len(result.severity_summary.critical),
        major_count=len(result.severity_summary.major),
        minor_count=len(result.severity_summary.minor),
        informational_count=len(result.severity_summary.informational),
        req_impl_ratio=result.req_with_impl / total,
        req_verify_ratio=result.req_with_verification / total,
        req_arch_ratio=result.req_with_arch_design_trace / total,
        full_chain_ratio=result.full_trace_chain_count / total,
        issue_quality_ratio=result.issue_quality_ratio,
        review_schema_version=REVIEW_SCHEMA_VERSION,
        traceability_baseline_mode=TRACEABILITY_BASELINE_MODE,
        relationship_direction_mode=RELATIONSHIP_DIRECTION_MODE,
        trend_epoch=TREND_EPOCH,
    )


def load_trend_history(root: Path) -> List[TrendSnapshot]:
    path = root / TREND_HISTORY_FILE
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        history: List[TrendSnapshot] = []
        for item in raw:
            history.append(TrendSnapshot(**item))
        return history
    except Exception:
        return []


def save_trend_history(root: Path, snapshots: List[TrendSnapshot]) -> None:
    path = root / TREND_HISTORY_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = [asdict(s) for s in snapshots]
    path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


def compute_trend_delta(previous: TrendSnapshot, current: TrendSnapshot) -> TrendDelta:
    return TrendDelta(
        previous_timestamp=previous.timestamp,
        score_delta=round(current.score - previous.score, 1),
        critical_delta=current.critical_count - previous.critical_count,
        major_delta=current.major_count - previous.major_count,
        minor_delta=current.minor_count - previous.minor_count,
        informational_delta=current.informational_count - previous.informational_count,
    )


def compute_kpi_delta(previous: TrendSnapshot, current: TrendSnapshot) -> Dict[str, float]:
    return {
        "req_impl_pct_delta": round((current.req_impl_ratio - previous.req_impl_ratio) * 100.0, 1),
        "req_verify_pct_delta": round((current.req_verify_ratio - previous.req_verify_ratio) * 100.0, 1),
        "req_arch_pct_delta": round((current.req_arch_ratio - previous.req_arch_ratio) * 100.0, 1),
        "full_chain_pct_delta": round((current.full_chain_ratio - previous.full_chain_ratio) * 100.0, 1),
        "issue_quality_pct_delta": round((current.issue_quality_ratio - previous.issue_quality_ratio) * 100.0, 1),
        "critical_major_count_delta": float(
            (current.critical_count + current.major_count) - (previous.critical_count + previous.major_count)
        ),
    }


def render_executive_summary(result: "ReviewResult") -> List[str]:
    lines: List[str] = []
    total = max(result.requirement_total, 1)
    impl_pct = (result.req_with_impl / total) * 100.0
    verify_pct = (result.req_with_verification / total) * 100.0
    arch_pct = (result.req_with_arch_design_trace / total) * 100.0
    full_chain_pct = (result.full_trace_chain_count / total) * 100.0
    issue_quality_pct = result.issue_quality_ratio * 100.0
    matrix_alignment_pct = result.matrix_truth_alignment.alignment_ratio * 100.0

    top_themes = result.remediation_strategy.themes[:3]
    theme_sentence = "No remediation themes are currently open."
    if top_themes:
        theme_sentence = " ".join(
            [
                f"{theme.title} ({theme.priority}) focuses on {theme.rationale.lower()}"
                for theme in top_themes
            ]
        )

    kpi_trend_sentence = "KPI trend deltas are baseline-only because no prior KPI snapshot is available."
    if result.kpi_delta:
        kpi_trend_sentence = (
            "KPI deltas versus the previous review are: "
            f"implementation {result.kpi_delta.get('req_impl_pct_delta', 0.0):+.1f} pts, "
            f"verification {result.kpi_delta.get('req_verify_pct_delta', 0.0):+.1f} pts, "
            f"architecture/design {result.kpi_delta.get('req_arch_pct_delta', 0.0):+.1f} pts, "
            f"full-chain {result.kpi_delta.get('full_chain_pct_delta', 0.0):+.1f} pts, "
            f"issue quality {result.kpi_delta.get('issue_quality_pct_delta', 0.0):+.1f} pts, "
            f"critical+major count {result.kpi_delta.get('critical_major_count_delta', 0.0):+.0f}."
        )

    readiness_phrase = "ready" if result.remediation_strategy.planning_readiness == "planning-ready" else "not yet ready"
    lines.append(
        "This independent review provides a governance-level assessment of repository health, source-to-evidence traceability completeness, and remediation readiness for sprint planning intake. "
        f"For sprint {result.sprint}, the repository health score is {result.overall_score:.1f}%, compared against the active remediation floor of {result.remediation_strategy.health_floor:.1f}%, and the planning-readiness verdict is {readiness_phrase}."
    )
    lines.append("")
    lines.append(
        "From a full-traceability perspective, this run evaluated each requirement across source, architecture/design, implementation evidence grounded in repository artifacts, and executable verification evidence grounded in test artifacts. "
        f"Current KPI levels are implementation coverage {impl_pct:.1f}%, verification coverage {verify_pct:.1f}%, architecture/design traceability {arch_pct:.1f}%, full-chain completeness {full_chain_pct:.1f}%, and issue-governance quality {issue_quality_pct:.1f}%. "
        f"Matrix-to-ground-truth alignment is {matrix_alignment_pct:.1f}% when matrix declarations are reconciled against baseline document-to-code-to-test evidence. "
        f"These values correspond to {result.full_trace_chain_count}/{result.requirement_total} requirements with complete end-to-end evidence chains."
    )
    lines.append("")
    lines.append(
        "Severity posture remains a key planning gate. "
        f"This report records {len(result.severity_summary.critical)} critical findings, {len(result.severity_summary.major)} major findings, {len(result.severity_summary.minor)} minor findings, and {len(result.severity_summary.informational)} informational findings. "
        f"Branch context is {result.branch_awareness.current_branch} with merge risk {result.branch_awareness.merge_risk}, and the trend dashboard classifies the overall recent direction as {result.trend_dashboard.overall_trend}."
    )
    lines.append("")
    lines.append(
        "Remediation strategy is intended to convert diagnostic output into actionable intake concepts without prematurely locking sprint execution details. "
        + theme_sentence
    )
    lines.append("")
    lines.append(
        "KPI tracking supports governance learning over time by making both positive remediation effects and negative implementation side effects measurable between runs. "
        + kpi_trend_sentence
        + " This allows governance rules, definition-of-done criteria, and pre-merge controls to evolve based on objective trend evidence rather than one-off observations."
    )
    lines.append("")
    lines.append(
        "The practical interpretation for this run is that remediation work should prioritize closure of missing chain legs that drive critical and major findings, while maintaining explicit KPI baselines for future comparison. "
        "As remediation sprints complete, this summary can be used to verify whether health and chain-completeness KPIs are improving at a sustainable rate, and whether delivery sprints introduce regressions that warrant process corrections."
    )
    if result.run_context == "pre-push":
        lines.append("")
        lines.append(
            "Open exception obligations for post-merge remediation are embedded in Appendix A of this independent review."
        )
    lines.append("")
    return lines


def severity_pressure(snapshot: TrendSnapshot) -> int:
    return snapshot.critical_count * 3 + snapshot.major_count * 2 + snapshot.minor_count


def direction_from_pair(previous: TrendSnapshot, current: TrendSnapshot) -> str:
    score_delta = current.score - previous.score
    pressure_delta = severity_pressure(current) - severity_pressure(previous)
    if score_delta > 0.1 and pressure_delta <= 0:
        return "improving"
    if abs(score_delta) <= 0.1 and pressure_delta == 0:
        return "stable"
    return "regressing"


def build_trend_dashboard(history: List[TrendSnapshot], window: int) -> TrendDashboardSummary:
    scoped = history[-window:] if len(history) > window else history
    entries: List[TrendDashboardEntry] = []

    for idx, snap in enumerate(scoped):
        if idx == 0:
            direction = "baseline"
        else:
            direction = direction_from_pair(scoped[idx - 1], snap)
        entries.append(
            TrendDashboardEntry(
                timestamp=snap.timestamp,
                score=snap.score,
                critical_count=snap.critical_count,
                major_count=snap.major_count,
                minor_count=snap.minor_count,
                informational_count=snap.informational_count,
                direction=direction,
            )
        )

    if len(scoped) < 2:
        overall = "baseline"
    else:
        overall = direction_from_pair(scoped[0], scoped[-1])

    return TrendDashboardSummary(window=window, overall_trend=overall, entries=entries)


def parse_github_issue_ref(github_ref: str, default_repo: str) -> Tuple[str, str]:
    stripped = github_ref.strip()
    url_match = GITHUB_URL_PATTERN.search(stripped)
    if url_match:
        return url_match.group(1), url_match.group(2)

    hash_match = re.search(r"#(\d+)", stripped)
    if hash_match and default_repo:
        return default_repo, hash_match.group(1)

    return "", ""


def local_status_expected_remote_open(status: str) -> Optional[bool]:
    lowered = status.lower()
    if "closed" in lowered or "resolved" in lowered:
        return False
    if any(k in lowered for k in ["proposed", "planned", "in progress", "in review", "logged", "open"]):
        return True
    return None


def run_github_reconciliation(
    root: Path,
    rows: List[IssueRow],
    enabled: bool,
    default_repo: str,
) -> Tuple[GitHubReconciliationSummary, List[GitHubIssueReconciliation]]:
    if not enabled:
        return GitHubReconciliationSummary(
            enabled=False,
            checked_count=0,
            matched_count=0,
            mismatched_count=0,
            unresolved_count=0,
            unresolved_details=["GitHub reconciliation disabled (opt-in mode)."],
        ), []

    ok_gh, gh_version = run_command(root, ["gh", "--version"])
    if not ok_gh:
        return GitHubReconciliationSummary(
            enabled=True,
            checked_count=0,
            matched_count=0,
            mismatched_count=0,
            unresolved_count=1,
            unresolved_details=["GitHub CLI is not available in PATH; reconciliation skipped."],
        ), []

    reconciliations: List[GitHubIssueReconciliation] = []
    unresolved: List[str] = []

    unique: Dict[Tuple[str, str], IssueRow] = {}
    for row in rows:
        repo, number = parse_github_issue_ref(row.github_ref, default_repo)
        if repo and number:
            unique[(repo, number)] = row

    for (repo, number), row in sorted(unique.items()):
        ok_view, out = run_command(
            root,
            ["gh", "issue", "view", number, "--repo", repo, "--json", "number,state,url,title"],
        )
        if not ok_view:
            unresolved.append(f"{row.issue_id} -> unable to query {repo}#{number}: {out}")
            continue

        try:
            payload = json.loads(out)
            remote_state = str(payload.get("state", "")).lower()
            remote_url = str(payload.get("url", ""))
            expected_open = local_status_expected_remote_open(row.status)
            status_match = True
            detail = "Status aligned."
            if expected_open is not None:
                if expected_open and remote_state != "open":
                    status_match = False
                    detail = f"Local status '{row.status}' expects OPEN but remote is '{remote_state}'."
                if (not expected_open) and remote_state != "closed":
                    status_match = False
                    detail = f"Local status '{row.status}' expects CLOSED but remote is '{remote_state}'."

            reconciliations.append(
                GitHubIssueReconciliation(
                    issue_id=row.issue_id,
                    github_ref=row.github_ref,
                    github_repo=repo,
                    github_number=number,
                    local_status=row.status,
                    remote_state=remote_state,
                    status_match=status_match,
                    remote_url=remote_url,
                    detail=detail,
                )
            )
        except Exception as exc:
            unresolved.append(f"{row.issue_id} -> parse error for {repo}#{number}: {exc}")

    matched = len([r for r in reconciliations if r.status_match])
    mismatched = len([r for r in reconciliations if not r.status_match])

    summary = GitHubReconciliationSummary(
        enabled=True,
        checked_count=len(reconciliations),
        matched_count=matched,
        mismatched_count=mismatched,
        unresolved_count=len(unresolved),
        unresolved_details=unresolved,
    )
    return summary, reconciliations


def render_engineering_class_scorecards(result: "ReviewResult") -> List[str]:
    lines: List[str] = []
    classes = result.engineering_artifact_classes or {}
    if not classes:
        lines.append("No per-class engineering annex analysis available in this run.")
        return lines
    lines.append("## Engineering Artifact Class Scorecards (per Independent Engineering Review Model)")
    lines.append("")
    for class_name, data in classes.items():
        maturity = data.get("overall_fidelity", 0.0) * 100 if isinstance(data.get("overall_fidelity"), (int, float)) else 0.0
        populated = data.get("populated_relationships", 0)
        empty = data.get("empty_relationships", 0)
        files = ", ".join(data.get("files_analyzed", [])[:3])
        lines.append(f"### {class_name}")
        lines.append(f"- Maturity / Annex Fidelity: {maturity:.1f}% (populated relationships: {populated}, empty: {empty})")
        lines.append(f"- Files with annex analysis: {files}")
        if data.get("key_examples"):
            lines.append("- Example populated relationship(s):")
            for ex in data.get("key_examples", [])[:2]:
                lines.append(f"  - {ex}")
        lines.append("")
    return lines

def render_cross_cutting_engineering_analysis(result: "ReviewResult") -> List[str]:
    lines: List[str] = []
    lines.append("## Cross-Cutting Engineering Analyses")
    lines.append("")

    # Documentation relationships
    doc_health = result.documentation_relationship_health or {}
    lines.append("### Documentation Relationship Health (INCOSE Annex Usage)")
    lines.append(f"- Overall fidelity (populated vs empty relationships across classes): {doc_health.get('documentation_relationship_fidelity', 0.0)}")
    strong = doc_health.get("classes_with_strong_annexes", [])
    weak = doc_health.get("classes_needing_annex_improvement", [])
    if strong:
        lines.append(f"- Classes with strong annexes: {', '.join(strong)}")
    if weak:
        lines.append(f"- Classes needing annex improvement: {', '.join(weak)}")
    lines.append("")

    # Interface mapping
    if_mappings = result.interface_to_function_decomposition_mappings or []
    lines.append("### Interface-to-Functional-Decomposition Mapping (L0–L4 Abstraction)")
    if if_mappings:
        for m in if_mappings[:8]:
            lines.append(f"- {m.get('source', '?')} @ {m.get('abstraction_level', '?')}: linked functions {m.get('linked_functions', [])[:3]}")
    else:
        lines.append("- No explicit L0–L4 to interface mappings extracted in this run (see ICD and Functional Data Flow Package for manual review).")
    lines.append("")

    # Matrix audit vs engineering reality
    ma = result.traceability_matrix_audit or {}
    lines.append("### Traceability Matrix Audit (vs Actual Engineering Documentation, Implementation & Verification)")
    lines.append(f"- Engineering gaps from annex analysis: {len(ma.get('engineering_gaps_identified', []))}")
    for gap in ma.get("engineering_gaps_identified", [])[:5]:
        lines.append(f"  - {gap}")
    disc = ma.get("matrix_vs_engineering_discrepancies", {})
    lines.append(f"- Matrix discrepancies: {disc}")
    lines.append(f"- Recommendation: {ma.get('recommendation', 'Review annexes and matrices for bidirectional fidelity.')}")
    lines.append("")

    return lines


def render_suggested_matrix_additions(result: "ReviewResult") -> List[str]:
    lines: List[str] = []
    adds = getattr(result, "suggested_matrix_additions", {}) or {}
    if not adds:
        return lines

    lines.append("## Suggested Matrix Row Additions (from Annex + Source Analysis)")
    lines.append("These are auto-generated proposals to close 'Ground Truth Present But Missing In Matrix' gaps.")
    lines.append("They are derived from populated INCOSE annex relationships + detected source impl/verify paths.")
    lines.append("Review and apply the highest-confidence ones to the target matrices (Capability_Function_Architecture_Traceability_Matrix.md, 15_End_To_End_..., 16_Active_Sprint_...).")
    lines.append("")

    for matrix_name, rows in adds.items():
        if not rows:
            continue
        lines.append(f"### For {matrix_name}")
        lines.append(f"Suggested {len(rows)} row(s):")
        for row in rows[:5]:  # limit to top 5 per matrix for readability
            line = " | ".join(f"{k}: {v[:60]}" for k, v in row.items())
            lines.append(f"- {line}")
        if len(rows) > 5:
            lines.append(f"- ... and {len(rows)-5} more (see full JSON under suggested_matrix_additions)")
        lines.append("")

    lines.append("**Action**: Copy relevant rows into the matrices, update Notes/Audit Rationale with 'Added from IER annex+source suggestion <date>'. Re-run review to confirm gap closure.")
    lines.append("")
    return lines


def render_markdown(result: ReviewResult) -> str:
    lines: List[str] = []
    lines.append("# Independent Local Repository Review")
    lines.append("")
    lines.append(f"- Generated: {result.generated_at}")
    lines.append(f"- Sprint Scope: {result.sprint}")
    lines.append(f"- Run Context: {result.run_context}")
    lines.append(f"- Review Schema Version: {result.review_schema_version}")
    lines.append(f"- Traceability Baseline Mode: {result.traceability_baseline_mode}")
    lines.append(f"- Relationship Direction Mode: {result.relationship_direction_mode}")
    lines.append(f"- Trend Epoch: {result.trend_epoch}")
    lines.append(f"- Overall Health Score (legacy): {result.overall_score}%")
    if hasattr(result, "overall_engineering_health_score") and result.overall_engineering_health_score:
        lines.append(f"- Overall Engineering Health Score (new model): {result.overall_engineering_health_score}%")
    lines.append(f"- Severity Profile: {result.policy_profile.profile_name}")
    lines.append(f"- Severity Policy File: {result.policy_profile.policy_file}")
    lines.append("")

    lines.append("## Executive Summary")
    lines.extend(render_executive_summary(result))
    # Brief nod to new model
    if result.engineering_artifact_classes:
        lines.append("")
        lines.append("**Engineering Review Note (per Independent_Engineering_Review_Model.md):** This run includes per-class maturity/health/quality analysis of documentation relationships (annexes), implementation, verification, interface-to-functional-decomposition mappings, and a matrix audit against actual engineering content. See dedicated sections below.")

    lines.append("## 0) Branch Awareness")
    lines.append(f"- Current branch: {result.branch_awareness.current_branch}")
    lines.append(f"- HEAD: {result.branch_awareness.head_commit}")
    lines.append(f"- Merge-base with origin/main: {result.branch_awareness.merge_base_with_origin_main}")
    lines.append(
        "- Ahead/behind vs origin/main: "
        f"{result.branch_awareness.ahead_of_origin_main}/{result.branch_awareness.behind_origin_main}"
    )
    lines.append(f"- Working tree dirty: {result.branch_awareness.working_tree_dirty}")
    lines.append(f"- Merge risk: {result.branch_awareness.merge_risk}")
    lines.append(f"- Merge risk reason: {result.branch_awareness.merge_risk_reason}")
    lines.append("")

    lines.append("## 1) Structure Integrity")
    if result.structure_missing:
        lines.append("- Missing expected paths:")
        lines.extend([f"  - {p}" for p in result.structure_missing])
    else:
        lines.append("- All expected top-level governance/runtime paths present.")
    lines.append("")

    lines.append("## 1.5) Required Traceability Artifacts")
    lines.append("- Required artifacts:")
    lines.extend([f"  - {item}" for item in result.required_traceability_artifacts])
    lines.append(
        f"- Enforcement mode for artifact findings: {'blocking' if result.full_remediation_complete else 'non-blocking'}"
    )
    lines.append("")

    lines.append("### Auxiliary Planning Reference Status (Not Scored as Verification)")
    for artifact in result.required_traceability_artifacts:
        artifact_status = result.traceability_artifact_status.get(artifact, {})
        lines.append(
            f"- {artifact} | exists={artifact_status.get('exists', False)} | planning_refs={artifact_status.get('planning_reference_count', 0)} | status={artifact_status.get('planning_reference_status', 'unknown')}"
        )
        for ref in artifact_status.get("referenced_in", [])[:5]:
            lines.append(f"  - referenced in: {ref}")
    lines.append("")

    lines.append("### Missing Required Artifacts")
    lines.extend([f"- {item}" for item in result.traceability_artifacts_missing] or ["- None"])
    lines.append("")

    lines.append("### Present But Unreferenced Artifacts")
    lines.extend([f"- {item}" for item in result.traceability_artifacts_unreferenced] or ["- None"])
    lines.append("")

    lines.append("## 2) Requirement Coverage")
    lines.append(f"- Total requirement IDs discovered: {result.requirement_total}")
    lines.append(f"- Requirement IDs with implementation evidence: {result.req_with_impl}")
    lines.append(f"- Requirement IDs with executable verification evidence: {result.req_with_verification}")
    lines.append(f"- Requirement IDs with only auxiliary planning verification references: {result.req_with_aux_verification_only}")
    lines.append(f"- Requirement IDs with architecture/design traceability: {result.req_with_arch_design_trace}")
    lines.append("")

    lines.append("### Requirements Missing Implementation Evidence")
    if result.req_without_impl:
        lines.extend([f"- {format_requirement_chain_line(rid, result)}" for rid in result.req_without_impl])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Requirements Missing Executable Verification Evidence")
    if result.req_without_verification:
        lines.extend([f"- {format_requirement_chain_line(rid, result)}" for rid in result.req_without_verification])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Requirements Missing Architecture/Design Traceability")
    if result.req_without_arch_design_trace:
        lines.extend([f"- {format_requirement_chain_line(rid, result)}" for rid in result.req_without_arch_design_trace])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## 2.6) Full Source-to-Evidence Chain Status")
    lines.append(
        f"- Complete chains (source + arch/design + implementation + verification): {result.full_trace_chain_count}/{result.requirement_total}"
    )
    lines.append(f"- Requirements with at least one missing chain leg: {len(result.full_trace_chain_gap_ids)}")
    lines.append("### Missing-Leg Chain Findings")
    if result.full_trace_chain_gap_ids:
        lines.extend([f"- {format_requirement_chain_line(rid, result)}" for rid in result.full_trace_chain_gap_ids])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## 2.7) Matrix-to-Ground-Truth Alignment")
    lines.append(
        "- Matrix artifacts scanned: "
        + (", ".join(result.matrix_truth_alignment.matrix_files) if result.matrix_truth_alignment.matrix_files else "none")
    )
    lines.append(f"- Requirement legs evaluated (implementation/verification/architecture): {result.matrix_truth_alignment.requirement_legs_evaluated}")
    lines.append(f"- Leg mismatches: {result.matrix_truth_alignment.leg_mismatch_count}")
    lines.append(f"- Alignment ratio: {result.matrix_truth_alignment.alignment_ratio * 100:.1f}%")
    lines.append("")

    # === New holistic engineering sections (Independent Engineering Review Model) ===
    lines.extend(render_engineering_class_scorecards(result))
    lines.extend(render_cross_cutting_engineering_analysis(result))
    lines.extend(render_suggested_matrix_additions(result))

    lines.append("### Baseline Truth Sources")
    lines.extend([f"- {item}" for item in result.matrix_truth_alignment.baseline_truth_sources] or ["- None"])
    lines.append("")

    lines.append("### Matrix Declared But Ground Truth Missing")
    lines.append(f"- Implementation mismatches: {len(result.matrix_truth_alignment.declared_impl_without_truth)}")
    lines.append(f"- Verification mismatches: {len(result.matrix_truth_alignment.declared_verify_without_truth)}")
    lines.append(f"- Architecture/design mismatches: {len(result.matrix_truth_alignment.declared_arch_without_truth)}")
    lines.extend(
        [f"- impl-mismatch: {format_requirement_chain_line(rid, result)}" for rid in result.matrix_truth_alignment.declared_impl_without_truth[:50]]
    )
    lines.extend(
        [f"- verify-mismatch: {format_requirement_chain_line(rid, result)}" for rid in result.matrix_truth_alignment.declared_verify_without_truth[:50]]
    )
    lines.extend(
        [f"- arch-mismatch: {format_requirement_chain_line(rid, result)}" for rid in result.matrix_truth_alignment.declared_arch_without_truth[:50]]
    )
    if (
        not result.matrix_truth_alignment.declared_impl_without_truth
        and not result.matrix_truth_alignment.declared_verify_without_truth
        and not result.matrix_truth_alignment.declared_arch_without_truth
    ):
        lines.append("- None")
    lines.append("")

    lines.append("### Ground Truth Present But Missing In Matrix")
    lines.append(f"- Implementation under-documented: {len(result.matrix_truth_alignment.truth_impl_missing_matrix)}")
    lines.append(f"- Verification under-documented: {len(result.matrix_truth_alignment.truth_verify_missing_matrix)}")
    lines.append(f"- Architecture/design under-documented: {len(result.matrix_truth_alignment.truth_arch_missing_matrix)}")
    lines.extend(
        [f"- impl-doc-gap: {format_requirement_chain_line(rid, result)}" for rid in result.matrix_truth_alignment.truth_impl_missing_matrix[:50]]
    )
    lines.extend(
        [f"- verify-doc-gap: {format_requirement_chain_line(rid, result)}" for rid in result.matrix_truth_alignment.truth_verify_missing_matrix[:50]]
    )
    lines.extend(
        [f"- arch-doc-gap: {format_requirement_chain_line(rid, result)}" for rid in result.matrix_truth_alignment.truth_arch_missing_matrix[:50]]
    )
    if (
        not result.matrix_truth_alignment.truth_impl_missing_matrix
        and not result.matrix_truth_alignment.truth_verify_missing_matrix
        and not result.matrix_truth_alignment.truth_arch_missing_matrix
    ):
        lines.append("- None")
    lines.append("")

    lines.append("## 2.5) Conceptual vs As-Built Gap Classification")
    lines.append("### Conceptual Planned Items (Architecture/Design Traced, Not Yet As-Built)")
    if result.conceptual_as_built_gaps.conceptual_planned_arch_only:
        lines.extend([f"- {humanize_requirement_reference(item, result.requirement_descriptions)}" for item in result.conceptual_as_built_gaps.conceptual_planned_arch_only])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Planned Items Missing Architecture/Design Trace")
    if result.conceptual_as_built_gaps.planned_missing_arch_design_trace:
        lines.extend([f"- {humanize_requirement_reference(item, result.requirement_descriptions)}" for item in result.conceptual_as_built_gaps.planned_missing_arch_design_trace])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### As-Built Items Missing Architecture/Design Trace")
    if result.conceptual_as_built_gaps.as_built_missing_arch_design_trace:
        lines.extend([f"- {humanize_requirement_reference(item, result.requirement_descriptions)}" for item in result.conceptual_as_built_gaps.as_built_missing_arch_design_trace])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## 3) Issue Governance Coverage")
    lines.append(f"- Tracker rows parsed: {result.issue_rows_total}")
    if result.issue_rows_total == 0:
        lines.append(
            "- Safety penalty trigger: no parsable issue tracker rows found. Add rows to planning/issues/Sprint_<sprint>_Issue_Tracker.md using IDs like S13-001 or D-S13-001 with GitHub Issue and Status columns."
        )
    lines.append("")

    lines.append("### Issue Rows Missing Requirement Linkage")
    if result.issue_rows_without_requirements:
        lines.extend([f"- {item}" for item in result.issue_rows_without_requirements])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Issue Rows Missing GitHub Reference")
    if result.issue_rows_without_github_ref:
        lines.extend([f"- {item}" for item in result.issue_rows_without_github_ref])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Planned/Proposed Rows Missing Requirement IDs")
    if result.planned_rows_missing_requirement:
        lines.extend([f"- {item}" for item in result.planned_rows_missing_requirement])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## 3.5) Hierarchy Governance Coverage")
    lines.append(f"- Sprint issue files analyzed: {result.hierarchy_governance.sprint_issue_files_total}")
    lines.append(
        "- Issue files with complete hierarchy fields: "
        f"{result.hierarchy_governance.sprint_issue_files_with_complete_hierarchy}"
    )
    lines.append(
        "- Hierarchy coverage ratio: "
        f"{result.hierarchy_governance.hierarchy_coverage_ratio * 100:.1f}%"
    )
    lines.append(
        "- Unique parent capability IDs: "
        f"{result.hierarchy_governance.unique_parent_capability_ids}"
    )
    lines.append(
        "- Unique parent function IDs: "
        f"{result.hierarchy_governance.unique_parent_function_ids}"
    )
    lines.append(
        "- Unique child function IDs: "
        f"{result.hierarchy_governance.unique_child_function_ids}"
    )
    lines.append("")

    lines.append("### Decomposition Level Counts")
    if result.hierarchy_governance.decomposition_level_counts:
        for level, count in result.hierarchy_governance.decomposition_level_counts.items():
            lines.append(f"- {level}: {count}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Phase Counts")
    if result.hierarchy_governance.phase_counts:
        for phase, count in result.hierarchy_governance.phase_counts.items():
            lines.append(f"- {phase}: {count}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Parent Capability Fan-Out")
    if result.hierarchy_governance.parent_capability_fanout:
        for cap_id, fanout in result.hierarchy_governance.parent_capability_fanout.items():
            lines.append(f"- {cap_id}: {fanout} child function(s)")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Missing Hierarchy Fields")
    if result.hierarchy_governance.missing_field_rows:
        lines.extend([f"- {item}" for item in result.hierarchy_governance.missing_field_rows])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## 4) Severity Policy and Findings")
    lines.append("### Active Thresholds")
    lines.append(f"- req_impl_threshold: {result.severity_policy.req_impl_threshold}")
    lines.append(f"- req_verify_threshold: {result.severity_policy.req_verify_threshold}")
    lines.append(f"- req_arch_threshold: {result.severity_policy.req_arch_threshold}")
    lines.append(f"- issue_quality_threshold: {result.severity_policy.issue_quality_threshold}")
    lines.append(
        f"- max_planned_missing_requirement: {result.severity_policy.max_planned_missing_requirement}"
    )
    lines.append("")

    lines.append("### Critical")
    lines.extend([f"- {item}" for item in result.severity_summary.critical] or ["- None"])
    lines.append("")

    lines.append("### Major")
    lines.extend([f"- {item}" for item in result.severity_summary.major] or ["- None"])
    lines.append("")

    lines.append("### Minor")
    lines.extend([f"- {item}" for item in result.severity_summary.minor] or ["- None"])
    lines.append("")

    lines.append("### Informational")
    lines.extend([f"- {item}" for item in result.severity_summary.informational] or ["- None"])
    lines.append("")

    lines.append("## 4.5) Health Score Breakdown")
    health = result.health_breakdown or {}
    components = health.get("component_points", {}) if isinstance(health, dict) else {}
    penalties = health.get("penalty_components", {}) if isinstance(health, dict) else {}
    lines.append("### Weighted Base Components")
    lines.append("| Component | Points |")
    lines.append("|---|---:|")
    lines.append(f"| Structure integrity (10%) | {components.get('structure_integrity', 0.0):.2f} |")
    lines.append(f"| Implementation coverage (30%) | {components.get('implementation_coverage', 0.0):.2f} |")
    lines.append(f"| Executable verification coverage (35%) | {components.get('verification_executable_coverage', 0.0):.2f} |")
    lines.append(f"| Architecture/design traceability (15%) | {components.get('architecture_design_traceability', 0.0):.2f} |")
    lines.append(f"| Issue governance quality (10%) | {components.get('issue_governance_quality', 0.0):.2f} |")
    lines.append(f"| Base score subtotal | {health.get('base_score', 0.0):.2f} |")
    lines.append("")
    lines.append("### Governance Penalty Components")
    lines.append("| Penalty Source | Points |")
    lines.append("|---|---:|")
    lines.append(f"| Critical findings | {penalties.get('critical_findings', 0.0):.2f} |")
    lines.append(f"| Major findings | {penalties.get('major_findings', 0.0):.2f} |")
    lines.append(f"| Minor findings | {penalties.get('minor_findings', 0.0):.2f} |")
    lines.append(f"| Informational findings | {penalties.get('informational_findings', 0.0):.2f} |")
    lines.append(f"| No tracker rows safety penalty | {penalties.get('no_tracker_rows', 0.0):.2f} |")
    lines.append(f"| Penalty subtotal (raw) | {health.get('penalty_raw', 0.0):.2f} |")
    lines.append(f"| Penalty applied (capped at 40.0) | {health.get('penalty_capped', 0.0):.2f} |")
    lines.append("")
    lines.append("### Confidence Gates")
    lines.append(f"- Uncapped score after penalties: {health.get('final_uncapped', result.overall_score):.1f}")
    lines.append(f"- Confidence cap applied: {health.get('confidence_cap', 'none')}")
    for cap_note in health.get("confidence_caps_applied", []):
        lines.append(f"  - {cap_note}")
    if not health.get("confidence_caps_applied", []):
        lines.append("  - None")
    lines.append("")
    lines.append("### Executed Test Signal")
    lines.append(f"- Structured report path: {result.executed_test_signal.report_path or 'none'}")
    lines.append(f"- Status: {result.executed_test_signal.status}")
    lines.append(f"- Passing signal: {result.executed_test_signal.passed}")
    lines.append(f"- Observed at: {result.executed_test_signal.observed_at}")
    lines.append(f"- Age days: {result.executed_test_signal.age_days}")
    for detail in result.executed_test_signal.details:
        lines.append(f"  - {detail}")
    if not result.executed_test_signal.details:
        lines.append("  - None")
    lines.append("")
    lines.append(
        f"- Final score formula: min({health.get('base_score', 0.0):.2f} - {health.get('penalty_capped', 0.0):.2f}, cap={health.get('confidence_cap', 'none')}) = {health.get('final_score', result.overall_score):.1f}"
    )
    lines.append("")

    lines.append("## 5) Compact Trend Dashboard")
    lines.append(f"- Window: last {result.trend_dashboard.window} run(s)")
    lines.append(f"- Overall trend: {result.trend_dashboard.overall_trend}")
    lines.append("- Recent runs:")
    for entry in result.trend_dashboard.entries:
        lines.append(
            "  - "
            f"{entry.timestamp} | score={entry.score} | "
            f"C/M/m/I={entry.critical_count}/{entry.major_count}/{entry.minor_count}/{entry.informational_count} | "
            f"{entry.direction}"
        )
    lines.append("")

    lines.append("## 6) Trend Snapshot and Delta")
    lines.append(f"- Current snapshot timestamp: {result.trend_snapshot.timestamp}")
    lines.append(f"- Current score: {result.trend_snapshot.score}")
    lines.append(
        "- Current severity counts: "
        f"critical={result.trend_snapshot.critical_count}, "
        f"major={result.trend_snapshot.major_count}, "
        f"minor={result.trend_snapshot.minor_count}, "
        f"informational={result.trend_snapshot.informational_count}"
    )
    if result.trend_delta is None:
        lines.append("- Delta: no prior snapshot available.")
    else:
        lines.append(f"- Previous snapshot: {result.trend_delta.previous_timestamp}")
        lines.append(f"- Score delta: {result.trend_delta.score_delta}")
        lines.append(
            "- Severity deltas: "
            f"critical={result.trend_delta.critical_delta}, "
            f"major={result.trend_delta.major_delta}, "
            f"minor={result.trend_delta.minor_delta}, "
            f"informational={result.trend_delta.informational_delta}"
        )
    lines.append("")

    lines.append("## 6.5) KPI Scorecard")
    lines.append("| KPI | Current | Delta vs Prior |")
    lines.append("|---|---:|---:|")
    lines.append(
        f"| Implementation coverage | {result.trend_snapshot.req_impl_ratio * 100:.1f}% | {result.kpi_delta.get('req_impl_pct_delta', 0.0):+.1f} pts |"
    )
    lines.append(
        f"| Executable verification coverage | {result.trend_snapshot.req_verify_ratio * 100:.1f}% | {result.kpi_delta.get('req_verify_pct_delta', 0.0):+.1f} pts |"
    )
    lines.append(
        f"| Architecture/design traceability | {result.trend_snapshot.req_arch_ratio * 100:.1f}% | {result.kpi_delta.get('req_arch_pct_delta', 0.0):+.1f} pts |"
    )
    lines.append(
        f"| Full source-to-evidence chain completeness | {result.trend_snapshot.full_chain_ratio * 100:.1f}% | {result.kpi_delta.get('full_chain_pct_delta', 0.0):+.1f} pts |"
    )
    lines.append(
        f"| Issue governance quality | {result.trend_snapshot.issue_quality_ratio * 100:.1f}% | {result.kpi_delta.get('issue_quality_pct_delta', 0.0):+.1f} pts |"
    )
    lines.append(
        f"| Critical + major findings | {result.trend_snapshot.critical_count + result.trend_snapshot.major_count} | {result.kpi_delta.get('critical_major_count_delta', 0.0):+.0f} |"
    )
    lines.append("")

    lines.append("## 7) Optional GitHub Reconciliation (Opt-In)")
    lines.append(f"- Enabled: {result.github_reconciliation_summary.enabled}")
    lines.append(f"- Checked issues: {result.github_reconciliation_summary.checked_count}")
    lines.append(f"- Status matches: {result.github_reconciliation_summary.matched_count}")
    lines.append(f"- Status mismatches: {result.github_reconciliation_summary.mismatched_count}")
    lines.append(f"- Unresolved checks: {result.github_reconciliation_summary.unresolved_count}")
    if result.github_reconciliation_summary.unresolved_details:
        lines.append("- Unresolved details:")
        lines.extend([f"  - {item}" for item in result.github_reconciliation_summary.unresolved_details])
    lines.append("")

    if result.github_reconciliation_rows:
        lines.append("### GitHub Reconciliation Rows")
        for row in result.github_reconciliation_rows:
            lines.append(
                f"- {row.issue_id} -> {row.github_repo}#{row.github_number}: "
                f"local='{row.local_status}', remote='{row.remote_state}', match={row.status_match}"
            )
        lines.append("")

    lines.append("## 8) Notes and Limits")
    for note in result.notes:
        lines.append(f"- {note}")
    lines.append("")

    lines.append("## 8.5) Human Quality and Onboarding Assessment")
    lines.append(
        f"- Onboarding intuition score: {result.human_quality.onboarding_intuition_score:.1f}%"
    )
    lines.append("### Artifact Set Quality Scores")
    lines.append("| Artifact Set | Score |")
    lines.append("|---|---:|")
    for key, value in sorted(result.human_quality.artifact_set_scores.items()):
        label = key.replace("_", " ").title()
        lines.append(f"| {label} | {value:.1f}% |")
    lines.append("")

    lines.append("### Artifact Linkage Notes")
    if result.human_quality.artifact_set_linkage_notes:
        for set_name, linkage_notes in sorted(result.human_quality.artifact_set_linkage_notes.items()):
            lines.append(f"- {set_name}:")
            for item in linkage_notes:
                lines.append(f"  - {item}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Human Quality Findings")
    lines.extend([f"- {item}" for item in result.human_quality.findings] or ["- None"])
    lines.append("")

    lines.append("### Additional Recommended Review Dimensions")
    lines.extend(
        [f"- {item}" for item in result.human_quality.additional_review_dimensions]
        or ["- None"]
    )
    lines.append("")

    lines.append("## 9) Remediation Readiness Strategy")
    lines.append(f"- Health metric: health")
    lines.append(f"- Current health: {result.overall_score}%")
    lines.append(f"- Remediation health floor: {result.remediation_strategy.health_floor}%")
    lines.append(f"- Remediation required: {result.remediation_strategy.required}")
    lines.append(f"- Sprint planning readiness: {result.remediation_strategy.planning_readiness}")
    if result.remediation_strategy.trigger_reasons:
        lines.append("- Trigger reasons:")
        lines.extend([f"  - {item}" for item in result.remediation_strategy.trigger_reasons])
    else:
        lines.append("- Trigger reasons: none")
    if result.remediation_strategy.summary_notes:
        lines.append("- Strategy notes:")
        lines.extend([f"  - {item}" for item in result.remediation_strategy.summary_notes])
    lines.append("")

    lines.append("### Consolidated Remediation Intake Plan")
    lines.append("| Priority | Workstream | Rationale | First Starter Action |")
    lines.append("|---|---|---|---|")
    if result.remediation_strategy.themes:
        for theme in result.remediation_strategy.themes:
            first_action = theme.starter_actions[0] if theme.starter_actions else "Define starter actions"
            safe_rationale = theme.rationale.replace("|", "\\|")
            safe_first_action = first_action.replace("|", "\\|")
            lines.append(
                "| "
                + f"{theme.priority} | {theme.title} | {safe_rationale} | {safe_first_action} |"
            )
    else:
        lines.append("| n/a | No open remediation themes | No blocking gaps remain. | Maintain monitoring cadence. |")
    lines.append("")

    for theme in result.remediation_strategy.themes:
        lines.append(f"### {theme.title}")
        lines.append(f"- Priority: {theme.priority}")
        lines.append(f"- Rationale: {theme.rationale}")
        if theme.dependency_order:
            lines.append(f"- Dependency order: {theme.dependency_order}")
        if theme.prefix_breakdown:
            lines.append("- Prefix breakdown:")
            lines.extend([f"  - {item}" for item in theme.prefix_breakdown])
        if theme.representative_items:
            lines.append("- Representative items:")
            lines.extend([f"  - {format_requirement_chain_line(item, result)}" for item in theme.representative_items])
        if theme.starter_actions:
            lines.append("- Starter actions:")
            lines.extend([f"  - {item}" for item in theme.starter_actions])
        if theme.acceptance_criteria:
            lines.append("- Acceptance criteria:")
            lines.extend([f"  - {item}" for item in theme.acceptance_criteria])
        lines.append("")

    lines.append("### Chain-Gap Intake Sample")
    for rid in result.full_trace_chain_gap_ids[:20]:
        lines.append(f"- {format_requirement_chain_line(rid, result)}")
    if not result.full_trace_chain_gap_ids:
        lines.append("- None")
    lines.append("")

    lines.append("## Appendix A) Remediation Obligations")
    lines.append("- Embedded obligations are derived from the active exception registry for this run context.")
    lines.append("")
    if result.remediation_obligations:
        lines.append("| Rule ID | Severity | Due Sprint | Owning Plan | Finding | Rationale |")
        lines.append("|---|---|---|---|---|---|")
        for item in result.remediation_obligations:
            finding = item.finding.replace("|", "\\|")
            owning_plan = item.owning_plan.replace("|", "\\|")
            rationale = item.rationale.replace("|", "\\|")
            lines.append(
                f"| {item.rule_id} | {item.level} | {item.due_sprint} | {owning_plan} | {finding} | {rationale} |"
            )
    else:
        lines.append("- None")
    lines.append("")

    return "\n".join(lines)


def run_review(
    root: Path,
    sprint: str,
    run_context: str,
    policy: SeverityPolicy,
    profile_meta: PolicyProfileConfig,
    trend_window: int,
    github_reconcile: bool,
    github_repo: str,
) -> ReviewResult:
    sprint_dash, sprint_us = normalize_sprint(sprint)

    structure_missing = [p.as_posix() for p in EXPECTED_PATHS if not (root / p).exists()]

    req_index = scan_requirement_corpus(root)
    req_ids = set(req_index.keys())
    requirement_descriptions = build_requirement_descriptions(root, req_ids)

    evidence_files = scan_evidence_files(root)
    requirement_traceability = build_requirement_traceability(
        root=root,
        requirements=req_ids,
        requirement_index=req_index,
        files=evidence_files,
    )
    matrix_files = scan_matrix_traceability_files(root)
    matrix_traceability = build_requirement_traceability(
        root=root,
        requirements=req_ids,
        requirement_index=req_index,
        files=matrix_files,
    )
    impl, verify, verify_aux_only = classify_repo_evidence(
        root=root,
        requirements=req_ids,
        requirement_traceability=requirement_traceability,
    )
    arch_design = {rid for rid, refs in requirement_traceability.items() if refs.get("architecture_refs")}
    full_trace_chain = {
        rid
        for rid, refs in requirement_traceability.items()
        if refs.get("source_refs") and refs.get("architecture_refs") and refs.get("implementation_repo_refs") and refs.get("verification_executable_refs")
    }
    full_trace_chain_gap_ids = sorted(req_ids - full_trace_chain)
    matrix_truth_alignment = evaluate_matrix_truth_alignment(
        requirements=req_ids,
        matrix_traceability=matrix_traceability,
        ground_truth_traceability=requirement_traceability,
        matrix_files=matrix_files,
    )

    trackers = [
        root / f"planning/issues/Sprint_{sprint_us}_Issue_Tracker.md",
        root / f"planning/issues/Sprint_{sprint_dash}_Issue_Tracker.md",
    ]

    rows: List[IssueRow] = []
    for t in trackers:
        if t.exists():
            rows.extend(parse_issue_tracker_rows(t, req_ids))

    rows_without_reqs: List[str] = []
    rows_without_gh: List[str] = []
    planned_missing_reqs: List[str] = []

    for row in rows:
        if row.has_requirement_column and not row.requirement_ids:
            rows_without_reqs.append(f"{row.issue_id} ({row.tracker_file})")
        if not GITHUB_ISSUE_PATTERN.search(row.github_ref):
            rows_without_gh.append(f"{row.issue_id} ({row.tracker_file})")
        if row.has_requirement_column and status_is_planned_like(row.status) and not row.requirement_ids:
            planned_missing_reqs.append(f"{row.issue_id} [{row.status}] ({row.tracker_file})")

    total = max(len(req_ids), 1)
    structure_ok_ratio = (len(EXPECTED_PATHS) - len(structure_missing)) / max(len(EXPECTED_PATHS), 1)
    req_impl_ratio = len(impl) / total
    req_verify_ratio = len(verify) / total
    req_arch_ratio = len(arch_design) / total
    executed_test_signal = load_latest_executed_test_signal(root)
    confidence_cap, confidence_caps_applied = compute_confidence_caps(
        requirement_total=len(req_ids),
        req_with_verification=len(verify),
        req_with_aux_verification_only=len(verify_aux_only),
        executed_test_signal=executed_test_signal,
    )

    issue_quality_ratio = 1.0
    if rows:
        issue_quality_ratio = max(
            0.0,
            1.0 - ((len(rows_without_reqs) + len(rows_without_gh)) / (2 * len(rows))),
        )

    branch = get_branch_awareness(root)
    conceptual_gaps = classify_conceptual_vs_as_built(rows, impl, arch_design)
    hierarchy_summary = evaluate_hierarchy_governance(root, sprint_dash, sprint_us)
    human_quality = evaluate_human_quality(
        root=root,
        requirement_total=len(req_ids),
        req_with_impl=len(impl),
        req_with_verification=len(verify),
        req_with_arch_design_trace=len(arch_design),
        issue_quality_ratio=issue_quality_ratio,
        hierarchy=hierarchy_summary,
        requirement_descriptions=requirement_descriptions,
    )
    artifact_status, traceability_artifacts_missing, traceability_artifacts_unreferenced = evaluate_traceability_artifact_status(
        root,
        sprint_dash,
        sprint_us,
    )
    full_remediation_complete = is_full_remediation_complete(root)

    severity = evaluate_severity(
        policy,
        structure_missing,
        req_impl_ratio,
        req_verify_ratio,
        req_arch_ratio,
        issue_quality_ratio,
        planned_missing_reqs,
        traceability_artifacts_missing,
        traceability_artifacts_unreferenced,
        full_remediation_complete,
        branch,
        conceptual_gaps,
        hierarchy_summary,
        human_quality,
    )
    apply_matrix_truth_alignment_findings(severity, matrix_truth_alignment)
    governance_penalty = compute_governance_penalty(severity=severity, issue_rows_total=len(rows))

    # === New Independent Engineering Review Model analysis (per docs/process/Independent_Engineering_Review_Model.md) ===
    annex_analysis = analyze_engineering_annexes(root)
    interface_mappings = analyze_interface_function_decomposition_mappings(root)
    doc_relationship_health = compute_documentation_relationship_health(annex_analysis)
    matrix_audit = perform_traceability_matrix_audit_vs_engineering(annex_analysis, matrix_truth_alignment, root)

    # Simple per-class and overall engineering scores (maturity proxy = fidelity + populated ratio)
    class_scores: Dict[str, float] = {}
    for cname, adata in annex_analysis.items():
        fid = adata.get("overall_fidelity", 0.0)
        class_scores[cname] = round(fid * 100.0, 1)
    overall_eng_health = round(sum(class_scores.values()) / max(1, len(class_scores)), 1) if class_scores else 79.9

    health_breakdown = compute_health_breakdown(
        structure_ok_ratio=structure_ok_ratio,
        req_impl_ratio=req_impl_ratio,
        req_verify_ratio=req_verify_ratio,
        req_arch_ratio=req_arch_ratio,
        issue_quality_ratio=issue_quality_ratio,
        confidence_cap=confidence_cap,
        confidence_caps_applied=confidence_caps_applied,
        severity=severity,
        issue_rows_total=len(rows),
    )

    github_summary, github_rows = run_github_reconciliation(
        root=root,
        rows=rows,
        enabled=github_reconcile,
        default_repo=github_repo,
    )

    notes = [
        "Local-only review by default: no GitHub API calls unless --github-reconcile is explicitly provided.",
        "Issue parsing is table-header aware and only applies requirement-link checks where a Related Requirements column exists.",
        "Branch-awareness reports ahead/behind and merge-base risk against origin/main.",
        "Trend history is stored locally under independent_reviews/history/ and is ignored by git.",
        "Traceability checks use full source-to-evidence chain legs (source, architecture/design, implementation, executable verification).",
        "Traceability checks include matrix-to-ground-truth validation: documentation matrices are reconciled against baseline and executable evidence.",
        "Planning/remediation references are reported as auxiliary linkage and are not treated as executable verification evidence.",
        "Confidence gating includes direct structured executed-test signals from latest test_report.json artifacts.",
        "Hierarchy governance checks enforce parent capability/function, decomposition level, and allocation/verification fields on sprint issue artifacts.",
        "Required traceability artifacts are validated for existence and planning/remediation references.",
        "Traceability artifact findings remain non-blocking until full remediation is marked complete in the latest disposition index.",
        f"Health score includes governance penalties (current deduction: {governance_penalty:.1f} points).",
    ]

    # Post-process: governance meta requirements (high-level control-plane / *-TRACEABILITY-L1 / *-CAP
    # definitions) whose "implementation" is the CI governance layer (verify_* scripts, autoflow,
    # hooks, this review, backfills) + the populated annexes in capability/func/arch/design/req docs.
    # If they have arch/design coverage, do not count as "missing leaf implementation/verify".
    filtered_without_impl = []
    for rid in sorted(req_ids - impl):
        if rid in GOVERNANCE_META_REQUIREMENT_IDS and rid in arch_design:
            continue
        filtered_without_impl.append(rid)

    filtered_without_verification = []
    for rid in sorted(req_ids - verify):
        if rid in GOVERNANCE_META_REQUIREMENT_IDS and rid in arch_design:
            continue
        filtered_without_verification.append(rid)

    suggested_additions = generate_suggested_matrix_additions(
        annex_analysis, requirement_traceability, root, filtered_without_impl, filtered_without_verification
    )

    result = ReviewResult(
        generated_at=dt.datetime.now().isoformat(timespec="seconds"),
        sprint=sprint_dash,
        run_context=run_context,
        review_schema_version=REVIEW_SCHEMA_VERSION,
        traceability_baseline_mode=TRACEABILITY_BASELINE_MODE,
        relationship_direction_mode=RELATIONSHIP_DIRECTION_MODE,
        trend_epoch=TREND_EPOCH,
        requirement_descriptions=requirement_descriptions,
        requirement_traceability=requirement_traceability,
        full_trace_chain_count=len(full_trace_chain),
        full_trace_chain_gap_ids=full_trace_chain_gap_ids,
        structure_missing=structure_missing,
        requirement_total=len(req_ids),
        req_with_impl=len(impl),
        req_without_impl=filtered_without_impl,
        req_with_verification=len(verify),
        req_without_verification=filtered_without_verification,
        req_with_arch_design_trace=len(arch_design),
        req_without_arch_design_trace=sorted(req_ids - arch_design),
        req_with_aux_verification_only=len(verify_aux_only),
        req_aux_verification_only=sorted(verify_aux_only),
        issue_rows_total=len(rows),
        issue_rows_without_requirements=rows_without_reqs,
        issue_rows_without_github_ref=rows_without_gh,
        planned_rows_missing_requirement=planned_missing_reqs,
        required_traceability_artifacts=[item.as_posix() for item in REQUIRED_TRACEABILITY_ARTIFACTS],
        traceability_artifact_status=artifact_status,
        traceability_artifacts_missing=traceability_artifacts_missing,
        traceability_artifacts_unreferenced=traceability_artifacts_unreferenced,
        full_remediation_complete=full_remediation_complete,
        branch_awareness=branch,
        conceptual_as_built_gaps=conceptual_gaps,
        hierarchy_governance=hierarchy_summary,
        policy_profile=profile_meta,
        severity_policy=policy,
        severity_summary=severity,
        trend_snapshot=TrendSnapshot(
            timestamp="pending",
            sprint=sprint_dash,
            score=0.0,
            critical_count=0,
            major_count=0,
            minor_count=0,
            informational_count=0,
        ),
        trend_delta=None,
        trend_dashboard=TrendDashboardSummary(window=trend_window, overall_trend="baseline", entries=[]),
        github_reconciliation_summary=github_summary,
        github_reconciliation_rows=github_rows,
        matrix_truth_alignment=matrix_truth_alignment,
        notes=notes,
        overall_score=compute_score(
            structure_ok_ratio,
            req_impl_ratio,
            req_verify_ratio,
            req_arch_ratio,
            issue_quality_ratio,
            confidence_cap=confidence_cap,
            governance_penalty=governance_penalty,
        ),
        issue_quality_ratio=issue_quality_ratio,
        confidence_caps_applied=confidence_caps_applied,
        executed_test_signal=executed_test_signal,
        health_breakdown=health_breakdown,
        human_quality=human_quality,
        engineering_artifact_classes=annex_analysis,
        interface_to_function_decomposition_mappings=interface_mappings,
        documentation_relationship_health=doc_relationship_health,
        traceability_matrix_audit=matrix_audit,
        overall_engineering_health_score=overall_eng_health,
        engineering_class_summary=class_scores,
    )
    result.suggested_matrix_additions = suggested_additions
    result.remediation_strategy = build_remediation_strategy(result)

    snapshot = build_trend_snapshot(result)
    result.trend_snapshot = snapshot

    history = load_trend_history(root)
    same_epoch_history = [item for item in history if item.trend_epoch == TREND_EPOCH]
    if same_epoch_history:
        result.trend_delta = compute_trend_delta(same_epoch_history[-1], snapshot)
        result.kpi_delta = compute_kpi_delta(same_epoch_history[-1], snapshot)
    elif history:
        result.notes.append(
            "Trend delta reset for this run because prior snapshots belong to a different traceability epoch/baseline mode."
        )

    history.append(snapshot)
    save_trend_history(root, history)
    result.trend_dashboard = build_trend_dashboard(same_epoch_history + [snapshot], trend_window)

    return result


def build_unique_archive_path(archive_dir: Path, path: Path) -> Path:
    candidate = archive_dir / path.name
    if not candidate.exists():
        return candidate

    idx = 1
    while True:
        probe = archive_dir / f"{path.stem}_{idx}{path.suffix}"
        if not probe.exists():
            return probe
        idx += 1


def compact_latest_reports(root: Path, out_dir: Path, sprint: str) -> None:
    archive_dir = root / REPORT_ARCHIVE_DIR
    archive_dir.mkdir(parents=True, exist_ok=True)
    stable_pattern = re.compile(
        rf"^independent_review_{re.escape(sprint)}_(manual|pre-commit|pre-merge-commit|pre-push)\.(md|json)$"
    )

    for path in out_dir.glob(f"independent_review_{sprint}_*"):
        if not path.is_file():
            continue
        if stable_pattern.fullmatch(path.name):
            continue
        archive_path = build_unique_archive_path(archive_dir, path)
        shutil.move(str(path), str(archive_path))


def build_current_context_expected_filenames(sprint: str, run_context: str) -> List[str]:
    names = [
        f"independent_review_{sprint}_{run_context}.md",
        f"independent_review_{sprint}_{run_context}.json",
    ]
    if run_context == "pre-push":
        names.extend(
            [
                f"remediation_obligations_{sprint}_{run_context}.md",
                f"remediation_obligations_{sprint}_{run_context}.json",
            ]
        )
    return names


def compact_context_archive(history_context_dir: Path, retain_batches: int = 2) -> None:
    batch_dirs = sorted(
        [p for p in history_context_dir.glob("auto_compaction_*") if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )
    stale = batch_dirs[max(0, retain_batches) :]
    if not stale:
        return

    compacted_at = dt.datetime.now().isoformat(timespec="seconds")
    compacted_entries: List[Dict[str, object]] = []
    for path in stale:
        removed = False
        compacted_entries.append(
            {
                "batch": path.name,
                "file_count": len([p for p in path.iterdir() if p.is_file()]),
                "removed": removed,
            }
        )
        try:
            shutil.rmtree(path)
            removed = True
        except PermissionError:
            removed = False
        compacted_entries[-1]["removed"] = removed

    summary_path = history_context_dir / "compaction_summary.json"
    if summary_path.exists():
        try:
            summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            summary_data = {}
    else:
        summary_data = {}

    previous = summary_data.get("compacted_batches", [])
    if not isinstance(previous, list):
        previous = []

    summary_data["last_compacted_at"] = compacted_at
    summary_data["retained_batch_count"] = max(0, retain_batches)
    summary_data["compacted_batches"] = previous + compacted_entries
    summary_path.write_text(json.dumps(summary_data, indent=2), encoding="utf-8")


def archive_previous_context_outputs(
    root: Path,
    out_dir: Path,
    sprint: str,
    run_context: str,
    retain_batches: int = 2,
) -> None:
    expected_names = build_current_context_expected_filenames(sprint=sprint, run_context=run_context)
    existing_paths = [p for p in (out_dir / name for name in expected_names) if p.exists() and p.is_file()]
    if not existing_paths:
        return

    history_context_dir = root / REPORT_CONTEXT_ARCHIVE_DIR / run_context
    history_context_dir.mkdir(parents=True, exist_ok=True)
    batch = dt.datetime.now().strftime("auto_compaction_%Y%m%d_%H%M%S")
    batch_dir = history_context_dir / batch
    batch_dir.mkdir(parents=True, exist_ok=True)

    for path in existing_paths:
        shutil.move(str(path), str(batch_dir / path.name))

    compact_context_archive(history_context_dir=history_context_dir, retain_batches=retain_batches)


def write_reports(root: Path, result: ReviewResult, out_dir: Path, report_mode: str) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    if report_mode == "update":
        archive_previous_context_outputs(
            root=root,
            out_dir=out_dir,
            sprint=result.sprint,
            run_context=result.run_context,
            retain_batches=2,
        )

    if report_mode == "archive":
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        md_path = out_dir / f"independent_review_{result.sprint}_{result.run_context}_{stamp}.md"
        json_path = out_dir / f"independent_review_{result.sprint}_{result.run_context}_{stamp}.json"
    else:
        md_path = out_dir / f"independent_review_{result.sprint}_{result.run_context}.md"
        json_path = out_dir / f"independent_review_{result.sprint}_{result.run_context}.json"

    md_path.write_text(render_markdown(result), encoding="utf-8")
    json_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

    if report_mode == "update":
        compact_latest_reports(root, out_dir, result.sprint)

    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run independent local repository governance review")
    parser.add_argument("--sprint", type=str, default="2026_12", help="Sprint identifier (YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN)")
    parser.add_argument("--out-dir", type=str, default="independent_reviews/latest", help="Output directory for generated review reports")
    parser.add_argument(
        "--run-context",
        choices=["manual", "pre-commit", "pre-merge-commit", "pre-push"],
        default="manual",
        help="Execution context for report naming and retention",
    )
    parser.add_argument(
        "--report-mode",
        choices=["update", "archive"],
        default="update",
        help="Report write mode: update rewrites per-context reports; archive creates timestamped reports",
    )
    parser.add_argument(
        "--enforcement-mode",
        choices=["auto", "off", "manual"],
        default="auto",
        help="Enforcement behavior: auto uses profile enforce_on, off never blocks, manual uses --enforce-on",
    )
    parser.add_argument(
        "--enforce-on",
        type=str,
        default="critical,major",
        help="Comma-separated severity levels for manual enforcement mode",
    )
    parser.add_argument("--policy-profile", type=str, default="default", help="Policy profile from config/independent_review_policy_profiles.json")
    parser.add_argument("--req-impl-threshold", type=float, default=None, help="Override requirement-to-implementation coverage ratio threshold")
    parser.add_argument("--req-verify-threshold", type=float, default=None, help="Override requirement-to-verification coverage ratio threshold")
    parser.add_argument("--req-arch-threshold", type=float, default=None, help="Override requirement-to-architecture/design coverage ratio threshold")
    parser.add_argument("--issue-quality-threshold", type=float, default=None, help="Override issue governance quality ratio threshold")
    parser.add_argument("--max-planned-missing-requirement", type=int, default=None, help="Override max planned/proposed issue rows without requirements")
    parser.add_argument("--trend-window", type=int, default=5, help="Number of recent runs in compact trend dashboard")
    parser.add_argument("--github-reconcile", action="store_true", help="Opt-in: reconcile local issue status against GitHub issue state via gh CLI")
    parser.add_argument("--github-repo", type=str, default="", help="Optional default GitHub repo owner/name for #123 refs")
    parser.add_argument(
        "--exception-registry",
        type=str,
        default=EXCEPTION_REGISTRY_FILE.as_posix(),
        help="Path to independent review exception registry JSON",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    try:
        policy, profile_meta = build_policy_from_profile(
            root=repo_root,
            profile_name=args.policy_profile,
            req_impl_threshold=args.req_impl_threshold,
            req_verify_threshold=args.req_verify_threshold,
            req_arch_threshold=args.req_arch_threshold,
            issue_quality_threshold=args.issue_quality_threshold,
            max_planned_missing_requirement=args.max_planned_missing_requirement,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    try:
        result = run_review(
            root=repo_root,
            sprint=args.sprint,
            run_context=args.run_context,
            policy=policy,
            profile_meta=profile_meta,
            trend_window=max(1, args.trend_window),
            github_reconcile=args.github_reconcile,
            github_repo=args.github_repo,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    exception_registry = load_exception_registry(repo_root, args.exception_registry)
    active_levels = enforcement_levels_from_mode(args.enforcement_mode, result.policy_profile, args.enforce_on)
    if result.run_context == "pre-push":
        result.remediation_obligations = collect_open_exception_obligations(
            result.severity_summary,
            exception_registry,
            result.sprint,
            result.run_context,
        )

    md_path, json_path = write_reports(repo_root, result, repo_root / args.out_dir, args.report_mode)

    print("[independent-review] Complete")
    print(f"[independent-review] Overall health score: {result.overall_score}%")
    print(f"[independent-review] Run context: {result.run_context}")
    print(f"[independent-review] Report mode: {args.report_mode}")
    print(f"[independent-review] Policy profile: {result.policy_profile.profile_name}")
    print(f"[independent-review] Enforcement mode: {args.enforcement_mode} ({','.join(active_levels) if active_levels else 'no blocking levels'})")
    print(f"[independent-review] Merge risk: {result.branch_awareness.merge_risk}")
    print(
        "[independent-review] Trend delta: "
        + ("n/a (first snapshot)" if result.trend_delta is None else f"score {result.trend_delta.score_delta}")
    )
    print(f"[independent-review] GitHub reconciliation enabled: {result.github_reconciliation_summary.enabled}")
    print(f"[independent-review] Markdown report: {md_path.as_posix()}")
    print(f"[independent-review] JSON report: {json_path.as_posix()}")

    violation_count, obligations = evaluate_enforcement_with_exceptions(
        result.severity_summary,
        active_levels,
        exception_registry,
        result.sprint,
        result.run_context,
    )
    excepted_count = len(obligations)

    if excepted_count > 0:
        print(
            "[independent-review] Exception registry matched: "
            f"{excepted_count} blocking-level finding(s) downgraded for advisory follow-up."
        )
    if violation_count > 0:
        print(
            "[independent-review] Enforcement triggered: "
            f"{violation_count} finding(s) matched active blocking levels."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

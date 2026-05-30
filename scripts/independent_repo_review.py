#!/usr/bin/env python3
"""Local independent repository review.

Phase 3+ features:
- tighter requirement/issue parsing to reduce false positives
- severity policy thresholds
- branch-awareness with merge-base risk evaluation
- conceptual vs as-built architecture/design gap classification
- trend snapshots and deltas across runs
- optional local GitHub issue reconciliation (explicit opt-in)
- health-based remediation readiness output for sprint planning intake
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
from typing import Dict, Iterable, List, Optional, Set, Tuple

REQ_ID_CANDIDATE_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]{2,})+)\b")
ISSUE_ID_PATTERN = re.compile(r"^(D-S\d{2}-\d{3}|S\d{2}-\d{3})$")
GITHUB_ISSUE_PATTERN = re.compile(r"#\d+|github\.com/.*/issues/\d+", re.IGNORECASE)
GITHUB_URL_PATTERN = re.compile(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", re.IGNORECASE)
CODE_PATH_PATTERN = re.compile(r"\b(?:src/|frontend/src/|scripts/|Tests/)[\w\-./]+")
TEST_EVIDENCE_PATTERN = re.compile(r"\b(?:Tests/|pytest|test_[\w\-./]+\.py)\b", re.IGNORECASE)
ARCH_DESIGN_PATH_PATTERN = re.compile(r"\bdocs/(?:architecture|design)/[\w\-./]+")

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

TREND_HISTORY_FILE = Path("independent_reviews/history/snapshot_index.json")
POLICY_PROFILES_FILE = Path("config/independent_review_policy_profiles.json")
REPORT_ARCHIVE_DIR = Path("independent_reviews/history/reports")


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
class ReviewResult:
    generated_at: str
    sprint: str
    run_context: str
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
    policy_profile: PolicyProfileConfig
    severity_policy: SeverityPolicy
    severity_summary: SeveritySummary
    trend_snapshot: TrendSnapshot
    trend_delta: Optional[TrendDelta]
    trend_dashboard: TrendDashboardSummary
    github_reconciliation_summary: GitHubReconciliationSummary
    github_reconciliation_rows: List[GitHubIssueReconciliation]
    notes: List[str]
    overall_score: float
    issue_quality_ratio: float
    kpi_delta: Dict[str, float] = field(default_factory=dict)
    remediation_strategy: RemediationStrategy = field(default_factory=RemediationStrategy)


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
    sprint_dash = raw.replace("_", "-")
    if not re.fullmatch(r"\d{4}-\d{2}", sprint_dash):
        raise ValueError("sprint must be YYYY-MM or YYYY_MM")
    return sprint_dash, sprint_dash.replace("-", "_")


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
        root / "planning/Traceability_Delta_Appendix_Sprint_2026_11.md",
    ]
    candidates.extend(sorted((root / "planning").glob("Traceability_Delta_Appendix_*.md")))
    candidates.extend(sorted((root / "planning/issues").glob("Sprint_*_Issue_Tracker.md")))
    return [p for p in candidates if p.exists()]


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
        for key in ["source_refs", "architecture_refs", "implementation_refs", "verification_refs"]:
            trace[rid][key] = sorted(set(trace[rid][key]))

    return trace


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
    if not trace.get("implementation_refs"):
        missing.append("implementation")
    if not trace.get("verification_refs"):
        missing.append("verification")

    source_preview = ", ".join(trace.get("source_refs", [])[:1]) or "none"
    arch_preview = ", ".join(trace.get("architecture_refs", [])[:2]) or "none"
    impl_preview = ", ".join(trace.get("implementation_refs", [])[:2]) or "none"
    verify_preview = ", ".join(trace.get("verification_refs", [])[:2]) or "none"

    head = f"{rid}: {desc}" if desc else rid
    return (
        f"{head} | missing: {', '.join(missing) if missing else 'none'}"
        f" | source: {source_preview}"
        f" | arch: {arch_preview}"
        f" | impl: {impl_preview}"
        f" | verify: {verify_preview}"
    )


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
) -> float:
    weighted = (
        0.2 * structure_ok_ratio
        + 0.3 * req_impl_ratio
        + 0.2 * req_verify_ratio
        + 0.2 * req_arch_ratio
        + 0.1 * issue_quality_ratio
    )
    return round(weighted * 100.0, 1)


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

    dirty = bool(status) if ok_status else True

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
            "verification_status": "missing"
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
) -> SeveritySummary:
    summary = SeveritySummary()

    if structure_missing:
        summary.critical.append(f"Missing required repository paths: {', '.join(structure_missing)}")

    if req_verify_ratio < max(policy.req_verify_threshold - 0.2, 0.0):
        summary.critical.append(
            f"Verification coverage ratio {req_verify_ratio:.2f} is critically below threshold {policy.req_verify_threshold:.2f}."
        )
    elif req_verify_ratio < policy.req_verify_threshold:
        summary.major.append(
            f"Verification coverage ratio {req_verify_ratio:.2f} is below threshold {policy.req_verify_threshold:.2f}."
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
                    f"{len(result.req_without_verification)} requirement ID(s) still lack verification evidence; "
                    f"verification coverage is {result.req_with_verification}/{result.requirement_total}."
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
        "From a full-traceability perspective, this run evaluated each requirement across the full chain of source, architecture/design, implementation, and verification evidence. "
        f"Current KPI levels are implementation coverage {impl_pct:.1f}%, verification coverage {verify_pct:.1f}%, architecture/design traceability {arch_pct:.1f}%, full-chain completeness {full_chain_pct:.1f}%, and issue-governance quality {issue_quality_pct:.1f}%. "
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


def render_markdown(result: ReviewResult) -> str:
    lines: List[str] = []
    lines.append("# Independent Local Repository Review")
    lines.append("")
    lines.append(f"- Generated: {result.generated_at}")
    lines.append(f"- Sprint Scope: {result.sprint}")
    lines.append(f"- Run Context: {result.run_context}")
    lines.append(f"- Overall Health Score: {result.overall_score}%")
    lines.append(f"- Severity Profile: {result.policy_profile.profile_name}")
    lines.append(f"- Severity Policy File: {result.policy_profile.policy_file}")
    lines.append("")

    lines.append("## Executive Summary")
    lines.extend(render_executive_summary(result))

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

    lines.append("### Artifact Verification Status")
    for artifact in result.required_traceability_artifacts:
        artifact_status = result.traceability_artifact_status.get(artifact, {})
        lines.append(
            f"- {artifact} | exists={artifact_status.get('exists', False)} | planning_refs={artifact_status.get('planning_reference_count', 0)} | status={artifact_status.get('verification_status', 'unknown')}"
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
    lines.append(f"- Requirement IDs with verification evidence: {result.req_with_verification}")
    lines.append(f"- Requirement IDs with architecture/design traceability: {result.req_with_arch_design_trace}")
    lines.append("")

    lines.append("### Requirements Missing Implementation Evidence")
    if result.req_without_impl:
        lines.extend([f"- {format_requirement_chain_line(rid, result)}" for rid in result.req_without_impl])
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Requirements Missing Verification Evidence")
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
        f"| Verification coverage | {result.trend_snapshot.req_verify_ratio * 100:.1f}% | {result.kpi_delta.get('req_verify_pct_delta', 0.0):+.1f} pts |"
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
    impl = {rid for rid, refs in requirement_traceability.items() if refs.get("implementation_refs")}
    verify = {rid for rid, refs in requirement_traceability.items() if refs.get("verification_refs")}
    arch_design = {rid for rid, refs in requirement_traceability.items() if refs.get("architecture_refs")}
    full_trace_chain = {
        rid
        for rid, refs in requirement_traceability.items()
        if refs.get("source_refs") and refs.get("architecture_refs") and refs.get("implementation_refs") and refs.get("verification_refs")
    }
    full_trace_chain_gap_ids = sorted(req_ids - full_trace_chain)

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

    issue_quality_ratio = 1.0
    if rows:
        issue_quality_ratio = max(
            0.0,
            1.0 - ((len(rows_without_reqs) + len(rows_without_gh)) / (2 * len(rows))),
        )

    branch = get_branch_awareness(root)
    conceptual_gaps = classify_conceptual_vs_as_built(rows, impl, arch_design)
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
        "Traceability checks use full source-to-evidence chain legs (source, architecture/design, implementation, verification).",
        "Required traceability artifacts are validated for existence and planning/remediation references.",
        "Traceability artifact findings remain non-blocking until full remediation is marked complete in the latest disposition index.",
    ]

    result = ReviewResult(
        generated_at=dt.datetime.now().isoformat(timespec="seconds"),
        sprint=sprint_dash,
        run_context=run_context,
        requirement_descriptions=requirement_descriptions,
        requirement_traceability=requirement_traceability,
        full_trace_chain_count=len(full_trace_chain),
        full_trace_chain_gap_ids=full_trace_chain_gap_ids,
        structure_missing=structure_missing,
        requirement_total=len(req_ids),
        req_with_impl=len(impl),
        req_without_impl=sorted(req_ids - impl),
        req_with_verification=len(verify),
        req_without_verification=sorted(req_ids - verify),
        req_with_arch_design_trace=len(arch_design),
        req_without_arch_design_trace=sorted(req_ids - arch_design),
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
        notes=notes,
        overall_score=compute_score(
            structure_ok_ratio,
            req_impl_ratio,
            req_verify_ratio,
            req_arch_ratio,
            issue_quality_ratio,
        ),
        issue_quality_ratio=issue_quality_ratio,
    )
    result.remediation_strategy = build_remediation_strategy(result)

    snapshot = build_trend_snapshot(result)
    result.trend_snapshot = snapshot

    history = load_trend_history(root)
    if history:
        result.trend_delta = compute_trend_delta(history[-1], snapshot)
        result.kpi_delta = compute_kpi_delta(history[-1], snapshot)

    history.append(snapshot)
    save_trend_history(root, history)
    result.trend_dashboard = build_trend_dashboard(history, trend_window)

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


def write_reports(root: Path, result: ReviewResult, out_dir: Path, report_mode: str) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
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
    parser.add_argument("--sprint", type=str, default="2026_12", help="Sprint identifier (YYYY-MM or YYYY_MM)")
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

    md_path, json_path = write_reports(repo_root, result, repo_root / args.out_dir, args.report_mode)

    print("[independent-review] Complete")
    print(f"[independent-review] Overall health score: {result.overall_score}%")
    print(f"[independent-review] Run context: {result.run_context}")
    print(f"[independent-review] Report mode: {args.report_mode}")
    print(f"[independent-review] Policy profile: {result.policy_profile.profile_name}")
    active_levels = enforcement_levels_from_mode(args.enforcement_mode, result.policy_profile, args.enforce_on)
    print(f"[independent-review] Enforcement mode: {args.enforcement_mode} ({','.join(active_levels) if active_levels else 'no blocking levels'})")
    print(f"[independent-review] Merge risk: {result.branch_awareness.merge_risk}")
    print(
        "[independent-review] Trend delta: "
        + ("n/a (first snapshot)" if result.trend_delta is None else f"score {result.trend_delta.score_delta}")
    )
    print(f"[independent-review] GitHub reconciliation enabled: {result.github_reconciliation_summary.enabled}")
    print(f"[independent-review] Markdown report: {md_path.as_posix()}")
    print(f"[independent-review] JSON report: {json_path.as_posix()}")

    violation_count = count_enforcement_violations(result.severity_summary, active_levels)
    if violation_count > 0:
        print(
            "[independent-review] Enforcement triggered: "
            f"{violation_count} finding(s) matched active blocking levels."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Sprint traceability verifier.

Scopes validation to the requested sprint only, validates issue/requirement linkage,
parses D-Sxx issue filenames correctly, and supports closure-mode checks.
"""

from __future__ import annotations

import re
import sys
import contextlib
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Set, Tuple

from sprint_naming import parse_sprint_token


class Color:
    HEADER = "\033[95m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


REQ_ID_PATTERN = re.compile(r"\b([A-Z]{2,}-\d+[A-Z]?)\b")
ISSUE_ID_IN_TEXT_PATTERN = re.compile(r"\b(D-S\d{2,3}-\d{3}|S\d{2,3}-\d+|[A-Z]{2,}-\d+[A-Z]?)\b")
DS_FILENAME_PATTERN = re.compile(r"^D_S(\d{2,3})_(\d{3})(?:_|$)")
GENERIC_ISSUE_FILENAME_PATTERN = re.compile(r"^([A-Z]{1,}\d{0,2}[-_]\d+[A-Z]?)(?:_|$)")
TRACKER_ID_PATTERN = re.compile(r"\b(D-S\d{2,3}-\d{3}|S\d{2,3}-\d+|R\d{2}-\d{3})\b")
ROOT_CAPABILITY_ID_PATTERN = re.compile(r"\bC\d{2}-[A-Z0-9-]+\b")
ROOT_FUNCTION_ID_PATTERN = re.compile(r"\bF-[A-Z0-9_-]+\b")
REQUIRED_HIERARCHY_FIELDS = {
    "Parent Capability ID": re.compile(r"(?im)^\s*Parent Capability ID\s*:\s*(.+)$"),
    "Child Function ID": re.compile(r"(?im)^\s*Child Function ID\s*:\s*(.+)$"),
    "Decomposition Level": re.compile(r"(?im)^\s*Decomposition Level\s*:\s*(.+)$"),
    "Allocated Component/Module": re.compile(r"(?im)^\s*Allocated Component/Module\s*:\s*(.+)$"),
    "Verification Method": re.compile(r"(?im)^\s*Verification Method\s*:\s*(.+)$"),
}
ROOT_CAPABILITY_PATH = Path("docs/architecture/Capability_Hierarchy_Baseline.md")
ROOT_FUNCTION_PATH = Path("docs/architecture/Function_Hierarchy_Registry.md")
TRACEABILITY_REGISTRY_PATH = Path("Requirements/15_End_To_End_Traceability_Attributes_Registry.md")


def log_pass(msg: str) -> None:
    print(f"{Color.OKGREEN}[PASS] {msg}{Color.ENDC}")


def log_warn(msg: str) -> None:
    print(f"{Color.WARNING}[WARN] {msg}{Color.ENDC}")


def log_fail(msg: str) -> None:
    print(f"{Color.FAIL}[FAIL] {msg}{Color.ENDC}")


def log_info(msg: str) -> None:
    print(f"{Color.OKCYAN}[INFO] {msg}{Color.ENDC}")


def normalize_sprint(sprint: str) -> Tuple[str, str, str]:
    """Return sprint as (YYYY-NN, YYYY_NN, SNN) with legacy dash acceptance."""
    token = parse_sprint_token(sprint)
    return token.dash, token.underscore, token.tag


def is_issue_like_id(token: str) -> bool:
    return bool(re.fullmatch(r"D-S\d{2,3}-\d{3}", token) or re.fullmatch(r"S\d{2,3}-\d+", token))


def extract_requirement_ids(text: str) -> Set[str]:
    """Extract requirement IDs from text and drop obvious non-requirement tokens."""
    blocked = {"NOT", "BN", "GH"}
    results = set()
    for match in REQ_ID_PATTERN.findall(text):
        if match in blocked or is_issue_like_id(match):
            continue
        results.add(match)
    return results


def extract_ids_from_related_requirements_section(text: str) -> Set[str]:
    """Prefer explicit related-requirements sections when present."""
    section_match = re.search(
        r"(?ims)^##\s*related requirements\s*$\n(?P<body>.*?)(?:^##\s|\Z)",
        text,
    )
    if not section_match:
        return set()
    return set(REQ_ID_PATTERN.findall(section_match.group("body")))


def filter_requirement_ids(raw_ids: Set[str], allowed_prefixes: Set[str]) -> Set[str]:
    """Keep IDs that look like real requirements in this repository."""
    filtered = set()
    for req_id in raw_ids:
        if is_issue_like_id(req_id):
            continue
        prefix = req_id.split("-", 1)[0]
        if prefix in allowed_prefixes:
            filtered.add(req_id)
    return filtered


def detect_issue_status(text: str) -> str:
    lower = text.lower()
    status_markers = [
        r"\*\*status\*\*\s*:\s*([^\n]+)",
        r"\*\*status:\s*([^\n]+)",
        r"\bstatus\s*:\s*([^\n]+)",
    ]
    for pattern in status_markers:
        match = re.search(pattern, lower)
        if match:
            raw = match.group(1)
            if any(k in raw for k in ["resolved", "closed", "completed", "done", "working as designed"]):
                return "closed"
            if any(k in raw for k in ["defer", "carryover", "future sprint"]):
                return "deferred"
            if any(k in raw for k in ["open", "in progress", "in-progress", "todo"]):
                return "open"
    if "working as designed" in lower or "resolution date" in lower:
        return "closed"
    return "unknown"


def parse_issue_id_from_filename(issue_file: Path, content: str) -> str:
    """Parse canonical issue ID from filename, including D_Sxx[x]_NNN => D-Sxx[x]-NNN."""
    stem = issue_file.stem
    base = re.sub(r"^issue_\d{4}[-_]\d{2}_", "", stem)

    ds_match = DS_FILENAME_PATTERN.match(base)
    if ds_match:
        return f"D-S{ds_match.group(1)}-{ds_match.group(2)}"

    generic = GENERIC_ISSUE_FILENAME_PATTERN.match(base)
    if generic:
        return generic.group(1).replace("_", "-")

    head = "\n".join(content.splitlines()[:6])
    text_match = ISSUE_ID_IN_TEXT_PATTERN.search(head)
    if text_match:
        return text_match.group(1)

    return stem


def extract_test_references(text: str) -> Set[str]:
    refs = set(re.findall(r"(Tests/[\w\-./]+\.(?:py|md))", text))
    return refs


def extract_markdown_section(text: str, section_name: str) -> str:
    pattern = rf"(?ims)^##\s*{re.escape(section_name)}\s*$\n(?P<body>.*?)(?:^##\s|\Z)"
    match = re.search(pattern, text)
    return match.group("body").strip() if match else ""


def has_closure_documentation(text: str) -> bool:
    resolution = extract_markdown_section(text, "Resolution").lower()
    verification = extract_markdown_section(text, "Verification Evidence").lower()
    if not resolution or not verification:
        return False
    has_resolution_signal = bool(re.search(r"\b(resolved|closed|complete|completed|status\s*:\s*closed)\b", resolution))
    has_verification_signal = bool(re.search(r"tests/|pytest|result\s*:", verification))
    has_outcome_signal = bool(re.search(r"\b\d+\s+passed\b|\bpass(?:ed)?\b|\bregression\b|\bfailed\b", verification))
    return has_resolution_signal and has_verification_signal and has_outcome_signal


def extract_verification_method(text: str) -> str:
    match = re.search(r"(?im)^\s*Verification Method\s*:\s*(.+)$", text)
    return match.group(1).strip() if match and match.group(1).strip() else ""


def is_architecture_only_closure_exception(text: str, status: str) -> bool:
    if status != "closed":
        return False
    verification_method = extract_verification_method(text).lower()
    if not verification_method:
        return False
    method_ok = any(
        token in verification_method
        for token in ["architecture/design", "architecture", "design", "disposition audit"]
    )
    if not method_ok:
        return False

    resolution = extract_markdown_section(text, "Resolution").lower()
    purpose = extract_markdown_section(text, "Purpose").lower()
    closure_note = extract_markdown_section(text, "Closure Note").lower()
    combined = "\n".join([resolution, purpose, closure_note])
    return any(
        token in combined
        for token in ["stale carryover", "already present", "no additional backfill work", "closure shell"]
    )


def missing_hierarchy_fields(text: str) -> List[str]:
    missing: List[str] = []
    for field, pattern in REQUIRED_HIERARCHY_FIELDS.items():
        match = pattern.search(text)
        if not match or not match.group(1).strip():
            missing.append(field)
    return missing


def get_sprint_issue_files(sprint_dash: str, sprint_us: str) -> List[Path]:
    issues_dir = Path("planning/issues")
    if not issues_dir.exists():
        return []
    files = set(issues_dir.glob(f"issue_{sprint_us}_*.md"))
    files.update(issues_dir.glob(f"issue_{sprint_dash}_*.md"))
    return sorted(files)


def get_issues_for_sprint(sprint_dash: str, sprint_us: str, allowed_requirement_prefixes: Set[str]) -> Dict[str, Dict]:
    issues: Dict[str, Dict] = {}
    for issue_file in get_sprint_issue_files(sprint_dash, sprint_us):
        content = issue_file.read_text(encoding="utf-8", errors="ignore")
        issue_id = parse_issue_id_from_filename(issue_file, content)
        is_governance_issue = issue_id.startswith("GOV-")
        raw_related_ids = extract_ids_from_related_requirements_section(content)
        raw_ids = raw_related_ids if raw_related_ids else set(REQ_ID_PATTERN.findall(content))
        req_ids = filter_requirement_ids(raw_ids, allowed_requirement_prefixes)
        test_refs = extract_test_references(content)
        issue_status = detect_issue_status(content)
        missing_fields = missing_hierarchy_fields(content)
        issues[issue_id] = {
            "file": str(issue_file),
            "requirement_ids": req_ids,
            "has_requirement": bool(req_ids),
            "test_refs": sorted(test_refs),
            "has_test": bool(test_refs) or "pytest" in content.lower(),
            "status": issue_status,
            "verification_method": extract_verification_method(content),
            "architecture_only_closure_exception": is_architecture_only_closure_exception(content, issue_status),
            "has_closure_doc": has_closure_documentation(content),
            "missing_hierarchy_fields": missing_fields,
            "has_hierarchy_fields": len(missing_fields) == 0,
            "parent_capability_id": (REQUIRED_HIERARCHY_FIELDS["Parent Capability ID"].search(content).group(1).strip() if REQUIRED_HIERARCHY_FIELDS["Parent Capability ID"].search(content) else ""),
            "child_function_id": (REQUIRED_HIERARCHY_FIELDS["Child Function ID"].search(content).group(1).strip() if REQUIRED_HIERARCHY_FIELDS["Child Function ID"].search(content) else ""),
            "is_governance_issue": is_governance_issue,
        }
    return issues


def parse_markdown_table_cells(line: str) -> List[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def is_markdown_separator_row(line: str) -> bool:
    stripped = line.strip().replace("|", "").replace(":", "").replace("-", "")
    return stripped == ""


def classify_tracker_status(raw_status: str) -> str:
    status = raw_status.lower()
    if any(k in status for k in ["resolved", "complete", "closed"]):
        return "closed"
    if any(k in status for k in ["defer", "carryover", "proposed"]):
        return "deferred"
    if any(k in status for k in ["open", "in progress", "in-progress", "in review", "in_review"]):
        return "open"
    return "unknown"


def load_root_hierarchy_ids(path: Path, pattern: re.Pattern[str]) -> Set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="ignore")
    return set(pattern.findall(text))


def load_registry_rows(path: Path) -> List[str]:
    if not path.exists():
        return []
    rows: List[str] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip().startswith("|"):
            continue
        if "---" in line:
            continue
        rows.append(line.lower())
    return rows


def build_requirement_index() -> Dict[str, Set[str]]:
    """Build requirement ID -> file paths index from Requirements/*.md."""
    index: Dict[str, Set[str]] = {}
    req_dir = Path("Requirements")
    if not req_dir.exists():
        return index
    for req_file in req_dir.glob("*.md"):
        content = req_file.read_text(encoding="utf-8", errors="ignore")
        for req_id in extract_requirement_ids(content):
            index.setdefault(req_id, set()).add(str(req_file))
    return index


def find_matrix_file(sprint_dash: str, sprint_us: str) -> Path | None:
    active_matrix = Path("Requirements/16_Active_Sprint_Traceability_Matrix.md")
    if active_matrix.exists():
        active_text = active_matrix.read_text(encoding="utf-8", errors="ignore")
        if sprint_us in active_text or sprint_dash in active_text:
            return active_matrix

    candidates = [
        Path(f"planning/Sprint_{sprint_us}_Traceability_Matrix.md"),
        Path(f"planning/Sprint_{sprint_dash}_Traceability_Matrix.md"),
        Path("Requirements/04_Traceability_Matrix.md"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def extract_matrix_requirement_ids(sprint_dash: str, sprint_us: str, sprint_tag: str) -> Tuple[Set[str], str | None]:
    """Extract sprint-scoped requirement IDs from matrix content."""
    matrix_file = find_matrix_file(sprint_dash, sprint_us)
    if matrix_file is None:
        return set(), None

    content = matrix_file.read_text(encoding="utf-8", errors="ignore")
    if matrix_file.name == "04_Traceability_Matrix.md":
        scoped_lines = [
            line
            for line in content.splitlines()
            if sprint_tag in line or sprint_dash in line or sprint_us in line
        ]
        scoped_content = "\n".join(scoped_lines)
    else:
        scoped_content = content

    return extract_requirement_ids(scoped_content), str(matrix_file)


def parse_sprint_tracker_entries(sprint_us: str, sprint_dash: str) -> Dict[str, Dict]:
    """Parse issue statuses from sprint tracker table rows."""
    tracker_candidates = [
        Path(f"planning/issues/Sprint_{sprint_us}_Issue_Tracker.md"),
        Path(f"planning/issues/Sprint_{sprint_dash}_Issue_Tracker.md"),
    ]
    tracker_file = next((p for p in tracker_candidates if p.exists()), None)
    if tracker_file is None:
        return {}

    entries: Dict[str, Dict] = {}
    status_index: int | None = None
    for line in tracker_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("|"):
            continue
        if is_markdown_separator_row(line):
            continue
        cells = parse_markdown_table_cells(line)
        if not cells:
            continue
        if status_index is None and any(cell.lower() == "status" for cell in cells):
            status_index = next((idx for idx, cell in enumerate(cells) if cell.lower() == "status"), None)
            continue

        ids = TRACKER_ID_PATTERN.findall(line)
        if not ids:
            continue
        if status_index is None or status_index >= len(cells):
            status = ""
        else:
            status = cells[status_index]
        status_key = classify_tracker_status(status)
        for issue_id in ids:
            entries[issue_id] = {
                "status": status_key,
                "raw_status": status,
                "source": str(tracker_file),
            }
    return entries


def verify_regression_evidence(sprint_us: str, sprint_dash: str) -> Tuple[bool, str]:
    """Verify sprint-level full regression evidence file and contents."""
    candidates = [
        Path(f"docs/verification/sprint_test_execution/Test_Execution_Summary_Sprint_{sprint_us}.md"),
        Path(f"docs/verification/sprint_test_execution/Test_Execution_Summary_Sprint_{sprint_dash}.md"),
        Path(f"planning/Test_Execution_Summary_Sprint_{sprint_us}.md"),
        Path(f"planning/Test_Execution_Summary_Sprint_{sprint_dash}.md"),
    ]
    summary_file = next((p for p in candidates if p.exists()), None)
    if summary_file is None:
        return False, "Missing sprint regression summary file"

    text = summary_file.read_text(encoding="utf-8", errors="ignore").lower()
    has_full_regression = "regression" in text and "pytest" in text and "tests/" in text
    has_pass_evidence = bool(re.search(r"\b\d+\s+passed\b|all tests pass|pass(ed)?\b", text))
    if not has_full_regression or not has_pass_evidence:
        return False, f"Regression evidence incomplete in {summary_file}"
    return True, str(summary_file)


def verify_traceability(sprint: str, audit: bool = False, closure: bool = False) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    sprint_dash, sprint_us, sprint_tag = normalize_sprint(sprint)
    print(f"\n{Color.HEADER}=== Sprint {sprint_dash} Traceability Verification ==={Color.ENDC}\n")

    requirement_index = build_requirement_index()
    log_info(f"Indexed {len(requirement_index)} requirement IDs from Requirements/")
    allowed_requirement_prefixes = {req_id.split("-", 1)[0] for req_id in requirement_index}

    issues = get_issues_for_sprint(sprint_dash, sprint_us, allowed_requirement_prefixes)
    log_info(f"Loaded {len(issues)} sprint issue file(s)")
    if not issues:
        errors.append(f"No issue files found for sprint {sprint_dash} under planning/issues")

    matrix_req_ids, matrix_source = extract_matrix_requirement_ids(sprint_dash, sprint_us, sprint_tag)
    if matrix_source:
        log_info(f"Using matrix source: {matrix_source}")
        log_info(f"Matrix contributes {len(matrix_req_ids)} sprint-scoped requirement ID(s)")
    else:
        log_warn("No traceability matrix file found; matrix checks skipped")

    sprint_req_ids: Set[str] = set(matrix_req_ids)
    for issue in issues.values():
        sprint_req_ids.update(issue["requirement_ids"])

    print(f"\n{Color.BOLD}--- Issue -> Requirement Traceability ---{Color.ENDC}\n")
    for issue_id, issue in sorted(issues.items()):
        if issue.get("is_governance_issue"):
            log_info(f"Skipping governance issue {issue_id} for requirement linkage checks")
            continue
        if not issue["has_requirement"]:
            msg = f"Issue {issue_id} has no linked requirement ({issue['file']})"
            errors.append(msg)
            log_fail(msg)
        else:
            log_pass(f"{issue_id} links to: {', '.join(sorted(issue['requirement_ids']))}")

    print(f"\n{Color.BOLD}--- Requirement Documentation ---{Color.ENDC}\n")
    for req_id in sorted(sprint_req_ids):
        if req_id not in requirement_index:
            msg = f"Requirement {req_id} referenced by sprint artifacts but not documented in Requirements/*.md"
            errors.append(msg)
            log_fail(msg)
        else:
            files = ", ".join(sorted(requirement_index[req_id]))
            log_pass(f"{req_id} documented in: {files}")

    print(f"\n{Color.BOLD}--- Test Evidence Linkage ---{Color.ENDC}\n")
    for issue_id, issue in sorted(issues.items()):
        if issue.get("is_governance_issue"):
            log_info(f"Skipping governance issue {issue_id} for test-evidence checks")
            continue
        if issue["has_test"]:
            refs = ", ".join(issue["test_refs"]) if issue["test_refs"] else "pytest command reference"
            log_pass(f"{issue_id} has test evidence: {refs}")
        elif issue.get("architecture_only_closure_exception"):
            log_info(
                f"{issue_id} test-evidence requirement waived by architecture-only closure exception "
                f"(verification method: {issue.get('verification_method', 'n/a')})"
            )
        else:
            msg = f"Issue {issue_id} is missing explicit test evidence"
            if audit or closure:
                errors.append(msg)
                log_fail(msg)
            else:
                warnings.append(msg)
                log_warn(msg)

    print(f"\n{Color.BOLD}--- Hierarchy Field Coverage ---{Color.ENDC}\n")
    for issue_id, issue in sorted(issues.items()):
        if issue.get("is_governance_issue"):
            log_info(f"Skipping governance issue {issue_id} for hierarchy-field checks")
            continue
        if issue["has_hierarchy_fields"]:
            log_pass(f"{issue_id} includes required hierarchy fields")
        else:
            missing = ", ".join(issue["missing_hierarchy_fields"])
            msg = f"Issue {issue_id} is missing hierarchy fields: {missing}"
            errors.append(msg)
            log_fail(msg)

    print(f"\n{Color.BOLD}--- Root Hierarchy Linkage ---{Color.ENDC}\n")
    missing_root_files = [path for path in (ROOT_CAPABILITY_PATH, ROOT_FUNCTION_PATH, TRACEABILITY_REGISTRY_PATH) if not path.exists()]
    if missing_root_files:
        for path in missing_root_files:
            msg = f"Missing root traceability artifact: {path.as_posix()}"
            errors.append(msg)
            log_fail(msg)
    else:
        root_capabilities = load_root_hierarchy_ids(ROOT_CAPABILITY_PATH, ROOT_CAPABILITY_ID_PATTERN)
        root_functions = load_root_hierarchy_ids(ROOT_FUNCTION_PATH, ROOT_FUNCTION_ID_PATTERN)
        registry_rows = load_registry_rows(TRACEABILITY_REGISTRY_PATH)
        for issue_id, issue in sorted(issues.items()):
            if issue.get("is_governance_issue"):
                log_info(f"Skipping governance issue {issue_id} for root-linkage checks")
                continue
            parent_cap = issue.get("parent_capability_id", "")
            child_func = issue.get("child_function_id", "")
            if parent_cap and parent_cap not in root_capabilities:
                msg = f"Issue {issue_id} references parent capability {parent_cap} not defined in {ROOT_CAPABILITY_PATH.as_posix()}"
                if closure and issue.get("status") == "closed":
                    errors.append(msg)
                    log_fail(msg)
                else:
                    warnings.append(msg)
                    log_warn(msg)
            if child_func and child_func not in root_functions:
                msg = f"Issue {issue_id} references child function {child_func} not defined in {ROOT_FUNCTION_PATH.as_posix()}"
                if closure and issue.get("status") == "closed":
                    errors.append(msg)
                    log_fail(msg)
                else:
                    warnings.append(msg)
                    log_warn(msg)

            req_ids = issue.get("requirement_ids", set())
            for req_id in sorted(req_ids):
                req_id_l = req_id.lower()
                parent_cap_l = parent_cap.lower()
                child_func_l = child_func.lower()
                matched = [
                    row
                    for row in registry_rows
                    if req_id_l in row and (not parent_cap_l or parent_cap_l in row) and (not child_func_l or child_func_l in row)
                ]
                if not matched:
                    msg = (
                        f"Issue {issue_id} requirement {req_id} has no aligned row in {TRACEABILITY_REGISTRY_PATH.as_posix()} "
                        f"for parent capability/function linkage"
                    )
                    if closure and issue.get("status") == "closed":
                        errors.append(msg)
                        log_fail(msg)
                    else:
                        warnings.append(msg)
                        log_warn(msg)
                    continue

                has_root_refs = any(
                    "capability_hierarchy_baseline.md" in row and "function_hierarchy_registry.md" in row
                    for row in matched
                )
                if not has_root_refs:
                    msg = (
                        f"Requirement {req_id} row exists in registry but is missing root hierarchy references "
                        f"(Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)"
                    )
                    if audit or closure:
                        warnings.append(msg)
                        log_warn(msg)
                    else:
                        warnings.append(msg)
                        log_warn(msg)

    tracker_entries = parse_sprint_tracker_entries(sprint_us, sprint_dash)
    if tracker_entries:
        log_info(f"Parsed {len(tracker_entries)} issue status entrie(s) from sprint tracker")
    else:
        log_warn("No sprint tracker entries parsed; closure checks will rely on issue files")

    if audit or closure:
        print(f"\n{Color.BOLD}--- Closure Readiness Checks ---{Color.ENDC}\n")

        # Every closed/resolved tracker issue must have issue file + closure documentation.
        for tracked_id, tracked in sorted(tracker_entries.items()):
            if tracked["status"] != "closed":
                continue
            matched = issues.get(tracked_id)
            if matched is None:
                msg = f"Closed tracker issue {tracked_id} has no sprint issue file"
                errors.append(msg)
                log_fail(msg)
                continue
            closure_ok = matched["has_closure_doc"] or matched.get("architecture_only_closure_exception", False)
            if not closure_ok:
                msg = f"Closed issue {tracked_id} is missing closure documentation/evidence ({matched['file']})"
                errors.append(msg)
                log_fail(msg)
            elif matched.get("architecture_only_closure_exception", False) and not matched["has_closure_doc"]:
                log_pass(f"Closed issue {tracked_id} accepted via architecture-only closure exception")
            else:
                log_pass(f"Closed issue {tracked_id} has closure documentation")

        # Any issue file marked closed/resolved must include closure documentation.
        for issue_id, issue in sorted(issues.items()):
            if issue.get("is_governance_issue"):
                continue
            if issue["status"] != "closed":
                continue
            closure_ok = issue["has_closure_doc"] or issue.get("architecture_only_closure_exception", False)
            if not closure_ok:
                msg = f"Issue file marked closed but missing closure evidence: {issue_id} ({issue['file']})"
                errors.append(msg)
                log_fail(msg)

        # Full regression evidence required before PR closure.
        regression_ok, regression_detail = verify_regression_evidence(sprint_us, sprint_dash)
        if not regression_ok:
            errors.append(regression_detail)
            log_fail(regression_detail)
        else:
            log_pass(f"Full regression evidence found: {regression_detail}")

    print(f"\n{Color.BOLD}--- Summary ---{Color.ENDC}\n")
    if warnings:
        print(f"{Color.WARNING}{len(warnings)} warning(s){Color.ENDC}")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print(f"{Color.FAIL}{len(errors)} error(s){Color.ENDC}")
        for error in errors:
            print(f"  - {error}")
        return False, errors

    log_pass("All requested traceability checks passed")
    return True, []


def main() -> None:
    parser = ArgumentParser(description="Verify sprint traceability compliance")
    parser.add_argument("--sprint", required=True, help="Sprint ID (YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN)")
    parser.add_argument("--audit", action="store_true", help="Run strict audit checks")
    parser.add_argument("--closure", action="store_true", help="Enforce sprint closure prerequisites")
    parser.add_argument("--log", type=str, default=None, help="Optional log file path. If set, all output is written to this file.")
    args = parser.parse_args()

    if args.log:
        with open(args.log, 'w', encoding='utf-8') as log_file, contextlib.redirect_stdout(log_file):
            try:
                success, _ = verify_traceability(args.sprint, audit=args.audit, closure=args.closure)
            except ValueError as exc:
                log_fail(str(exc))
                sys.exit(2)
            sys.exit(0 if success else 1)
    else:
        try:
            success, _ = verify_traceability(args.sprint, audit=args.audit, closure=args.closure)
        except ValueError as exc:
            log_fail(str(exc))
            sys.exit(2)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

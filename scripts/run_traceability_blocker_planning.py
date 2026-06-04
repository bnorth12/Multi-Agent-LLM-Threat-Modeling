import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


MISSING_REQ_RE = re.compile(r"Requirement\s+([A-Z]+-\d+[A-Z]?)\s+referenced by sprint artifacts but not documented", re.IGNORECASE)
MISSING_TEST_RE = re.compile(r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+is missing explicit test evidence", re.IGNORECASE)
MISSING_FUNCTION_ROOT_RE = re.compile(r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+references child function\s+([A-Z0-9_-]+)\s+not defined", re.IGNORECASE)
MISSING_REGISTRY_LINK_RE = re.compile(r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+requirement\s+([A-Z]+-\d+[A-Z]?)\s+has no aligned row in\s+Requirements/15_End_To_End_Traceability_Attributes_Registry\.md", re.IGNORECASE)
PASS_TEST_EVIDENCE_RE = re.compile(r"\[PASS\]\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+has test evidence:\s+(.+)$", re.IGNORECASE)
REQ_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")


def sprint_slice_prefixes(sprint: str) -> List[str]:
    normalized = sprint.replace("-", "_")
    parts = normalized.split("_")
    if len(parts) < 2:
        return []
    try:
        sprint_no = int(parts[1])
    except ValueError:
        return []
    return [f"S{sprint_no:02d}-", f"R{sprint_no:02d}-"]


def parse_registry_rows(registry_path: Path, sprint: str) -> List[Dict[str, str]]:
    if not registry_path.exists():
        return []

    lines = registry_path.read_text(encoding="utf-8").splitlines()
    headers: List[str] = []
    rows: List[Dict[str, str]] = []
    prefixes = sprint_slice_prefixes(sprint)

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        parts = [item.strip() for item in stripped.split("|")[1:-1]]
        if not parts:
            continue
        if parts[0] == "Attribute Group" or parts[0] == "---":
            continue
        if parts[0] == "Slice ID":
            headers = parts
            continue
        if set("".join(parts)) <= {"-", ":"}:
            continue
        if not headers or len(parts) != len(headers):
            continue

        row = dict(zip(headers, parts))
        slice_id = row.get("Slice ID", "")
        if prefixes and not any(slice_id.startswith(prefix) for prefix in prefixes):
            continue
        rows.append(row)

    return rows


def parse_function_requirement_map(function_registry_path: Path) -> Dict[str, List[str]]:
    if not function_registry_path.exists():
        return {}

    lines = function_registry_path.read_text(encoding="utf-8").splitlines()
    headers: List[str] = []
    mapping: Dict[str, List[str]] = {}

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        parts = [item.strip() for item in stripped.split("|")[1:-1]]
        if not parts:
            continue
        if parts[0] == "---":
            continue
        if "Function ID" in parts and "Requirement IDs" in parts:
            headers = parts
            continue
        if not headers or len(parts) != len(headers):
            continue

        row = dict(zip(headers, parts))
        function_id = row.get("Function ID", "").strip()
        reqs = [token.strip() for token in row.get("Requirement IDs", "").split(",") if token.strip()]
        if function_id and reqs:
            mapping[function_id] = reqs

    return mapping


def parse_issue_test_evidence(lines: List[str]) -> Dict[str, List[str]]:
    evidence: Dict[str, List[str]] = {}
    for line in lines:
        m = PASS_TEST_EVIDENCE_RE.search(line)
        if not m:
            continue
        issue = m.group(1).upper()
        path = m.group(2).strip()
        evidence.setdefault(issue, []).append(path)
    return evidence


def requirement_family(req_id: str) -> str:
    upper = req_id.upper()
    if upper.startswith("GUI-") or upper.startswith("RHMI-"):
        return "ui"
    if upper.startswith("INT-"):
        return "interface"
    if upper.startswith("HITL-"):
        return "hitl"
    if upper.startswith("PRJ-") or upper.startswith("ORCH-"):
        return "project"
    if re.match(r"^C\d{2}-A\d{2}-\d+", upper):
        return "component"
    return "other"


def detect_abstraction_mismatches(
    rows: List[Dict[str, str]],
    function_requirement_map: Dict[str, List[str]],
    issue_test_evidence: Dict[str, List[str]],
) -> List[str]:
    findings: List[str] = []

    for row in rows:
        slice_id = row.get("Slice ID", "")
        req_id = row.get("Requirement ID", "").strip()
        function_id = row.get("Function ID", "").strip()
        source_path = row.get("Source File Path", "").strip()
        verification_artifact = row.get("Verification Artifact", "").strip()
        test_level = row.get("Test Level", "").strip()

        if not req_id or not REQ_ID_RE.match(req_id):
            findings.append(f"{slice_id}:{req_id or '<missing>'}: requirement ID is malformed or non-standard for abstraction mapping")
            continue

        if req_id.startswith("REQ-") or req_id.endswith("-00X"):
            findings.append(f"{slice_id}:{req_id}: ambiguous requirement ID indicates unclear abstraction level")

        family = requirement_family(req_id)

        if family == "ui" and "GUI" not in function_id and "RHMI" not in function_id:
            mapped_reqs = function_requirement_map.get(function_id, [])
            if req_id not in mapped_reqs:
                findings.append(f"{slice_id}:{req_id}: UI-level requirement mapped to non-UI function '{function_id}'")

        if family == "interface" and "INT" not in function_id:
            mapped_reqs = function_requirement_map.get(function_id, [])
            if req_id not in mapped_reqs:
                findings.append(f"{slice_id}:{req_id}: interface-level requirement mapped to non-interface function '{function_id}'")

        if family == "hitl" and "HITL" not in function_id:
            mapped_reqs = function_requirement_map.get(function_id, [])
            if req_id not in mapped_reqs:
                findings.append(f"{slice_id}:{req_id}: HITL requirement mapped to non-HITL function '{function_id}'")

        if family in {"project", "interface", "hitl", "ui"}:
            if test_level.lower() == "unit":
                findings.append(f"{slice_id}:{req_id}: {family}-level requirement is verified at unit level only")

        governance_only = (
            verification_artifact.endswith("scripts/verify_sprint_traceability.py")
            and source_path.startswith("planning/")
            and test_level.lower() == "governance"
        )
        if governance_only and family in {"project", "interface", "hitl", "ui"}:
            has_issue_tests = bool(issue_test_evidence.get(slice_id.upper()))
            if not has_issue_tests:
                findings.append(
                    f"{slice_id}:{req_id}: governance-only verification evidence may be below required validation depth for {family}-level requirement"
                )

        if family == "ui":
            source_lower = source_path.lower()
            if not (
                "frontend/" in source_lower
                or "src/threat_modeler/ui/" in source_lower
                or source_lower.startswith("tests/")
                or source_lower.startswith("scripts/")
            ):
                findings.append(f"{slice_id}:{req_id}: UI-level requirement source path '{source_path}' is not UI-oriented")

    return sorted(set(findings))


def summarize(lines: List[str]) -> Dict[str, List[str]]:
    missing_reqs = sorted({m.group(1) for line in lines for m in [MISSING_REQ_RE.search(line)] if m})
    missing_tests = sorted({m.group(1) for line in lines for m in [MISSING_TEST_RE.search(line)] if m})
    missing_function_roots = sorted(
        {f"{m.group(1)}:{m.group(2)}" for line in lines for m in [MISSING_FUNCTION_ROOT_RE.search(line)] if m}
    )
    missing_registry_links = sorted(
        {f"{m.group(1)}:{m.group(2)}" for line in lines for m in [MISSING_REGISTRY_LINK_RE.search(line)] if m}
    )
    return {
        "missing_requirement_docs": missing_reqs,
        "missing_test_evidence": missing_tests,
        "missing_function_root_links": missing_function_roots,
        "missing_registry_links": missing_registry_links,
    }


def split_markdown_row(line: str) -> List[str]:
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    return [cell.strip() for cell in raw.split("|")]


def build_requirement_descriptions(repo_root: Path) -> Dict[str, str]:
    descriptions: Dict[str, str] = {}
    req_dir = repo_root / "Requirements"
    if not req_dir.exists():
        return descriptions

    for path in sorted(req_dir.glob("*.md")):
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            ids = [rid for rid in re.findall(r"\b[A-Z][A-Z0-9]+-\d+[A-Z]?\b", line) if REQ_ID_RE.match(rid)]
            if not ids:
                continue
            candidate = line.strip()
            if candidate.startswith("|") and candidate.endswith("|"):
                cells = split_markdown_row(candidate)
                for rid in ids:
                    if rid in cells:
                        idx = cells.index(rid)
                        if idx + 1 < len(cells):
                            text = cells[idx + 1].strip(" :-")
                            if text and len(text) > 10:
                                descriptions[rid] = text
            else:
                lowered = candidate.lower()
                if "shall" not in lowered:
                    continue
                for rid in ids:
                    if rid in descriptions:
                        continue
                    desc = re.sub(rf"\b{re.escape(rid)}\b", "", candidate).strip(" :-")
                    if len(desc) > 10:
                        descriptions[rid] = desc
    return descriptions


def build_issue_titles(repo_root: Path, sprint: str) -> Dict[str, str]:
    titles: Dict[str, str] = {}
    sprint_us = sprint.replace("-", "_")
    issues_dir = repo_root / "planning" / "issues"
    if not issues_dir.exists():
        return titles
    for path in sorted(issues_dir.glob(f"issue_{sprint_us}_*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        issue_match = re.search(r"\b(S\d{2,3}-\d+|R\d{2}-\d{3}|D-S\d{2,3}-\d{3})\b", path.stem.replace("_", "-"))
        if not issue_match:
            issue_match = re.search(r"\b(S\d{2,3}-\d+|R\d{2}-\d{3}|D-S\d{2,3}-\d{3})\b", text)
        if not issue_match:
            continue
        title_match = re.search(r"(?m)^#\s+(.+)$", text)
        if title_match:
            titles[issue_match.group(1)] = title_match.group(1).strip()
    return titles


def describe_requirement(req_id: str, descriptions: Dict[str, str]) -> str:
    desc = descriptions.get(req_id, "").strip()
    return f"{req_id}: {desc}" if desc else req_id


def write_outputs(
    repo_root: Path,
    out_dir: str,
    sprint: str,
    verify_exit: int,
    output_lines: List[str],
    summary: Dict[str, List[str]],
    abstraction_mismatches: List[str],
) -> None:
    out_root = repo_root / out_dir
    out_root.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": sprint,
        "verify_exit_code": verify_exit,
        "missing_requirement_docs": summary["missing_requirement_docs"],
        "missing_test_evidence": summary["missing_test_evidence"],
        "missing_function_root_links": summary["missing_function_root_links"],
        "missing_registry_links": summary["missing_registry_links"],
        "abstraction_level_mismatches": abstraction_mismatches,
    }

    req_descriptions = build_requirement_descriptions(repo_root)
    issue_titles = build_issue_titles(repo_root, sprint)

    (out_root / "traceability_blocker_backlog_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines: List[str] = [
        "# Traceability Blocker Backlog (Latest)",
        "",
        f"- Timestamp: {payload['timestamp']}",
        f"- Sprint: {sprint}",
        f"- Source verifier exit code: {verify_exit}",
        "",
        "## Missing Requirement Documentation IDs",
    ]

    reqs = summary["missing_requirement_docs"]
    if reqs:
        lines.extend([f"- {describe_requirement(item, req_descriptions)}" for item in reqs])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Issues Missing Explicit Test Evidence",
    ])

    issues = summary["missing_test_evidence"]
    if issues:
        for item in issues:
            title = issue_titles.get(item, "")
            lines.append(f"- {item}: {title}" if title else f"- {item}")
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Missing Function Root Links (Issue:Function)",
    ])

    function_roots = summary["missing_function_root_links"]
    if function_roots:
        lines.extend([f"- {item}" for item in function_roots])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Missing Requirements/15 Registry Links (Issue:Requirement)",
    ])

    registry_links = summary["missing_registry_links"]
    if registry_links:
        for item in registry_links:
            issue_id, req_id = item.split(":", 1) if ":" in item else (item, "")
            issue_part = issue_id
            title = issue_titles.get(issue_id, "")
            if title:
                issue_part = f"{issue_id} ({title})"
            req_part = describe_requirement(req_id, req_descriptions) if req_id else ""
            lines.append(f"- {issue_part}: {req_part}" if req_part else f"- {issue_part}")
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Likely Abstraction-Level Mismatches",
    ])

    if abstraction_mismatches:
        lines.extend([f"- {item}" for item in abstraction_mismatches])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Suggested Remediation Order",
        "1. Resolve missing requirement-documentation IDs in a dedicated requirements commit.",
        "2. Validate each requirement at the same abstraction level it is written (system/project, capability/function, interface, component, or UI); rewrite or split requirement text when verification cannot be stated at that same level.",
        "3. Create missing function hierarchy entries in docs/architecture/Function_Hierarchy_Registry.md grouped by parent capability.",
        "4. Add or update Requirements/15 registry rows for missing issue/requirement links with architecture/design/implementation/verification references.",
        "5. Add explicit test evidence references for remaining issue files in a separate evidence commit.",
        "6. Re-run sprint traceability validation and capture post-remediation output.",
        "",
        "## Raw Verification Output (Tail)",
    ])

    tail = output_lines[-80:] if len(output_lines) > 80 else output_lines
    if tail:
        lines.extend([f"- {line}" for line in tail])
    else:
        lines.append("- no output")

    (out_root / "traceability_blocker_backlog_latest.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a blocker backlog from sprint traceability validation output")
    parser.add_argument("--sprint", type=str, required=True, help="Sprint identifier (YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN)")
    parser.add_argument("--out-dir", type=str, default="independent_reviews/latest", help="Output directory")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    verify_script = repo_root / "scripts" / "verify_sprint_traceability.py"

    proc = subprocess.run(
        [sys.executable, str(verify_script), "--sprint", args.sprint],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=False,
    )

    merged = []
    if proc.stdout:
        merged.extend(proc.stdout.splitlines())
    if proc.stderr:
        merged.extend(proc.stderr.splitlines())

    summary = summarize(merged)
    issue_test_evidence = parse_issue_test_evidence(merged)
    registry_path = repo_root / "Requirements" / "15_End_To_End_Traceability_Attributes_Registry.md"
    function_registry_path = repo_root / "docs" / "architecture" / "Function_Hierarchy_Registry.md"
    registry_rows = parse_registry_rows(registry_path, args.sprint)
    function_requirement_map = parse_function_requirement_map(function_registry_path)
    abstraction_mismatches = detect_abstraction_mismatches(
        registry_rows,
        function_requirement_map,
        issue_test_evidence,
    )

    write_outputs(repo_root, args.out_dir, args.sprint, proc.returncode, merged, summary, abstraction_mismatches)

    print("Traceability blocker backlog generated:")
    print(f"- Sprint: {args.sprint}")
    print(f"- Missing requirement docs: {len(summary['missing_requirement_docs'])}")
    print(f"- Missing explicit test evidence: {len(summary['missing_test_evidence'])}")
    print(f"- Missing function root links: {len(summary['missing_function_root_links'])}")
    print(f"- Missing registry links: {len(summary['missing_registry_links'])}")
    print(f"- Likely abstraction-level mismatches: {len(abstraction_mismatches)}")
    print(f"- Source verifier exit code: {proc.returncode}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

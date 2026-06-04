import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


REQ_ID_RE = re.compile(r"\b[A-Z]+-\d+[A-Z]?\b")
MISSING_TEST_RE = re.compile(r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+is missing explicit test evidence", re.IGNORECASE)
MISSING_REGISTRY_LINK_RE = re.compile(
    r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+requirement\s+([A-Z]+-\d+[A-Z]?)\s+has no aligned row in\s+Requirements/15_End_To_End_Traceability_Attributes_Registry\.md",
    re.IGNORECASE,
)


def is_requirement_id(token: str) -> bool:
    upper = token.upper()
    if re.fullmatch(r"S\d{2,3}-\d+", upper):
        return False
    if re.fullmatch(r"D-S\d{2,3}-\d{3}", upper):
        return False
    return "-" in upper


def load_blocker_backlog(repo_root: Path, out_dir: str, sprint: str) -> Dict[str, object]:
    path = repo_root / out_dir / "traceability_blocker_backlog_latest.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if str(payload.get("sprint", "")).replace("-", "_") != sprint.replace("-", "_"):
        return {}
    return payload


def issue_id_pattern_for_filename(issue_id: str) -> re.Pattern[str]:
    token = issue_id.replace("-", "[_-]")
    return re.compile(rf"_{token}(?:_|\.)", re.IGNORECASE)


def sprint_tokens(sprint: str) -> tuple[str, str]:
    return sprint.replace("_", "-"), sprint.replace("-", "_")


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
            ids = [rid for rid in re.findall(r"\b[A-Z][A-Z0-9]+-\d+[A-Z]?\b", line) if is_requirement_id(rid)]
            if not ids:
                continue
            stripped = line.strip()
            if stripped.startswith("|") and stripped.endswith("|"):
                cells = split_markdown_row(stripped)
                for rid in ids:
                    if rid in cells:
                        idx = cells.index(rid)
                        if idx + 1 < len(cells):
                            desc = cells[idx + 1].strip(" :-")
                            if desc and len(desc) > 10:
                                descriptions[rid] = desc
            else:
                if "shall" not in stripped.lower():
                    continue
                for rid in ids:
                    if rid in descriptions:
                        continue
                    desc = re.sub(rf"\b{re.escape(rid)}\b", "", stripped).strip(" :-")
                    if len(desc) > 10:
                        descriptions[rid] = desc
    return descriptions


def build_issue_titles(repo_root: Path, sprint: str) -> Dict[str, str]:
    titles: Dict[str, str] = {}
    _, sprint_us = sprint_tokens(sprint)
    issue_dir = repo_root / "planning" / "issues"
    if not issue_dir.exists():
        return titles
    for path in sorted(issue_dir.glob(f"issue_{sprint_us}_*.md")):
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


def backlog_requirement_scope(repo_root: Path, sprint: str, backlog_payload: Dict[str, object]) -> Dict[str, object]:
    registry_reqs: set[str] = set()
    missing_test_issues: List[str] = []

    missing_registry_links = backlog_payload.get("missing_registry_links", [])
    if isinstance(missing_registry_links, list):
        for item in missing_registry_links:
            parts = str(item).split(":", 1)
            if len(parts) == 2 and is_requirement_id(parts[1].strip()):
                registry_reqs.add(parts[1].strip())

    missing_test_raw = backlog_payload.get("missing_test_evidence", [])
    if isinstance(missing_test_raw, list):
        missing_test_issues = [str(v).strip() for v in missing_test_raw if str(v).strip()]

    issue_req_map: Dict[str, List[str]] = {}
    _, sprint_us = sprint_tokens(sprint)
    issues_dir = repo_root / "planning" / "issues"
    if issues_dir.exists() and missing_test_issues:
        issue_files = sorted(issues_dir.glob(f"issue_{sprint_us}_*.md"))
        for issue_id in missing_test_issues:
            pattern = issue_id_pattern_for_filename(issue_id)
            matched = next((path for path in issue_files if pattern.search(path.name)), None)
            if matched is None:
                continue
            text = matched.read_text(encoding="utf-8", errors="ignore")
            reqs = sorted({rid for rid in REQ_ID_RE.findall(text) if is_requirement_id(rid)})
            if reqs:
                issue_req_map[issue_id] = reqs

    test_reqs: set[str] = set()
    for reqs in issue_req_map.values():
        test_reqs.update(reqs)

    all_reqs = sorted(registry_reqs | test_reqs)
    return {
        "requirement_ids": all_reqs,
        "registry_link_requirements": sorted(registry_reqs),
        "missing_test_issues": missing_test_issues,
        "issue_requirement_map": issue_req_map,
    }


def live_verifier_requirement_scope(repo_root: Path, sprint: str) -> Dict[str, object]:
    verify_script = repo_root / "scripts" / "verify_sprint_traceability.py"
    proc = subprocess.run(
        [sys.executable, str(verify_script), "--sprint", sprint],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=False,
    )
    lines: List[str] = []
    if proc.stdout:
        lines.extend(proc.stdout.splitlines())
    if proc.stderr:
        lines.extend(proc.stderr.splitlines())

    registry_reqs: set[str] = set()
    missing_test_issues: List[str] = []
    for line in lines:
        registry_match = MISSING_REGISTRY_LINK_RE.search(line)
        if registry_match:
            req_id = registry_match.group(2).strip()
            if is_requirement_id(req_id):
                registry_reqs.add(req_id)
        test_match = MISSING_TEST_RE.search(line)
        if test_match:
            missing_test_issues.append(test_match.group(1).strip())

    issue_req_map: Dict[str, List[str]] = {}
    _, sprint_us = sprint_tokens(sprint)
    issues_dir = repo_root / "planning" / "issues"
    if issues_dir.exists() and missing_test_issues:
        issue_files = sorted(issues_dir.glob(f"issue_{sprint_us}_*.md"))
        for issue_id in missing_test_issues:
            pattern = issue_id_pattern_for_filename(issue_id)
            matched = next((path for path in issue_files if pattern.search(path.name)), None)
            if matched is None:
                continue
            text = matched.read_text(encoding="utf-8", errors="ignore")
            reqs = sorted({rid for rid in REQ_ID_RE.findall(text) if is_requirement_id(rid)})
            if reqs:
                issue_req_map[issue_id] = reqs

    test_reqs: set[str] = set()
    for reqs in issue_req_map.values():
        test_reqs.update(reqs)

    return {
        "requirement_ids": sorted(registry_reqs | test_reqs),
        "registry_link_requirements": sorted(registry_reqs),
        "missing_test_issues": sorted(set(missing_test_issues)),
        "issue_requirement_map": issue_req_map,
        "verifier_exit_code": proc.returncode,
    }


def find_remediation_plan(repo_root: Path, sprint: str, explicit_path: str) -> Path:
    if explicit_path:
        candidate = repo_root / explicit_path
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"Remediation plan not found: {candidate.as_posix()}")

    patterns = [
        f"planning/issues/issue_{sprint}_*.md",
        f"planning/issues/issue_{sprint.replace('_', '-')}_*.md",
        f"planning/issues/issue_{sprint.replace('-', '_')}_*.md",
        "planning/Sprint_Remediation_Issue_*.md",
        f"planning/Sprint_{sprint}_Remediation_*.md",
    ]
    for pattern in patterns:
        candidates = sorted(
            repo_root.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for candidate in candidates:
            text = candidate.read_text(encoding="utf-8", errors="ignore")
            if "## Remediation Targets" in text:
                return candidate
        if candidates:
            return candidates[0]

    joined_patterns = ", ".join(patterns)
    raise FileNotFoundError(f"No remediation plan matches: {joined_patterns}")


def parse_evidence_targets(lines: List[str]) -> List[str]:
    targets: List[str] = []
    capture = False
    for line in lines:
        stripped = line.strip()
        if stripped in {"## Evidence Targets", "## Remediation Targets"}:
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture and stripped.startswith("- "):
            targets.append(stripped[2:].strip())
    return targets


def build_workpack(repo_root: Path, plan_path: Path, sprint: str, out_dir: str) -> Dict[str, object]:
    lines = plan_path.read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines)
    plan_requirement_ids = sorted({rid for rid in REQ_ID_RE.findall(text) if is_requirement_id(rid)})
    targets = parse_evidence_targets(lines)

    backlog_payload = load_blocker_backlog(repo_root, out_dir, sprint)
    backlog_scope = backlog_requirement_scope(repo_root, sprint, backlog_payload) if backlog_payload else {
        "requirement_ids": [],
        "registry_link_requirements": [],
        "missing_test_issues": [],
        "issue_requirement_map": {},
    }
    live_scope = live_verifier_requirement_scope(repo_root, sprint)
    live_requirement_ids = live_scope.get("requirement_ids", []) if isinstance(live_scope, dict) else []
    backlog_requirement_ids = backlog_scope.get("requirement_ids", []) if isinstance(backlog_scope, dict) else []
    effective_requirement_ids = live_requirement_ids if live_requirement_ids else backlog_requirement_ids
    requirement_ids = sorted(set(plan_requirement_ids) | set(effective_requirement_ids))

    architecture_targets = sorted([t for t in targets if t.startswith("docs/architecture/") or t.startswith("docs/design/")])
    implementation_targets = sorted([t for t in targets if t.startswith("src/") or t.startswith("frontend/src/") or t.startswith("scripts/")])
    verification_targets = sorted([t for t in targets if t.startswith("Tests/") or t.startswith("test_reports/")])

    gaps: List[str] = []
    if implementation_targets and not architecture_targets:
        gaps.append("Implementation evidence exists without architecture/design targets.")
    if requirement_ids and not architecture_targets:
        gaps.append("Requirement IDs are present but architecture/design references are missing from evidence targets.")
    if implementation_targets and not verification_targets:
        gaps.append("Implementation targets are listed without verification targets.")

    if effective_requirement_ids and set(plan_requirement_ids).isdisjoint(set(effective_requirement_ids)):
        gaps.append(
            "Remediation plan requirement scope does not intersect verifier-driven blocker scope. "
            "Workpack was expanded using verifier-derived requirements."
        )

    if requirement_ids and architecture_targets:
        missing_requirement_evidence: Dict[str, List[str]] = {}
        for req_id in requirement_ids:
            evidence_hits: List[str] = []
            for rel in architecture_targets:
                target = repo_root / rel
                if not target.exists():
                    continue
                text = target.read_text(encoding="utf-8", errors="ignore")
                if req_id in text:
                    evidence_hits.append(rel)
            if not evidence_hits:
                missing_requirement_evidence[req_id] = []

        if missing_requirement_evidence:
            for req_id in sorted(missing_requirement_evidence):
                gaps.append(
                    f"Requirement {req_id} is not found in architecture/design authority targets listed by remediation plan."
                )

    return {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": sprint,
        "plan_path": plan_path.as_posix(),
        "live_verifier_exit_code": live_scope.get("verifier_exit_code", None),
        "plan_requirement_ids": plan_requirement_ids,
        "backlog_requirement_ids": effective_requirement_ids,
        "backlog_registry_link_requirements": (live_scope.get("registry_link_requirements") or backlog_scope.get("registry_link_requirements", [])),
        "backlog_missing_test_issues": (live_scope.get("missing_test_issues") or backlog_scope.get("missing_test_issues", [])),
        "backlog_issue_requirement_map": (live_scope.get("issue_requirement_map") or backlog_scope.get("issue_requirement_map", {})),
        "requirement_ids": requirement_ids,
        "architecture_targets": architecture_targets,
        "implementation_targets": implementation_targets,
        "verification_targets": verification_targets,
        "gaps": gaps,
    }


def write_outputs(repo_root: Path, out_dir: str, workpack: Dict[str, object]) -> None:
    out_root = repo_root / out_dir
    out_root.mkdir(parents=True, exist_ok=True)

    json_path = out_root / "architecture_design_authoring_workpack_latest.json"
    md_path = out_root / "architecture_design_authoring_workpack_latest.md"
    req_descriptions = build_requirement_descriptions(repo_root)
    issue_titles = build_issue_titles(repo_root, str(workpack.get("sprint", "")))

    json_path.write_text(json.dumps(workpack, indent=2), encoding="utf-8")

    lines: List[str] = [
        "# Architecture/Design Authoring Workpack (Latest)",
        "",
        f"- Timestamp: {workpack['timestamp']}",
        f"- Sprint: {workpack.get('sprint', '')}",
        f"- Remediation Plan: {workpack['plan_path']}",
        "",
        "## Requirement Scope",
    ]

    req_ids = workpack["requirement_ids"]
    if req_ids:
        for item in req_ids:
            desc = req_descriptions.get(item, "")
            lines.append(f"- {item}: {desc}" if desc else f"- {item}")
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Scope Sources",
        f"- Plan requirement IDs: {len(workpack.get('plan_requirement_ids', []))}",
        f"- Backlog requirement IDs: {len(workpack.get('backlog_requirement_ids', []))}",
        f"- Backlog missing-test issues: {len(workpack.get('backlog_missing_test_issues', []))}",
    ])

    if workpack.get("backlog_missing_test_issues"):
        lines.append("- Missing-test issue IDs:")
        for item in workpack.get("backlog_missing_test_issues", []):
            title = issue_titles.get(str(item), "")
            lines.append(f"  - {item}: {title}" if title else f"  - {item}")

    lines.extend([
        "",
        "## Architecture/Design Targets",
    ])

    arch_targets = workpack["architecture_targets"]
    if arch_targets:
        lines.extend([f"- {item}" for item in arch_targets])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Implementation Targets",
    ])

    impl_targets = workpack["implementation_targets"]
    if impl_targets:
        lines.extend([f"- {item}" for item in impl_targets])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Verification Targets",
    ])

    verify_targets = workpack["verification_targets"]
    if verify_targets:
        lines.extend([f"- {item}" for item in verify_targets])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Disposition Decision Template",
        "- Decision required: update architecture/design to match implementation OR change implementation to match architecture/design.",
        "- Selected path:",
        "- Decision rationale:",
        "- Approval reference:",
        "- Verification rerun evidence path:",
        "",
        "## Detected Gaps",
    ])

    gaps = workpack["gaps"]
    if gaps:
        lines.extend([f"- {item}" for item in gaps])
    else:
        lines.append("- none")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate architecture/design authoring workpack for remediation execution")
    parser.add_argument("--sprint", type=str, default="2026_12", help="Sprint identifier (YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN)")
    parser.add_argument("--out-dir", type=str, default="independent_reviews/latest", help="Output directory")
    parser.add_argument(
        "--remediation-plan",
        type=str,
        default="",
        help="Optional workspace-relative path to a remediation sprint markdown file",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Return non-zero when workpack gaps are detected",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    plan_path = find_remediation_plan(repo_root, args.sprint, args.remediation_plan)
    workpack = build_workpack(repo_root, plan_path, args.sprint, args.out_dir)
    write_outputs(repo_root, args.out_dir, workpack)

    print("Architecture/design authoring workpack generated:")
    print(f"- Plan: {plan_path.as_posix()}")
    print(f"- Requirement IDs: {len(workpack['requirement_ids'])}")
    print(f"- Architecture/design targets: {len(workpack['architecture_targets'])}")
    print(f"- Implementation targets: {len(workpack['implementation_targets'])}")
    print(f"- Verification targets: {len(workpack['verification_targets'])}")
    print(f"- Gaps: {len(workpack['gaps'])}")
    if args.enforce and workpack["gaps"]:
        print("Architecture/design authoring workpack enforcement failed due to detected gaps.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

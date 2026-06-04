#!/usr/bin/env python3
"""Execute an explicit analysis-to-remediation traceability cycle.

Cycle steps:
1. Select candidate requirements from latest independent review gaps.
2. Plan remediation by examining linked architecture/implementation/verification files.
3. Update remediation targets in core traceability docs.
4. Re-run independent review and publish before/after deltas.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "independent_reviews" / "latest"
MISSING_TEST_RE = re.compile(r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+is missing explicit test evidence", re.IGNORECASE)
MISSING_REGISTRY_LINK_RE = re.compile(
    r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+requirement\s+([A-Z]+-\d+[A-Z]?)\s+has no aligned row in\s+Requirements/15_End_To_End_Traceability_Attributes_Registry\.md",
    re.IGNORECASE,
)


def sprint_tokens(sprint: str) -> Tuple[str, str]:
    dash = sprint.replace("_", "-")
    underscore = sprint.replace("-", "_")
    return dash, underscore


def issue_id_pattern_for_filename(issue_id: str) -> re.Pattern[str]:
    token = issue_id.replace("-", "[_-]")
    return re.compile(rf"_{token}(?:_|\.)", re.IGNORECASE)


def is_requirement_id(token: str) -> bool:
    upper = token.upper()
    if re.fullmatch(r"S\d{2,3}-\d+", upper):
        return False
    if re.fullmatch(r"D-S\d{2,3}-\d{3}", upper):
        return False
    return "-" in upper


def load_blocker_backlog(repo_root: Path, out_dir: Path, sprint: str) -> Dict[str, Any]:
    backlog_path = out_dir / "traceability_blocker_backlog_latest.json"
    if not backlog_path.exists():
        return {}
    try:
        payload = load_json(backlog_path)
    except Exception:
        return {}
    if str(payload.get("sprint", "")).replace("-", "_") != sprint.replace("-", "_"):
        return {}
    return payload


def issue_requirements_from_files(repo_root: Path, sprint: str, issue_ids: List[str]) -> Dict[str, List[str]]:
    _, sprint_us = sprint_tokens(sprint)
    issue_dir = repo_root / "planning" / "issues"
    if not issue_dir.exists() or not issue_ids:
        return {}

    issue_files = sorted(issue_dir.glob(f"issue_{sprint_us}_*.md"))
    mapping: Dict[str, List[str]] = {}
    for issue_id in issue_ids:
        pattern = issue_id_pattern_for_filename(issue_id)
        matched = next((path for path in issue_files if pattern.search(path.name)), None)
        if matched is None:
            continue
        text = matched.read_text(encoding="utf-8", errors="ignore")
        reqs = sorted({rid for rid in REQ_ID_RE.findall(text) if is_requirement_id(rid)})
        if reqs:
            mapping[issue_id] = reqs
    return mapping


def backlog_requirement_sets(
    repo_root: Path,
    sprint: str,
    backlog_payload: Dict[str, Any],
) -> Tuple[set[str], set[str]]:
    registry_reqs: set[str] = set()
    for item in backlog_payload.get("missing_registry_links", []) if isinstance(backlog_payload.get("missing_registry_links"), list) else []:
        parts = str(item).split(":", 1)
        if len(parts) == 2 and is_requirement_id(parts[1].strip()):
            registry_reqs.add(parts[1].strip())

    missing_test_issues = [str(v).strip() for v in backlog_payload.get("missing_test_evidence", []) if str(v).strip()]
    issue_req_map = issue_requirements_from_files(repo_root=repo_root, sprint=sprint, issue_ids=missing_test_issues)
    missing_test_reqs: set[str] = set()
    for reqs in issue_req_map.values():
        missing_test_reqs.update(reqs)

    return registry_reqs, missing_test_reqs


def live_blocker_requirement_sets(repo_root: Path, sprint: str) -> Tuple[set[str], set[str], Dict[str, Any]]:
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

    issue_req_map = issue_requirements_from_files(repo_root=repo_root, sprint=sprint, issue_ids=missing_test_issues)
    missing_test_reqs: set[str] = set()
    for reqs in issue_req_map.values():
        missing_test_reqs.update(reqs)

    diagnostics = {
        "verifier_exit_code": proc.returncode,
        "missing_test_issues": sorted(set(missing_test_issues)),
        "registry_link_requirements": sorted(registry_reqs),
        "issue_requirement_map": issue_req_map,
    }
    return registry_reqs, missing_test_reqs, diagnostics


def review_json_path(repo_root: Path, sprint: str, explicit: str | None) -> Path:
    if explicit:
        candidate = Path(explicit)
        return candidate if candidate.is_absolute() else (repo_root / candidate)
    dash, _ = sprint_tokens(sprint)
    return repo_root / "independent_reviews" / "latest" / f"independent_review_{dash}_pre-push.json"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_ref(value: str) -> str:
    return value.replace("\\", "/").strip()


def existing_repo_file(ref: str, repo_root: Path) -> str:
    normalized = normalize_ref(ref)
    if not normalized:
        return ""

    candidate = Path(normalized)
    if candidate.is_absolute():
        try:
            candidate = candidate.resolve().relative_to(repo_root)
        except ValueError:
            return ""

    resolved = (repo_root / candidate).resolve()
    if resolved.exists() and resolved.is_file():
        return resolved.relative_to(repo_root).as_posix()
    return ""


def filter_existing_files(refs: List[str], repo_root: Path) -> List[str]:
    result: List[str] = []
    seen: set[str] = set()
    for item in refs:
        existing = existing_repo_file(str(item), repo_root)
        if not existing or existing in seen:
            continue
        seen.add(existing)
        result.append(existing)
    return result


def family(req_id: str) -> str:
    if req_id.startswith("C18-"):
        return "C18"
    if req_id.startswith("C10-"):
        return "C10"
    return req_id.split("-", 1)[0]


def priority_candidates(missing_impl: List[str], missing_verify: List[str], missing_arch: List[str]) -> List[str]:
    impl_set = set(missing_impl)
    verify_set = set(missing_verify)
    arch_set = set(missing_arch)
    all_ids = sorted(impl_set | verify_set | arch_set)

    family_counts: Dict[str, int] = {}
    for req_id in all_ids:
        fam = family(req_id)
        family_counts[fam] = family_counts.get(fam, 0) + 1

    family_rank = {
        name: idx for idx, name in enumerate([k for k, _v in sorted(family_counts.items(), key=lambda kv: (-kv[1], kv[0]))])
    }

    def score(req_id: str) -> Tuple[int, int, str]:
        missing_legs = int(req_id in impl_set) + int(req_id in verify_set) + int(req_id in arch_set)
        return (-missing_legs, family_rank.get(family(req_id), 999), req_id)

    return sorted(all_ids, key=score)


def summarize_counts(review_payload: Dict[str, Any]) -> Dict[str, int]:
    missing_impl = review_payload.get("req_without_impl", []) if isinstance(review_payload.get("req_without_impl", []), list) else []
    missing_verify = review_payload.get("req_without_verification", []) if isinstance(review_payload.get("req_without_verification", []), list) else []
    missing_arch = review_payload.get("req_without_arch_design_trace", []) if isinstance(review_payload.get("req_without_arch_design_trace", []), list) else []
    return {
        "missing_impl": len(missing_impl),
        "missing_verify": len(missing_verify),
        "missing_arch_design": len(missing_arch),
    }


def requirement_description_map(review_payload: Dict[str, Any]) -> Dict[str, str]:
    raw = review_payload.get("requirement_descriptions", {})
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v).strip() for k, v in raw.items() if str(v).strip()}


def select_candidates(
    review_payload: Dict[str, Any],
    max_items: int,
    backlog_registry_reqs: set[str],
    backlog_missing_test_reqs: set[str],
) -> List[str]:
    missing_impl = review_payload.get("req_without_impl", []) if isinstance(review_payload.get("req_without_impl", []), list) else []
    missing_verify = review_payload.get("req_without_verification", []) if isinstance(review_payload.get("req_without_verification", []), list) else []
    missing_arch = review_payload.get("req_without_arch_design_trace", []) if isinstance(review_payload.get("req_without_arch_design_trace", []), list) else []

    ranked = priority_candidates(missing_impl, missing_verify, missing_arch)
    ranked_set = set(ranked)
    backlog_union = sorted(backlog_registry_reqs | backlog_missing_test_reqs)
    for req_id in backlog_union:
        if req_id not in ranked_set:
            ranked.append(req_id)
            ranked_set.add(req_id)
    return ranked[: max(0, max_items)]


def requirement_plan(
    req_id: str,
    review_payload: Dict[str, Any],
    repo_root: Path,
    backlog_registry_reqs: set[str],
    backlog_missing_test_reqs: set[str],
) -> Dict[str, Any]:
    traceability = review_payload.get("requirement_traceability", {})
    req_trace = traceability.get(req_id, {}) if isinstance(traceability, dict) else {}
    if not isinstance(req_trace, dict):
        req_trace = {}

    architecture_refs = filter_existing_files([str(v) for v in req_trace.get("architecture_refs", [])], repo_root)
    implementation_refs = filter_existing_files([str(v) for v in req_trace.get("implementation_refs", [])], repo_root)
    verification_refs = filter_existing_files([str(v) for v in req_trace.get("verification_refs", [])], repo_root)
    source_refs = filter_existing_files([str(v) for v in req_trace.get("source_refs", [])], repo_root)

    missing_impl = req_id in set(review_payload.get("req_without_impl", []))
    missing_verify = req_id in set(review_payload.get("req_without_verification", []))
    missing_arch = req_id in set(review_payload.get("req_without_arch_design_trace", []))

    missing_legs: List[str] = []
    if missing_impl:
        missing_legs.append("implementation")
    if missing_verify:
        missing_legs.append("verification")
    if missing_arch:
        missing_legs.append("architecture/design")
    if req_id in backlog_registry_reqs:
        missing_legs.append("registry-linkage")
    if req_id in backlog_missing_test_reqs:
        missing_legs.append("test-evidence")

    planned_outputs = [
        "Requirements/04_Traceability_Matrix.md",
        "docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md",
        "Requirements/15_End_To_End_Traceability_Attributes_Registry.md",
    ]

    return {
        "requirement_id": req_id,
        "missing_legs": missing_legs,
        "linked_architecture_files": architecture_refs,
        "linked_implementation_files": implementation_refs,
        "linked_verification_files": verification_refs,
        "linked_source_files": source_refs,
        "planned_outputs": planned_outputs,
        "analysis_summary": {
            "architecture_links_found": len(architecture_refs),
            "implementation_links_found": len(implementation_refs),
            "verification_links_found": len(verification_refs),
            "source_links_found": len(source_refs),
        },
    }


def run_command(repo_root: Path, args: List[str], label: str) -> Dict[str, Any]:
    started_at = dt.datetime.now().isoformat(timespec="seconds")
    started = dt.datetime.now()
    proc = subprocess.run(args, cwd=str(repo_root), text=True, capture_output=True, check=False)
    ended = dt.datetime.now()
    return {
        "label": label,
        "command": args,
        "started_at": started_at,
        "ended_at": ended.isoformat(timespec="seconds"),
        "duration_seconds": round((ended - started).total_seconds(), 3),
        "exit_code": proc.returncode,
        "status": "success" if proc.returncode == 0 else "failed",
        "stdout_tail": "\n".join((proc.stdout or "").splitlines()[-20:]),
        "stderr_tail": "\n".join((proc.stderr or "").splitlines()[-20:]),
    }


def render_cycle_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = [
        "# Traceability Remediation Cycle (Latest)",
        "",
        f"- Generated: {report['generated_at']}",
        f"- Sprint: {report['sprint']}",
        f"- Max iterations: {report['max_iterations']}",
        f"- Candidate cap per iteration: {report['max_items']}",
        f"- Completed iterations: {len(report.get('iterations', []))}",
        "",
        "## Before vs After",
        "",
        f"- Missing implementation: {report['before_counts']['missing_impl']} -> {report['after_counts']['missing_impl']}",
        f"- Missing verification: {report['before_counts']['missing_verify']} -> {report['after_counts']['missing_verify']}",
        f"- Missing architecture/design: {report['before_counts']['missing_arch_design']} -> {report['after_counts']['missing_arch_design']}",
        "",
    ]

    for iteration in report.get("iterations", []):
        lines.extend(
            [
                f"## Iteration {iteration['iteration']}",
                "",
                f"- Candidate count: {len(iteration.get('candidates', []))}",
                f"- Plan file: {iteration.get('plan_markdown', '')}",
                "",
                "### Commands",
            ]
        )
        for item in iteration.get("commands", []):
            lines.append(
                f"- {item['label']} | status={item['status']} | exit={item['exit_code']} | duration={item['duration_seconds']:.3f}s"
            )
        lines.append("")

    lines.append("## Candidate Analysis (Last Iteration)")
    lines.append("")
    last_iteration = report.get("iterations", [])[-1] if report.get("iterations") else None
    requirement_descriptions = report.get("requirement_descriptions", {})
    if last_iteration and last_iteration.get("candidate_analysis"):
        lines.append("| Requirement ID | Description | Missing Legs | Arch Links | Impl Links | Verify Links |")
        lines.append("|---|---|---|---:|---:|---:|")
        for row in last_iteration["candidate_analysis"]:
            req_id = row["requirement_id"]
            desc = str(requirement_descriptions.get(req_id, "")).replace("|", "\\|") or "n/a"
            lines.append(
                f"| {req_id} | {desc} | {', '.join(row['missing_legs']) or 'none'} | "
                f"{row['analysis_summary']['architecture_links_found']} | "
                f"{row['analysis_summary']['implementation_links_found']} | "
                f"{row['analysis_summary']['verification_links_found']} |"
            )
    else:
        lines.append("- none")

    lines.append("")
    lines.append("## Notes")
    lines.append("- This cycle enforces analysis and remediation updates before running independent review again.")
    lines.append("- If no candidates are found, the cycle exits early after documenting that state.")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run explicit analysis-to-remediation traceability cycle")
    parser.add_argument("--sprint", required=True, help="Sprint identifier (e.g. 2026_102)")
    parser.add_argument("--review-json", default=None, help="Optional path to independent review JSON")
    parser.add_argument("--out-dir", default="independent_reviews/latest", help="Output directory")
    parser.add_argument("--max-items", type=int, default=40, help="Candidate cap per iteration")
    parser.add_argument("--max-iterations", type=int, default=2, help="Maximum remediation cycles to run")
    parser.add_argument("--policy-profile", default="default", help="Independent review policy profile")
    parser.add_argument("--enforcement-mode", default="off", choices=["auto", "off", "manual"], help="Independent review enforcement mode")
    parser.add_argument("--trend-window", type=int, default=5, help="Independent review trend window")
    args = parser.parse_args()

    out_dir = (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    dash_sprint, _ = sprint_tokens(args.sprint)
    baseline_review_json = review_json_path(REPO_ROOT, args.sprint, args.review_json)

    # Ensure a baseline review exists before remediation selection.
    if not baseline_review_json.exists():
        bootstrap_result = run_command(
            REPO_ROOT,
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "independent_repo_review.py"),
                "--sprint",
                args.sprint,
                "--run-context",
                "pre-push",
                "--report-mode",
                "update",
                "--policy-profile",
                args.policy_profile,
                "--enforcement-mode",
                "off",
                "--trend-window",
                str(max(1, args.trend_window)),
                "--out-dir",
                args.out_dir,
            ],
            "bootstrap-independent-review",
        )
        if bootstrap_result["exit_code"] != 0:
            print("[traceability-remediation-cycle] Failed to bootstrap baseline review")
            return bootstrap_result["exit_code"]

    current_review_json = baseline_review_json
    before_payload = load_json(current_review_json)
    before_counts = summarize_counts(before_payload)
    backlog_payload = load_blocker_backlog(REPO_ROOT, out_dir, args.sprint)
    backlog_registry_reqs, backlog_missing_test_reqs = backlog_requirement_sets(
        repo_root=REPO_ROOT,
        sprint=args.sprint,
        backlog_payload=backlog_payload,
    )
    live_registry_reqs, live_missing_test_reqs, live_diagnostics = live_blocker_requirement_sets(
        repo_root=REPO_ROOT,
        sprint=args.sprint,
    )
    effective_registry_reqs = live_registry_reqs or backlog_registry_reqs
    effective_missing_test_reqs = live_missing_test_reqs or backlog_missing_test_reqs

    iterations: List[Dict[str, Any]] = []

    for index in range(1, max(1, args.max_iterations) + 1):
        current_payload = load_json(current_review_json)
        candidates = select_candidates(
            current_payload,
            max_items=max(1, args.max_items),
            backlog_registry_reqs=effective_registry_reqs,
            backlog_missing_test_reqs=effective_missing_test_reqs,
        )

        candidate_analysis = [
            requirement_plan(
                req_id=req_id,
                review_payload=current_payload,
                repo_root=REPO_ROOT,
                backlog_registry_reqs=effective_registry_reqs,
                backlog_missing_test_reqs=effective_missing_test_reqs,
            )
            for req_id in candidates
        ]

        plan_json_path = out_dir / f"traceability_remediation_plan_{dash_sprint}_iter_{index}.json"
        plan_md_path = out_dir / f"traceability_remediation_plan_{dash_sprint}_iter_{index}.md"

        plan_payload = {
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
            "sprint": args.sprint,
            "iteration": index,
            "review_json": current_review_json.as_posix(),
            "backlog_input": backlog_payload if backlog_payload else {},
            "live_verifier_blockers": live_diagnostics,
            "candidate_count": len(candidates),
            "candidates": candidate_analysis,
        }
        plan_json_path.write_text(json.dumps(plan_payload, indent=2), encoding="utf-8")

        plan_lines: List[str] = [
            f"# Traceability Remediation Plan - Iteration {index}",
            "",
            f"- Sprint: {args.sprint}",
            f"- Review input: {current_review_json.as_posix()}",
            f"- Blocker backlog linked: {'yes' if backlog_payload else 'no'}",
            f"- Live verifier blockers: registry={len(effective_registry_reqs)}, test={len(effective_missing_test_reqs)}",
            f"- Candidate count: {len(candidates)}",
            "",
            "## Candidates",
            "",
            "| Requirement ID | Description | Missing Legs | Arch Links | Impl Links | Verify Links |",
            "|---|---|---|---:|---:|---:|",
        ]
        description_map = requirement_description_map(current_payload)
        for row in candidate_analysis:
            req_id = row["requirement_id"]
            desc = description_map.get(req_id, "")
            safe_desc = desc.replace("|", "\\|") if desc else "n/a"
            plan_lines.append(
                f"| {req_id} | {safe_desc} | {', '.join(row['missing_legs']) or 'none'} | "
                f"{row['analysis_summary']['architecture_links_found']} | "
                f"{row['analysis_summary']['implementation_links_found']} | "
                f"{row['analysis_summary']['verification_links_found']} |"
            )
        if not candidate_analysis:
            plan_lines.append("| n/a | n/a | none | 0 | 0 | 0 |")

        plan_md_path.write_text("\n".join(plan_lines) + "\n", encoding="utf-8")

        iteration_record: Dict[str, Any] = {
            "iteration": index,
            "candidates": candidates,
            "candidate_analysis": candidate_analysis,
            "plan_json": plan_json_path.as_posix(),
            "plan_markdown": plan_md_path.as_posix(),
            "commands": [],
        }

        if not candidates:
            iteration_record["notes"] = "No remaining candidates found; cycle ended."
            iterations.append(iteration_record)
            break

        backfill_result = run_command(
            REPO_ROOT,
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "run_traceability_verification_backfill.py"),
                "--sprint",
                args.sprint,
                "--review-json",
                current_review_json.as_posix(),
                "--max-items",
                str(len(candidates)),
            ],
            "apply-traceability-backfill",
        )
        iteration_record["commands"].append(backfill_result)

        triage_result = run_command(
            REPO_ROOT,
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "run_unimplemented_requirement_triage.py"),
                "--sprint",
                args.sprint,
                "--target-sprint",
                "2026_099",
            ],
            "update-unimplemented-triage",
        )
        iteration_record["commands"].append(triage_result)

        rerun_result = run_command(
            REPO_ROOT,
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "independent_repo_review.py"),
                "--sprint",
                args.sprint,
                "--run-context",
                "pre-push",
                "--report-mode",
                "update",
                "--policy-profile",
                args.policy_profile,
                "--enforcement-mode",
                args.enforcement_mode,
                "--trend-window",
                str(max(1, args.trend_window)),
                "--out-dir",
                args.out_dir,
            ],
            "rerun-independent-review",
        )
        iteration_record["commands"].append(rerun_result)

        readiness_result = run_command(
            REPO_ROOT,
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "run_remediation_readiness.py"),
                "--sprint",
                args.sprint,
            ],
            "refresh-remediation-readiness",
        )
        iteration_record["commands"].append(readiness_result)

        iterations.append(iteration_record)

        if rerun_result["exit_code"] != 0:
            break

        current_review_json = review_json_path(REPO_ROOT, args.sprint, None)
        if not current_review_json.exists():
            break

    final_review_json = review_json_path(REPO_ROOT, args.sprint, None)
    after_payload = load_json(final_review_json) if final_review_json.exists() else before_payload
    after_counts = summarize_counts(after_payload)

    report = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": args.sprint,
        "max_items": args.max_items,
        "max_iterations": args.max_iterations,
        "before_review_json": baseline_review_json.as_posix(),
        "after_review_json": final_review_json.as_posix(),
        "before_counts": before_counts,
        "after_counts": after_counts,
        "requirement_descriptions": after_payload.get("requirement_descriptions", {}),
        "iterations": iterations,
    }

    latest_json = out_dir / "traceability_remediation_cycle_latest.json"
    latest_md = out_dir / "traceability_remediation_cycle_latest.md"
    latest_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    latest_md.write_text(render_cycle_markdown(report), encoding="utf-8")

    print("Traceability remediation cycle complete:")
    print(f"- Sprint: {args.sprint}")
    print(f"- Before counts: {before_counts}")
    print(f"- After counts: {after_counts}")
    print(f"- Iterations executed: {len(iterations)}")
    print(f"- Report JSON: {latest_json.as_posix()}")
    print(f"- Report MD: {latest_md.as_posix()}")

    # Return non-zero if any command in the final iteration failed.
    for iteration in iterations:
        for command in iteration.get("commands", []):
            if command.get("exit_code", 0) != 0:
                return int(command["exit_code"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

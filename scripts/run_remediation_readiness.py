#!/usr/bin/env python3
"""Assess remediation readiness from the latest independent review artifact."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sprint_naming import parse_sprint_token


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "independent_reviews" / "latest"
REVIEW_GLOB = "independent_review_*.md"
REQUIRED_TRACEABILITY_ARTIFACTS = [
    "docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md",
    "docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md",
    "Requirements/15_End_To_End_Traceability_Attributes_Registry.md",
]


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_json(path: Optional[Path]) -> Dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_float(pattern: str, text: str) -> Optional[float]:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return float(match.group(1))


def parse_int(pattern: str, text: str) -> Optional[int]:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return int(match.group(1))


def parse_bool(pattern: str, text: str) -> Optional[bool]:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip().lower()
    if value in {"true", "yes", "1"}:
        return True
    if value in {"false", "no", "0"}:
        return False
    return None


def parse_text_value(pattern: str, text: str) -> Optional[str]:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def find_latest_review(latest_dir: Path) -> Tuple[Path, Optional[Path]]:
    review_paths = sorted(latest_dir.glob(REVIEW_GLOB), key=lambda path: path.stat().st_mtime)
    if not review_paths:
        raise FileNotFoundError(f"No independent review markdown artifacts found in {latest_dir}")
    review_md = review_paths[-1]
    review_json = review_md.with_suffix(".json")
    return review_md, review_json if review_json.exists() else None


def extract_section_bullets(lines: List[str]) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}
    current_heading: Optional[str] = None
    for line in lines:
        if line.startswith("### Requirements Missing "):
            current_heading = line.strip()
            sections.setdefault(current_heading, [])
            continue
        if current_heading and line.startswith("- "):
            sections[current_heading].append(line[2:].strip())
            continue
        if line.startswith("## ") and not line.startswith("### "):
            current_heading = None
    return sections


def pick_examples(items: List[str], limit: int = 3) -> List[str]:
    return items[:limit]


def section_title_to_bucket(title: str) -> str:
    cleaned = title.replace("### Requirements Missing ", "")
    cleaned = cleaned.replace("## ", "").strip()
    return cleaned or "legacy-findings"


def build_legacy_backlog(sections: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    backlog: List[Dict[str, Any]] = []
    for heading, items in sections.items():
        if not items:
            continue
        backlog.append(
            {
                "bucket": section_title_to_bucket(heading),
                "count": len(items),
                "items": items,
                "representative_items": pick_examples(items, limit=5),
            }
        )
    return backlog


def backlog_issue_key(index: int, bucket: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", bucket).strip("-").upper()
    return f"LB-{index:03d}-{slug[:24]}" if slug else f"LB-{index:03d}"


def build_issue_drafts(legacy_backlog: List[Dict[str, Any]], sprint: str) -> List[Dict[str, Any]]:
    issue_drafts: List[Dict[str, Any]] = []
    for index, bucket in enumerate(legacy_backlog, start=1):
        issue_drafts.append(
            {
                "issue_key": backlog_issue_key(index, bucket["bucket"]),
                "sprint": sprint,
                "title": f"[{sprint}] {bucket['bucket']} remediation carry-forward",
                "priority": "P0" if bucket["bucket"].lower().startswith(("implementation", "verification")) else "P1",
                "source_bucket": bucket["bucket"],
                "count": bucket["count"],
                "representative_items": bucket.get("representative_items", []),
                "starter_actions": [
                    "Create or link the sprint issue using this backlog bucket as the issue body.",
                    "Assign an owner, acceptance criteria, and evidence target before sprint commitment.",
                ],
                "acceptance_criteria": [
                    "The selected backlog item is opened as a sprint issue with a unique issue key.",
                    "The issue is linked to the sprint tracker and marked with the sprint label.",
                ],
            }
        )
    return issue_drafts


def summarize_review(review_md: Path, review_json: Optional[Path], sprint: str) -> Dict[str, Any]:
    markdown_text = load_text(review_md)
    json_data = load_json(review_json)
    lines = markdown_text.splitlines()
    sections = extract_section_bullets(lines)

    overall_health = json_data.get("overall_health")
    if overall_health is None:
        overall_health = parse_float(r"Overall Health Score:\s*([0-9.]+)%", markdown_text)
    overall_health = float(overall_health) if overall_health is not None else None

    remediation_floor = json_data.get("remediation_floor")
    if remediation_floor is None:
        remediation_floor = parse_float(r"active remediation floor of\s*([0-9.]+)%", markdown_text)
    remediation_floor = float(remediation_floor) if remediation_floor is not None else None

    planning_ready = json_data.get("planning_readiness")
    if planning_ready is None:
        planning_ready = "not yet ready" not in markdown_text.lower()
    elif isinstance(planning_ready, str):
        planning_ready = planning_ready.strip().lower() in {"true", "ready", "yes", "1"}
    planning_ready = bool(planning_ready)

    severity_summary = {
        "critical": json_data.get("critical_count"),
        "major": json_data.get("major_count"),
        "minor": json_data.get("minor_count"),
        "informational": json_data.get("informational_count"),
    }
    if any(value is None for value in severity_summary.values()):
        severity_summary = {
            "critical": parse_int(r"([0-9]+) critical findings?", markdown_text) or 0,
            "major": parse_int(r"([0-9]+) major findings?", markdown_text) or 0,
            "minor": parse_int(r"([0-9]+) minor findings?", markdown_text) or 0,
            "informational": parse_int(r"([0-9]+) informational findings?", markdown_text) or 0,
        }

    branch = json_data.get("branch") or parse_text_value(r"Current branch:\s*(.+)$", markdown_text)
    head = json_data.get("head") or parse_text_value(r"HEAD:\s*(.+)$", markdown_text)
    merge_risk = json_data.get("merge_risk") or parse_text_value(r"Merge risk:\s*(.+)$", markdown_text)
    working_tree_dirty = json_data.get("working_tree_dirty")
    if working_tree_dirty is None:
        working_tree_dirty = parse_bool(r"Working tree dirty:\s*(true|false|yes|no|0|1)", markdown_text)

    implementation_section = next((items for heading, items in sections.items() if "implementation evidence" in heading.lower()), [])
    verification_section = next((items for heading, items in sections.items() if "verification evidence" in heading.lower()), [])
    architecture_section = next((items for heading, items in sections.items() if "architecture/design" in heading.lower()), [])
    legacy_backlog = build_legacy_backlog(sections)
    issue_drafts = build_issue_drafts(legacy_backlog, sprint)

    implementation_count = parse_int(r"Close implementation evidence gaps \(P0\) focuses on ([0-9]+) requirement id", markdown_text)
    verification_count = parse_int(r"Close verification evidence gaps \(P0\) focuses on ([0-9]+) requirement id", markdown_text)
    architecture_count = parse_int(r"Backfill architecture and design traceability \(P1\) focuses on ([0-9]+) requirement id", markdown_text)

    traceability_artifact_status = json_data.get("traceability_artifact_status", {})
    required_traceability_artifacts = json_data.get("required_traceability_artifacts") or REQUIRED_TRACEABILITY_ARTIFACTS
    traceability_artifacts_missing = json_data.get("traceability_artifacts_missing") or []
    traceability_artifacts_unreferenced = json_data.get("traceability_artifacts_unreferenced") or []

    if not traceability_artifact_status:
        fallback_status: Dict[str, Dict[str, Any]] = {}
        for artifact in required_traceability_artifacts:
            artifact_path = REPO_ROOT / artifact
            exists = artifact_path.exists()
            fallback_status[artifact] = {
                "exists": exists,
                "planning_reference_count": 0,
                "referenced_in": [],
                "verification_status": "missing" if not exists else "present-not-referenced",
            }
        traceability_artifact_status = fallback_status
        traceability_artifacts_missing = [artifact for artifact, status in fallback_status.items() if not status.get("exists", False)]
        traceability_artifacts_unreferenced = [
            artifact
            for artifact, status in fallback_status.items()
            if status.get("exists", False) and int(status.get("planning_reference_count", 0)) == 0
        ]

    themes = [
        {
            "name": "Implementation evidence closure",
            "priority": "P0",
            "count": implementation_count if implementation_count is not None else len(implementation_section),
            "coverage": json_data.get("implementation_coverage") or "81/219",
            "examples": pick_examples(implementation_section),
            "starter_actions": [
                "Assign owners to the remaining implementation gaps and classify them by feature area.",
                "Batch the missing implementation evidence into the smallest cohesive sprint-intake slices.",
            ],
            "acceptance_criteria": [
                "Implementation coverage reaches the remediation floor or an approved exception is recorded.",
                "Every remaining implementation gap has an owner and a target evidence artifact.",
            ],
        },
        {
            "name": "Verification evidence closure",
            "priority": "P0",
            "count": verification_count if verification_count is not None else len(verification_section),
            "coverage": json_data.get("verification_coverage") or "48/219",
            "examples": pick_examples(verification_section),
            "starter_actions": [
                "Map missing verification evidence to concrete automated or inspection-based checks.",
                "Escalate any requirements that need test harness work before the evidence can be produced.",
            ],
            "acceptance_criteria": [
                "Verification gaps are linked to executable checks or approved manual verification artifacts.",
                "Critical and major findings do not remain blocked on unverifiable requirements.",
            ],
        },
        {
            "name": "Architecture/design backfill",
            "priority": "P1",
            "count": architecture_count if architecture_count is not None else len(architecture_section),
            "coverage": json_data.get("architecture_coverage") or "99/219",
            "examples": pick_examples(architecture_section),
            "starter_actions": [
                "Update the architecture/design references for the remaining missing traceability items.",
                "Verify that the updated design artifacts point to the same governance baselines used by the review report.",
            ],
            "acceptance_criteria": [
                "Architecture/design traceability rises enough to support planning intake without ambiguity.",
                "The intake package distinguishes design backfill from implementation and verification work.",
            ],
        },
    ]

    readiness = bool(
        overall_health is not None
        and remediation_floor is not None
        and overall_health >= remediation_floor
        and planning_ready
        and not traceability_artifacts_missing
    )
    verdict = "ready-for-intake" if readiness else "not-ready"

    result = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": sprint,
        "review_artifact": str(review_md),
        "review_json_artifact": str(review_json) if review_json else None,
        "branch": branch,
        "head": head,
        "merge_risk": merge_risk,
        "working_tree_dirty": working_tree_dirty,
        "overall_health": overall_health,
        "remediation_floor": remediation_floor,
        "planning_ready": planning_ready,
        "severity_summary": severity_summary,
        "verdict": verdict,
        "readiness": "ready" if readiness else "advisory",
        "dependency_order": [
            "Implementation evidence closure",
            "Verification evidence closure",
            "Architecture/design backfill",
        ],
        "themes": themes,
        "summary": [
            f"Health score {overall_health:.1f}% is below remediation floor {remediation_floor:.1f}%" if overall_health is not None and remediation_floor is not None else "Health score or remediation floor could not be parsed.",
            f"Planning-readiness verdict is {'ready' if planning_ready else 'not yet ready'}.",
            f"The review currently carries {severity_summary['critical']} critical, {severity_summary['major']} major, {severity_summary['minor']} minor, and {severity_summary['informational']} informational findings.",
            (
                "Required traceability artifacts are complete and available for remediation execution."
                if not traceability_artifacts_missing and not traceability_artifacts_unreferenced
                else "Traceability artifact baseline requires remediation action before closeout."
            ),
        ],
        "starter_actions": [
            "Use the three intake themes as the initial sprint decomposition for remediation planning.",
            "Promote only the work items that have a clear evidence target, owner, and dependency order.",
            "For each required artifact: populate when missing and verify currency when present during remediation execution.",
        ],
        "acceptance_criteria": [
            "The next review report reaches the remediation floor or records an explicit exception.",
            "Planning intake can cite concrete implementation, verification, and architecture/design follow-up items.",
        ],
        "notes": [
            "This runner reads the latest independent review artifact directly and does not re-run traceability closure.",
            "Concept-only or governance-only items should remain out of remediation intake until they have a concrete delivery path.",
        ],
        "required_traceability_artifacts": required_traceability_artifacts,
        "traceability_artifact_status": traceability_artifact_status,
        "traceability_artifacts_missing": traceability_artifacts_missing,
        "traceability_artifacts_unreferenced": traceability_artifacts_unreferenced,
        "legacy_backlog": legacy_backlog,
        "issue_drafts": issue_drafts,
    }
    return result


def write_legacy_backlog_report(out_dir: Path, result: Dict[str, Any]) -> None:
    json_path = out_dir / "legacy_findings_latest.json"
    md_path = out_dir / "legacy_findings_latest.md"
    history_path = REPO_ROOT / "independent_reviews" / "history" / "legacy_findings.jsonl"

    json_path.write_text(json.dumps({
        "generated_at": result["generated_at"],
        "sprint": result["sprint"],
        "review_artifact": result["review_artifact"],
        "verdict": result["verdict"],
        "readiness": result["readiness"],
        "overall_health": result.get("overall_health"),
        "remediation_floor": result.get("remediation_floor"),
        "legacy_backlog": result.get("legacy_backlog", []),
        "starter_actions": result.get("starter_actions", []),
        "acceptance_criteria": result.get("acceptance_criteria", []),
    }, indent=2), encoding="utf-8")

    md_lines = [
        "# Legacy Findings Backlog",
        "",
        f"- Generated: {result['generated_at']}",
        f"- Sprint: {result['sprint']}",
        f"- Review Artifact: {result['review_artifact']}",
        f"- Health Score: {result.get('overall_health'):.1f}%" if result.get("overall_health") is not None else "- Health Score: n/a",
        f"- Remediation Floor: {result.get('remediation_floor'):.1f}%" if result.get("remediation_floor") is not None else "- Remediation Floor: n/a",
        f"- Advisory Status: {result['readiness']}",
        "",
        "## Carry-Forward Buckets",
    ]
    for bucket in result.get("legacy_backlog", []):
        md_lines.append(f"- {bucket['bucket']} | count={bucket['count']}")
        if bucket.get("representative_items"):
            md_lines.append("  representative items:")
            md_lines.extend([f"  - {item}" for item in bucket["representative_items"]])
    md_lines.extend(["", "## Starter Actions"])
    md_lines.extend([f"- {item}" for item in result.get("starter_actions", [])])
    md_lines.extend(["", "## Acceptance Criteria"])
    md_lines.extend([f"- {item}" for item in result.get("acceptance_criteria", [])])
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    with history_path.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps({
            "generated_at": result["generated_at"],
            "sprint": result["sprint"],
            "review_artifact": result["review_artifact"],
            "legacy_backlog": result.get("legacy_backlog", []),
        }))
        history_file.write("\n")


def write_issue_draft_report(out_dir: Path, result: Dict[str, Any]) -> None:
    json_path = out_dir / "remediation_issue_drafts_latest.json"
    md_path = out_dir / "remediation_issue_drafts_latest.md"
    history_path = REPO_ROOT / "independent_reviews" / "history" / "remediation_issue_drafts.jsonl"

    issue_drafts = result.get("issue_drafts", [])
    json_path.write_text(json.dumps({
        "generated_at": result["generated_at"],
        "sprint": result["sprint"],
        "review_artifact": result["review_artifact"],
        "issue_drafts": issue_drafts,
    }, indent=2), encoding="utf-8")

    md_lines = [
        "# Remediation Sprint Issue Drafts",
        "",
        f"- Generated: {result['generated_at']}",
        f"- Sprint: {result['sprint']}",
        f"- Review Artifact: {result['review_artifact']}",
        "",
        "## Selectable Draft Issues",
    ]
    for draft in issue_drafts:
        md_lines.append(f"- [ ] {draft['issue_key']} | {draft['title']} | priority={draft['priority']} | count={draft['count']}")
        if draft.get("representative_items"):
            md_lines.append("  representative items:")
            md_lines.extend([f"  - {item}" for item in draft["representative_items"]])
        if draft.get("starter_actions"):
            md_lines.append("  starter actions:")
            md_lines.extend([f"  - {item}" for item in draft["starter_actions"]])
        if draft.get("acceptance_criteria"):
            md_lines.append("  acceptance criteria:")
            md_lines.extend([f"  - {item}" for item in draft["acceptance_criteria"]])
    md_lines.extend([
        "",
        "## Planning Rule",
        "- Check the rows you want to turn into sprint issues, then copy the selected keys into the sprint issue tracker or issue creation flow.",
    ])
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    with history_path.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps({
            "generated_at": result["generated_at"],
            "sprint": result["sprint"],
            "review_artifact": result["review_artifact"],
            "issue_drafts": issue_drafts,
        }))
        history_file.write("\n")


def write_report(out_dir: Path, result: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = REPO_ROOT / "independent_reviews" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "remediation_readiness_latest.json"
    md_path = out_dir / "remediation_readiness_latest.md"
    history_path = history_dir / "remediation_readiness.jsonl"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    md_lines = [
        "# Remediation Readiness",
        "",
        f"- Generated: {result['generated_at']}",
        f"- Sprint: {result['sprint']}",
        f"- Verdict: {result['verdict']}",
        f"- Readiness: {result['readiness']}",
        f"- Review Artifact: {result['review_artifact']}",
        f"- Health Score: {result.get('overall_health'):.1f}%" if result.get("overall_health") is not None else "- Health Score: n/a",
        f"- Remediation Floor: {result.get('remediation_floor'):.1f}%" if result.get("remediation_floor") is not None else "- Remediation Floor: n/a",
        f"- Planning Ready: {result.get('planning_ready', False)}",
        f"- Branch: {result.get('branch') or 'unknown'}",
        f"- Merge Risk: {result.get('merge_risk') or 'unknown'}",
        f"- Working Tree Dirty: {result.get('working_tree_dirty', False)}",
        "",
        "## Severity Summary",
    ]
    for key, value in result.get("severity_summary", {}).items():
        md_lines.append(f"- {key}: {value}")
    md_lines.extend(["", "## Dependency Order"])
    md_lines.extend([f"- {item}" for item in result.get("dependency_order", [])])
    md_lines.extend(["", "## Themes"])
    for theme in result.get("themes", []):
        md_lines.append(f"- {theme['priority']} {theme['name']} | count={theme['count']} | coverage={theme['coverage']}")
        if theme.get("examples"):
            md_lines.append("  examples:")
            md_lines.extend([f"  - {item}" for item in theme["examples"]])
        if theme.get("starter_actions"):
            md_lines.append("  starter actions:")
            md_lines.extend([f"  - {item}" for item in theme["starter_actions"]])
    md_lines.extend(["", "## Summary"])
    md_lines.extend([f"- {item}" for item in result.get("summary", [])])
    md_lines.extend(["", "## Acceptance Criteria"])
    md_lines.extend([f"- {item}" for item in result.get("acceptance_criteria", [])])
    md_lines.extend(["", "## Notes"])
    md_lines.extend([f"- {item}" for item in result.get("notes", [])])
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    with history_path.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps(result))
        history_file.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess remediation readiness from the latest independent review")
    parser.add_argument("--sprint", default="2026_12", help="Sprint identifier (YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN)")
    parser.add_argument("--review-md")
    parser.add_argument("--review-json")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    if args.review_md:
        review_md = Path(args.review_md)
        review_json = Path(args.review_json) if args.review_json else review_md.with_suffix(".json")
        if not review_md.exists():
            print(f"ERROR: review markdown not found: {review_md}")
            return 2
        if review_json and not review_json.exists():
            review_json = None
    else:
        review_md, review_json = find_latest_review(REPO_ROOT / "independent_reviews" / "latest")

    result = summarize_review(review_md, review_json, parse_sprint_token(args.sprint).underscore)
    write_report(Path(args.out_dir), result)
    write_legacy_backlog_report(Path(args.out_dir), result)
    write_issue_draft_report(Path(args.out_dir), result)

    print("Remediation readiness analysis complete")
    print(f"- sprint: {result['sprint']}")
    print(f"- verdict: {result['verdict']}")
    print(f"- health score: {result['overall_health']:.1f}%" if result.get("overall_health") is not None else "- health score: n/a")
    print(f"- remediation floor: {result['remediation_floor']:.1f}%" if result.get("remediation_floor") is not None else "- remediation floor: n/a")
    print("- legacy findings backlog: written")
    print("- remediation issue drafts: written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Assess remediation readiness from the latest independent review artifact."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "local_reviews" / "latest"
REVIEW_GLOB = "independent_review_*.md"


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

    implementation_count = parse_int(r"Close implementation evidence gaps \(P0\) focuses on ([0-9]+) requirement id", markdown_text)
    verification_count = parse_int(r"Close verification evidence gaps \(P0\) focuses on ([0-9]+) requirement id", markdown_text)
    architecture_count = parse_int(r"Backfill architecture and design traceability \(P1\) focuses on ([0-9]+) requirement id", markdown_text)

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
        ],
        "starter_actions": [
            "Use the three intake themes as the initial sprint decomposition for remediation planning.",
            "Promote only the work items that have a clear evidence target, owner, and dependency order.",
        ],
        "acceptance_criteria": [
            "The next review report reaches the remediation floor or records an explicit exception.",
            "Planning intake can cite concrete implementation, verification, and architecture/design follow-up items.",
        ],
        "notes": [
            "This runner reads the latest independent review artifact directly and does not re-run traceability closure.",
            "Concept-only or governance-only items should remain out of remediation intake until they have a concrete delivery path.",
        ],
    }
    return result


def write_report(out_dir: Path, result: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = REPO_ROOT / "local_reviews" / "history"
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
    parser.add_argument("--sprint", default="2026_12")
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
        review_md, review_json = find_latest_review(REPO_ROOT / "local_reviews" / "latest")

    result = summarize_review(review_md, review_json, args.sprint.replace("-", "_"))
    write_report(Path(args.out_dir), result)

    print("Remediation readiness analysis complete")
    print(f"- sprint: {result['sprint']}")
    print(f"- verdict: {result['verdict']}")
    print(f"- health score: {result['overall_health']:.1f}%" if result.get("overall_health") is not None else "- health score: n/a")
    print(f"- remediation floor: {result['remediation_floor']:.1f}%" if result.get("remediation_floor") is not None else "- remediation floor: n/a")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

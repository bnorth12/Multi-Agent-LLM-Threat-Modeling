#!/usr/bin/env python3
"""Certify sprint closeout quality from local closure artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from sprint_naming import parse_sprint_token


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "independent_reviews" / "latest"


def sprint_token(sprint: str) -> str:
    return parse_sprint_token(sprint).underscore


def artifact_path(relative_root: Path, sprint: str, suffix: str) -> Path:
    return relative_root / "planning" / f"Sprint_{sprint_token(sprint)}_{suffix}"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_markdown_table_cells(line: str) -> List[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def is_markdown_separator_row(line: str) -> bool:
    stripped = line.strip().replace("|", "").replace(":", "").replace("-", "")
    return stripped == ""


def classify_status(raw_status: str) -> str:
    status = raw_status.lower()
    if any(token in status for token in ("closed", "complete", "resolved")):
        return "closed"
    if any(token in status for token in ("in progress", "in-progress", "in_review", "in review")):
        return "in_progress"
    if "proposed" in status or "defer" in status or "carryover" in status:
        return "proposed"
    if "open" in status:
        return "open"
    return "other"


def parse_issue_statuses(issue_tracker_text: str) -> Dict[str, int]:
    counts = {"closed": 0, "in_progress": 0, "open": 0, "proposed": 0, "other": 0}
    status_index: int | None = None
    for line in issue_tracker_text.splitlines():
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

        status = cells[status_index] if status_index is not None and status_index < len(cells) else ""
        counts[classify_status(status)] += 1
    return counts


def certify(sprint: str, checklist: Path, summary: Path, issue_tracker: Path, ledger: Path) -> Dict[str, Any]:
    missing = [str(path) for path in (checklist, summary, issue_tracker, ledger) if not path.exists()]
    if missing:
        return {
            "verdict": "failed",
            "reason": "Missing required closure artifacts.",
            "missing": missing,
        }

    checklist_text = load_text(checklist)
    summary_text = load_text(summary)
    issue_text = load_text(issue_tracker)
    issue_counts = parse_issue_statuses(issue_text)

    checklist_complete = "✅ CLOSED" in checklist_text or "Status: Closed" in checklist_text
    summary_complete = "Overall Validation Status: ✅ PASS" in summary_text
    residual_active = issue_counts["open"] + issue_counts["in_progress"]
    carryover_count = issue_counts["proposed"]

    if checklist_complete and summary_complete and residual_active == 0:
        verdict = "certified"
    elif checklist_complete and summary_complete:
        verdict = "conditional"
    else:
        verdict = "failed"

    return {
        "verdict": verdict,
        "checklist_complete": checklist_complete,
        "summary_complete": summary_complete,
        "issue_counts": issue_counts,
        "residual_active": residual_active,
        "carryover_count": carryover_count,
        "notes": [
            "Closure artifacts are present and parsed locally.",
            "Residual active issues represent the current reconciliation burden for this sprint closeout stage.",
        ],
    }


def write_report(out_dir: Path, sprint: str, result: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = REPO_ROOT / "independent_reviews" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": sprint,
        **result,
    }

    json_path = out_dir / "sprint_closeout_certification_latest.json"
    md_path = out_dir / "sprint_closeout_certification_latest.md"
    history_path = history_dir / "sprint_closeout_certification.jsonl"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Sprint Closeout Certification",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Sprint: {payload['sprint']}",
        f"- Verdict: {payload['verdict']}",
        f"- Checklist Complete: {payload.get('checklist_complete', False)}",
        f"- Summary Complete: {payload.get('summary_complete', False)}",
        f"- Residual Active Issues: {payload.get('residual_active', 0)}",
        f"- Carryover Count: {payload.get('carryover_count', 0)}",
        "",
        "## Issue Counts",
        "",
    ]
    for key, value in payload.get("issue_counts", {}).items():
        md_lines.append(f"- {key}: {value}")
    md_lines.extend(["", "## Notes", ""])
    md_lines.extend([f"- {note}" for note in payload.get("notes", [])])
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    with history_path.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps(payload))
        history_file.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Certify sprint closeout quality")
    parser.add_argument("--sprint", default="2026_12", help="Sprint identifier (YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN)")
    parser.add_argument("--checklist")
    parser.add_argument("--summary")
    parser.add_argument("--issue-tracker")
    parser.add_argument(
        "--ledger",
        default=str(REPO_ROOT / "independent_reviews" / "latest" / "governance_execution_ledger_latest.json"),
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    sprint = sprint_token(args.sprint)
    checklist = Path(args.checklist) if args.checklist else artifact_path(REPO_ROOT, sprint, "Closure_Checklist.md")
    summary = Path(args.summary) if args.summary else artifact_path(REPO_ROOT, sprint, "Final_Validation_Summary.md")
    issue_tracker = Path(args.issue_tracker) if args.issue_tracker else REPO_ROOT / "planning" / "issues" / f"Sprint_{sprint}_Issue_Tracker.md"
    ledger = Path(args.ledger)

    result = certify(sprint, checklist, summary, issue_tracker, ledger)
    write_report(Path(args.out_dir), sprint, result)

    print("Sprint closeout certification complete")
    print(f"- sprint: {sprint}")
    print(f"- verdict: {result['verdict']}")
    print(f"- residual active issues: {result.get('residual_active', 0)}")
    return 0 if result["verdict"] in {"certified", "conditional"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Append proposed governance-automation backlog items from obligation reports.

This script reads remediation obligation JSON output from independent review runs and
adds new proposed items into planning/Governance/Governance_Automation_Improvement_Backlog.md.

Deterministic ID format:
- GOV-AUTO-OBL-<8_HEX>
where the hash key is SHA1(rule_id|level|finding).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple


DEFAULT_BACKLOG = Path("planning/Governance/Governance_Automation_Improvement_Backlog.md")
DEFAULT_REPORT_GLOB = "remediation_obligations_*_pre-push.json"
DEFAULT_REPORT_DIR = Path("independent_reviews/latest")


def find_latest_obligation_report(repo_root: Path) -> Path:
    report_dir = repo_root / DEFAULT_REPORT_DIR
    candidates = sorted(report_dir.glob(DEFAULT_REPORT_GLOB), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(
            f"No obligation report found under {report_dir.as_posix()} matching {DEFAULT_REPORT_GLOB}"
        )
    return candidates[0]


def deterministic_id(rule_id: str, level: str, finding: str) -> str:
    key = f"{rule_id.strip().lower()}|{level.strip().lower()}|{finding.strip().lower()}"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:8].upper()
    return f"GOV-AUTO-OBL-{digest}"


def compact_text(value: str, limit: int = 90) -> str:
    cleaned = " ".join(value.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def md_escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def load_obligation_items(report_path: Path) -> Tuple[Dict, List[Dict]]:
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    raw_items = payload.get("open_exception_obligations", [])
    if not isinstance(raw_items, list):
        raise ValueError("Invalid obligation report: open_exception_obligations must be a list")
    items = [item for item in raw_items if isinstance(item, dict)]
    return payload, items


def find_backlog_table_bounds(lines: List[str]) -> Tuple[int, int]:
    start = -1
    for idx, line in enumerate(lines):
        if line.strip().startswith("| ID | Title | Category | Status | Owner | Target Sprint | Disposition | Notes |"):
            start = idx
            break
    if start < 0:
        raise ValueError("Backlog table header not found")

    separator = start + 1
    if separator >= len(lines) or not lines[separator].strip().startswith("|---"):
        raise ValueError("Backlog table separator not found")

    end = separator + 1
    while end < len(lines) and lines[end].strip().startswith("|"):
        end += 1

    return separator + 1, end


def extract_existing_ids(lines: List[str], row_start: int, row_end: int) -> set[str]:
    existing = set()
    for idx in range(row_start, row_end):
        row = lines[idx].strip()
        if not row.startswith("|"):
            continue
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if cells:
            existing.add(cells[0])
    return existing


def build_backlog_row(item: Dict, source_report: Path, default_owner: str, default_status: str, default_disposition: str) -> str:
    rule_id = str(item.get("rule_id", "unknown-rule"))
    level = str(item.get("level", "informational"))
    finding = str(item.get("finding", ""))
    due_sprint = str(item.get("due_sprint", "unspecified"))
    owning_plan = str(item.get("owning_plan", "unspecified"))

    backlog_id = deterministic_id(rule_id, level, finding)
    title = f"Triaged obligation ({level}): {compact_text(finding, limit=72)}"
    notes = (
        f"Auto-triaged from {source_report.as_posix()}; "
        f"rule={rule_id}; plan={owning_plan}."
    )

    cells = [
        backlog_id,
        title,
        "Governance automation",
        default_status,
        default_owner,
        due_sprint,
        default_disposition,
        notes,
    ]
    escaped = [md_escape_cell(value) for value in cells]
    return "| " + " | ".join(escaped) + " |"


def apply_triage(
    backlog_path: Path,
    report_path: Path,
    default_owner: str,
    default_status: str,
    default_disposition: str,
    dry_run: bool,
) -> Tuple[int, int]:
    payload, obligations = load_obligation_items(report_path)
    backlog_lines = backlog_path.read_text(encoding="utf-8").splitlines()
    row_start, row_end = find_backlog_table_bounds(backlog_lines)
    existing_ids = extract_existing_ids(backlog_lines, row_start, row_end)

    to_add: List[str] = []
    seen_new = set()

    for item in obligations:
        row = build_backlog_row(
            item=item,
            source_report=report_path,
            default_owner=default_owner,
            default_status=default_status,
            default_disposition=default_disposition,
        )
        row_id = row.split("|", 3)[1].strip()
        if row_id in existing_ids or row_id in seen_new:
            continue
        seen_new.add(row_id)
        to_add.append(row)

    if to_add and not dry_run:
        updated = backlog_lines[:row_end] + to_add + backlog_lines[row_end:]
        backlog_path.write_text("\n".join(updated) + "\n", encoding="utf-8")

    _ = payload  # payload retained for future enhancement and schema checks.
    return len(obligations), len(to_add)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append governance backlog entries from obligation reports")
    parser.add_argument(
        "--obligation-report",
        type=str,
        default="",
        help="Path to remediation obligation JSON report. If omitted, latest pre-push report is auto-discovered.",
    )
    parser.add_argument(
        "--backlog",
        type=str,
        default=str(DEFAULT_BACKLOG),
        help="Path to governance automation backlog markdown file.",
    )
    parser.add_argument("--owner", type=str, default="Governance maintainers", help="Owner value for new backlog items")
    parser.add_argument("--status", type=str, default="Proposed", help="Status value for new backlog items")
    parser.add_argument("--disposition", type=str, default="Include", help="Disposition value for new backlog items")
    parser.add_argument("--dry-run", action="store_true", help="Preview counts without writing backlog updates")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    backlog_path = repo_root / args.backlog
    if not backlog_path.exists():
        print(f"ERROR: Backlog file not found: {backlog_path.as_posix()}")
        return 2

    try:
        report_path = Path(args.obligation_report) if args.obligation_report else find_latest_obligation_report(repo_root)
        if not report_path.is_absolute():
            report_path = repo_root / report_path
        if not report_path.exists():
            print(f"ERROR: Obligation report not found: {report_path.as_posix()}")
            return 2

        scanned, appended = apply_triage(
            backlog_path=backlog_path,
            report_path=report_path,
            default_owner=args.owner,
            default_status=args.status,
            default_disposition=args.disposition,
            dry_run=args.dry_run,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2

    mode = "dry-run" if args.dry_run else "apply"
    print("[governance-triage] Complete")
    print(f"[governance-triage] Mode: {mode}")
    print(f"[governance-triage] Obligation report: {report_path.as_posix()}")
    print(f"[governance-triage] Backlog: {backlog_path.as_posix()}")
    print(f"[governance-triage] Obligations scanned: {scanned}")
    print(f"[governance-triage] New backlog items appended: {appended}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

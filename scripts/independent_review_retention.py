#!/usr/bin/env python3
"""Retention maintenance for independent review latest outputs.

This script archives current run-context outputs from independent_reviews/latest
into per-context history batches before new files are generated. It then compacts
older history batches at the same run-context level.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
from pathlib import Path
from typing import Dict, List

HISTORY_CONTEXT_ARCHIVE_DIR = Path("independent_reviews/history/reports/by_context")


def build_expected_latest_filenames(sprint: str, run_context: str) -> List[str]:
    names = [
        f"independent_review_{sprint}_{run_context}.md",
        f"independent_review_{sprint}_{run_context}.json",
    ]

    if run_context == "pre-push":
        names.extend(
            [
                f"remediation_obligations_{sprint}_{run_context}.md",
                f"remediation_obligations_{sprint}_{run_context}.json",
                "governance_execution_ledger_latest.md",
                "governance_execution_ledger_latest.json",
                "traceability_blocker_backlog_latest.md",
                "traceability_blocker_backlog_latest.json",
                "traceability_remediation_cycle_latest.md",
                "traceability_remediation_cycle_latest.json",
                "architecture_design_authoring_workpack_latest.md",
                "architecture_design_authoring_workpack_latest.json",
                "legacy_findings_latest.md",
                "legacy_findings_latest.json",
                "remediation_issue_drafts_latest.md",
                "remediation_issue_drafts_latest.json",
                "remediation_readiness_latest.md",
                "remediation_readiness_latest.json",
            ]
        )

    return names


def build_expected_latest_globs(sprint: str, run_context: str) -> List[str]:
    if run_context != "pre-push":
        return []
    return [
        f"traceability_remediation_plan_{sprint}_iter_*.md",
        f"traceability_remediation_plan_{sprint}_iter_*.json",
        "unimplemented_requirement_triage_*.md",
        "unimplemented_requirement_triage_*.json",
    ]


def compact_context_history(history_context_dir: Path, retain_auto_batches: int) -> Dict[str, object]:
    batch_dirs = sorted(
        [path for path in history_context_dir.glob("auto_compaction_*") if path.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )
    stale = batch_dirs[max(0, retain_auto_batches) :]
    if not stale:
        return {
            "retained_batches": min(len(batch_dirs), max(0, retain_auto_batches)),
            "summarized_batches": 0,
        }

    summary_path = history_context_dir / "compaction_summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            summary = {}
    else:
        summary = {}

    previous = summary.get("compacted_batches", [])
    if not isinstance(previous, list):
        previous = []

    compacted_entries: List[Dict[str, object]] = []
    for batch in stale:
        removed = False
        compacted_entries.append(
            {
                "batch": batch.name,
                "file_count": len([path for path in batch.iterdir() if path.is_file()]),
                "removed": removed,
            }
        )
        try:
            shutil.rmtree(batch)
            removed = True
        except PermissionError:
            removed = False
        compacted_entries[-1]["removed"] = removed

    summary["last_compacted_at"] = dt.datetime.now().isoformat(timespec="seconds")
    summary["retained_batch_count"] = max(0, retain_auto_batches)
    summary["compacted_batches"] = previous + compacted_entries
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return {
        "retained_batches": min(len(batch_dirs), max(0, retain_auto_batches)),
        "summarized_batches": len(stale),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive/compact independent review latest outputs by run context")
    parser.add_argument("--repo-root", type=str, default=".", help="Repository root path")
    parser.add_argument("--sprint", type=str, required=True, help="Sprint identifier as used in report file names, e.g. 2026-013")
    parser.add_argument("--run-context", choices=["manual", "pre-commit", "pre-merge-commit", "pre-push", "closeout"], required=True)
    parser.add_argument("--out-dir", type=str, default="independent_reviews/latest", help="Latest reports directory")
    parser.add_argument("--retain-auto-batches", type=int, default=2, help="How many newest auto_compaction batches to keep")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    if not out_dir.exists():
        print(
            json.dumps(
                {
                    "context": args.run_context,
                    "status": "no-op",
                    "reason": f"out-dir not found: {out_dir.as_posix()}",
                },
                indent=2,
            )
        )
        return 0

    expected = build_expected_latest_filenames(args.sprint, args.run_context)
    candidates = [path for path in (out_dir / name for name in expected) if path.exists() and path.is_file()]
    for pattern in build_expected_latest_globs(args.sprint, args.run_context):
        candidates.extend([path for path in out_dir.glob(pattern) if path.is_file()])

    deduped: Dict[str, Path] = {}
    for candidate in candidates:
        deduped[candidate.name] = candidate
    candidates = sorted(deduped.values(), key=lambda p: p.name)

    history_context_dir = repo_root / HISTORY_CONTEXT_ARCHIVE_DIR / args.run_context
    history_context_dir.mkdir(parents=True, exist_ok=True)

    moved: List[str] = []
    if candidates:
        batch_name = dt.datetime.now().strftime("auto_compaction_%Y%m%d_%H%M%S")
        batch_dir = history_context_dir / batch_name
        batch_dir.mkdir(parents=True, exist_ok=True)
        for file_path in candidates:
            destination = batch_dir / file_path.name
            shutil.move(str(file_path), str(destination))
            moved.append(destination.as_posix())

    compact_summary = compact_context_history(
        history_context_dir=history_context_dir,
        retain_auto_batches=max(0, args.retain_auto_batches),
    )

    print(
        json.dumps(
            {
                "context": args.run_context,
                "sprint": args.sprint,
                "moved_from_latest": len(moved),
                "moved_files": moved,
                "history_context_dir": history_context_dir.as_posix(),
                "retained_batches": compact_summary.get("retained_batches", 0),
                "summarized_batches": compact_summary.get("summarized_batches", 0),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

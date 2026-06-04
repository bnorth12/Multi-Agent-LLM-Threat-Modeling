#!/usr/bin/env python3
"""One-time backfill for trend snapshot epoch metadata.

This utility annotates legacy trend snapshots with explicit epoch metadata used by
independent review trend dashboards and migration reporting.

Default behavior is dry-run. Use --write to persist changes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

DEFAULT_HISTORY_FILE = Path("independent_reviews/history/snapshot_index.json")
DEFAULT_MIGRATION_DIR = Path("independent_reviews/history/migrations")

LEGACY_TAGS = {
    "review_schema_version": 1,
    "traceability_baseline_mode": "legacy-line-scan",
    "relationship_direction_mode": "none",
    "trend_epoch": "legacy",
}

CURRENT_TAGS = {
    "review_schema_version": 2,
    "traceability_baseline_mode": "matrix-and-ground-truth-v2",
    "relationship_direction_mode": "documentation_vs_ground_truth",
    "trend_epoch": "taxonomy-direction-v2",
}


@dataclass
class BackfillSummary:
    total_entries: int
    legacy_tagged: int
    current_tagged: int
    unchanged: int
    changed: int


def classify_and_backfill(entry: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
    updated = dict(entry)
    changed = False

    schema = updated.get("review_schema_version")
    baseline = updated.get("traceability_baseline_mode")
    direction = updated.get("relationship_direction_mode")
    epoch = updated.get("trend_epoch")

    # Treat entries as current only when all current markers are already present.
    is_explicit_current = (
        schema == CURRENT_TAGS["review_schema_version"]
        and baseline == CURRENT_TAGS["traceability_baseline_mode"]
        and direction == CURRENT_TAGS["relationship_direction_mode"]
        and epoch == CURRENT_TAGS["trend_epoch"]
    )

    if is_explicit_current:
        return updated, changed, "current"

    # Any non-current record is normalized to explicit legacy tags for
    # backward-compatible trend dashboards and migration analytics.
    for key, value in LEGACY_TAGS.items():
        if updated.get(key) != value:
            updated[key] = value
            changed = True

    return updated, changed, "legacy"


def run_backfill(history_path: Path) -> Tuple[List[Dict[str, Any]], BackfillSummary]:
    raw = json.loads(history_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("snapshot history must be a JSON list")

    updated_entries: List[Dict[str, Any]] = []
    changed_count = 0
    legacy_count = 0
    current_count = 0

    for item in raw:
        if not isinstance(item, dict):
            # Preserve non-dict entries unchanged; still counted in total/unchanged.
            updated_entries.append(item)
            continue

        updated, changed, bucket = classify_and_backfill(item)
        updated_entries.append(updated)
        if changed:
            changed_count += 1
        if bucket == "legacy":
            legacy_count += 1
        else:
            current_count += 1

    summary = BackfillSummary(
        total_entries=len(updated_entries),
        legacy_tagged=legacy_count,
        current_tagged=current_count,
        unchanged=len(updated_entries) - changed_count,
        changed=changed_count,
    )
    return updated_entries, summary


def write_migration_report(
    repo_root: Path,
    migration_dir: Path,
    history_path: Path,
    summary: BackfillSummary,
    write_applied: bool,
) -> Tuple[Path, Path]:
    migration_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = migration_dir / f"snapshot_epoch_backfill_{stamp}.md"
    json_path = migration_dir / f"snapshot_epoch_backfill_{stamp}.json"

    payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "history_file": history_path.as_posix(),
        "write_applied": write_applied,
        "summary": {
            "total_entries": summary.total_entries,
            "legacy_tagged": summary.legacy_tagged,
            "current_tagged": summary.current_tagged,
            "unchanged": summary.unchanged,
            "changed": summary.changed,
        },
        "legacy_tags": LEGACY_TAGS,
        "current_tags": CURRENT_TAGS,
    }

    lines = [
        "# Snapshot Epoch Backfill Report",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- History file: {history_path.as_posix()}",
        f"- Write applied: {write_applied}",
        "",
        "## Summary",
        f"- Total entries: {summary.total_entries}",
        f"- Legacy tagged entries: {summary.legacy_tagged}",
        f"- Current tagged entries: {summary.current_tagged}",
        f"- Changed entries: {summary.changed}",
        f"- Unchanged entries: {summary.unchanged}",
        "",
        "## Tag Policy",
        "- Legacy tags:",
        f"  - review_schema_version={LEGACY_TAGS['review_schema_version']}",
        f"  - traceability_baseline_mode={LEGACY_TAGS['traceability_baseline_mode']}",
        f"  - relationship_direction_mode={LEGACY_TAGS['relationship_direction_mode']}",
        f"  - trend_epoch={LEGACY_TAGS['trend_epoch']}",
        "- Current tags:",
        f"  - review_schema_version={CURRENT_TAGS['review_schema_version']}",
        f"  - traceability_baseline_mode={CURRENT_TAGS['traceability_baseline_mode']}",
        f"  - relationship_direction_mode={CURRENT_TAGS['relationship_direction_mode']}",
        f"  - trend_epoch={CURRENT_TAGS['trend_epoch']}",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill explicit legacy epoch tags in trend snapshots")
    parser.add_argument(
        "--history-file",
        type=str,
        default=DEFAULT_HISTORY_FILE.as_posix(),
        help="Path to independent review snapshot history JSON",
    )
    parser.add_argument(
        "--migration-dir",
        type=str,
        default=DEFAULT_MIGRATION_DIR.as_posix(),
        help="Directory where migration report artifacts are written",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Persist updated history file in place (default is dry-run)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    history_path = (repo_root / args.history_file).resolve()
    migration_dir = (repo_root / args.migration_dir).resolve()

    if not history_path.exists():
        print(f"[snapshot-epoch-backfill] ERROR: history file not found: {history_path.as_posix()}")
        return 2

    try:
        updated_entries, summary = run_backfill(history_path)
    except Exception as exc:
        print(f"[snapshot-epoch-backfill] ERROR: unable to process history: {exc}")
        return 2

    if args.write:
        history_path.write_text(json.dumps(updated_entries, indent=2), encoding="utf-8")

    md_report, json_report = write_migration_report(
        repo_root=repo_root,
        migration_dir=migration_dir,
        history_path=history_path,
        summary=summary,
        write_applied=args.write,
    )

    print("[snapshot-epoch-backfill] Complete")
    print(f"[snapshot-epoch-backfill] Write applied: {args.write}")
    print(f"[snapshot-epoch-backfill] Total entries: {summary.total_entries}")
    print(f"[snapshot-epoch-backfill] Legacy tagged entries: {summary.legacy_tagged}")
    print(f"[snapshot-epoch-backfill] Current tagged entries: {summary.current_tagged}")
    print(f"[snapshot-epoch-backfill] Changed entries: {summary.changed}")
    print(f"[snapshot-epoch-backfill] Unchanged entries: {summary.unchanged}")
    print(f"[snapshot-epoch-backfill] Markdown report: {md_report.as_posix()}")
    print(f"[snapshot-epoch-backfill] JSON report: {json_report.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

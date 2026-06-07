#!/usr/bin/env python3
"""Retention maintenance for independent review latest outputs.

This script archives current run-context outputs from independent_reviews/latest
into per-context history batches before new files are generated. It compacts
older history batches for the same run-context before and after archival so the
next governance cycle starts from a clean latest directory and bounded history.
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
    # Enforce single canonical independent review file (md + json) in latest/.
    # Other governance outputs are embedded in the review appendices or compacted.
    # This prevents proliferation of separate review/sidecar files and limits
    # tracked churn to the two known files (as expected by policy for pre-push/push).
    names = [
        f"independent_review_{sprint}_{run_context}.md",
        f"independent_review_{sprint}_{run_context}.json",
    ]
    return names


def build_expected_latest_globs(sprint: str, run_context: str) -> List[str]:
    # Non-canonical pre-push sidecars and iter artifacts are always compaction candidates.
    if run_context == "pre-push":
        return [
            "*remediation_obligations_*",
            "*governance_execution_ledger_latest.*",
            "*traceability_blocker_backlog_latest.*",
            "*traceability_remediation_cycle_latest.*",
            "*architecture_design_authoring_workpack_latest.*",
            "*legacy_findings_latest.*",
            "*remediation_issue_drafts_latest.*",
            "*remediation_readiness_latest.*",
            f"traceability_remediation_plan_{sprint}_iter_*.md",
            f"traceability_remediation_plan_{sprint}_iter_*.json",
            "unimplemented_requirement_triage_*.md",
            "unimplemented_requirement_triage_*.json",
        ]
    return []


def build_retention_candidates(out_dir: Path, sprint: str, run_context: str) -> List[Path]:
    if run_context == "pre-push":
        # Pre-push regenerates the *single canonical independent review pair*.
        # Archive everything currently in latest/ so the post-run state has only
        # the two known files (the exception we document for dirty tree).
        return sorted([path for path in out_dir.iterdir() if path.is_file()], key=lambda p: p.name)

    expected = build_expected_latest_filenames(sprint, run_context)
    candidates = [path for path in (out_dir / name for name in expected) if path.exists() and path.is_file()]
    for pattern in build_expected_latest_globs(sprint, run_context):
        candidates.extend([path for path in out_dir.glob(pattern) if path.is_file()])

    deduped: Dict[str, Path] = {}
    for candidate in candidates:
        deduped[candidate.name] = candidate
    return sorted(deduped.values(), key=lambda p: p.name)


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


def _write_ier_mitigation_snapshots(batch_dir: Path) -> None:
    """Extract key IER fields (scores, gaps, suggestions, engineering health) from
    any independent_review_*.md or .json moved into this batch and write a
    compact ier_mitigation_snapshot.json alongside for roll-up consumers.
    Preserves the updated Independent Engineering Review (per-class scorecards,
    cross-cutting with L0-L4 mappings, Traceability Matrix Audit, Suggested
    additions) and prior finding context when previous reports are archived.
    """
    import re
    snapshot: Dict[str, Any] = {
        "batch": batch_dir.name,
        "archived_at": dt.datetime.now().isoformat(timespec="seconds"),
        "reviews": [],
    }

    for p in sorted(batch_dir.glob("independent_review_*.md")):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            rec: Dict[str, Any] = {"file": p.name}
            # Extract key headers and counts (tolerant regex for the rich IER structure)
            m = re.search(r"Generated:\s*([0-9T:.-]+)", text)
            if m:
                rec["generated"] = m.group(1)
            m = re.search(r"Overall Health Score \(legacy\):\s*([\d.]+)%", text)
            if m:
                rec["legacy_health"] = float(m.group(1))
            m = re.search(r"Overall Engineering Health Score \(new model\):\s*([\d.]+)%", text)
            if m:
                rec["engineering_health"] = float(m.group(1))
            m = re.search(r"Implementation under-documented:\s*(\d+)", text)
            if m:
                rec["impl_under_documented"] = int(m.group(1))
            m = re.search(r"Verification under-documented:\s*(\d+)", text)
            if m:
                rec["verify_under_documented"] = int(m.group(1))
            m = re.search(r"Architecture/design under-documented:\s*(\d+)", text)
            if m:
                rec["arch_under_documented"] = int(m.group(1))
            # Count suggested sections
            sugg_count = len(re.findall(r"Suggested \d+ row\(s\)", text))
            rec["suggested_row_count"] = sugg_count
            # Capture if cross-cutting / scorecards present (rich IER model indicator)
            rec["has_engineering_scorecards"] = "Engineering Artifact Class Scorecards" in text
            rec["has_cross_cutting"] = "Cross-Cutting Engineering Analyses" in text
            rec["has_matrix_audit"] = "Traceability Matrix Audit (vs Actual Engineering" in text
            snapshot["reviews"].append(rec)
        except Exception:
            pass

    # Also quick look at json for exact numbers if present (prefer structured)
    for p in sorted(batch_dir.glob("independent_review_*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
            # If the json has the new top level fields from ReviewResult, surface them
            if isinstance(data, dict):
                for rev in snapshot["reviews"]:
                    if rev.get("file", "").replace(".md", ".json") == p.name:
                        rev["json_engineering_health"] = data.get("overall_engineering_health_score")
                        rev["json_matrix_discrepancies"] = data.get("traceability_matrix_audit", {}).get("matrix_vs_engineering_discrepancies") if isinstance(data.get("traceability_matrix_audit"), dict) else None
                        break
                else:
                    # attach top level if no matching md rec
                    snapshot["reviews"].append({
                        "file": p.name,
                        "json_engineering_health": data.get("overall_engineering_health_score"),
                    })
        except Exception:
            pass

    if snapshot["reviews"]:
        out = batch_dir / "ier_mitigation_snapshot.json"
        out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")


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

    candidates = build_retention_candidates(out_dir=out_dir, sprint=args.sprint, run_context=args.run_context)

    history_context_dir = repo_root / HISTORY_CONTEXT_ARCHIVE_DIR / args.run_context
    history_context_dir.mkdir(parents=True, exist_ok=True)

    pre_compact_summary = compact_context_history(
        history_context_dir=history_context_dir,
        retain_auto_batches=max(0, args.retain_auto_batches),
    )

    moved: List[str] = []
    if candidates:
        batch_name = dt.datetime.now().strftime("auto_compaction_%Y%m%d_%H%M%S")
        batch_dir = history_context_dir / batch_name
        batch_dir.mkdir(parents=True, exist_ok=True)
        for file_path in candidates:
            destination = batch_dir / file_path.name
            shutil.move(str(file_path), str(destination))
            moved.append(destination.as_posix())

        # IER roll-up enrichment: for archived independent review canonical pairs,
        # emit a compact mitigation context snapshot so that prior findings,
        # per-class scorecards, cross-cutting analyses (L0-L4 etc.), matrix audit,
        # and "Suggested Matrix Row Additions" at the time of the run are easily
        # queryable in history without re-parsing full MD/JSON on every future roll-up.
        # This preserves the rich Independent Engineering Review view and the
        # mitigation trail across pre-push/push/manual archival.
        try:
            _write_ier_mitigation_snapshots(batch_dir)
        except Exception as exc:
            print(f"[retention] warning: failed to write IER mitigation snapshot: {exc}")

    post_compact_summary = compact_context_history(
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
                "pre_compaction": pre_compact_summary,
                "post_compaction": post_compact_summary,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run phase 4 governance maintenance checks and publish a latest summary."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run phase 4 maintenance checks for documentation and archive hygiene."
    )
    parser.add_argument(
        "--out-md",
        default="independent_reviews/latest/phase4_maintenance_latest.md",
        help="Markdown output path relative to repository root.",
    )
    parser.add_argument(
        "--out-json",
        default="independent_reviews/latest/phase4_maintenance_latest.json",
        help="JSON output path relative to repository root.",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Return non-zero when drift findings are detected.",
    )
    return parser.parse_args()


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def tracked_count(path: str) -> int:
    output = run_git(["ls-files", path])
    if not output:
        return 0
    return len(output.splitlines())


def scan_markdown_files() -> list[Path]:
    active_files = [
        REPO_ROOT / "planning" / "README.md",
        REPO_ROOT / "planning" / "Sprint_Planning_Checklist_Template.md",
        REPO_ROOT / "planning" / "Sprint_Traceability_Matrix_Template.md",
        REPO_ROOT / "planning" / "Sprint_Closure_Checklist_Template.md",
    ]

    files: list[Path] = []

    process_root = REPO_ROOT / "docs" / "process"
    if process_root.exists():
        files.extend(sorted(process_root.rglob("*.md")))

    for file_path in active_files:
        if file_path.exists():
            files.append(file_path)

    return files


def detect_drift(files: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    hyphenated_script = re.compile(r"verify-sprint-traceability\\.py")
    sprint_template_drift = re.compile(r"Sprint_YYYY_MM")

    for file_path in files:
        rel = file_path.relative_to(REPO_ROOT).as_posix()
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for idx, line in enumerate(lines, start=1):
            if hyphenated_script.search(line):
                findings.append(
                    {
                        "type": "script-name-drift",
                        "file": rel,
                        "line": idx,
                        "detail": "Use scripts/verify_sprint_traceability.py in active docs.",
                    }
                )

            if sprint_template_drift.search(line):
                # Keep governance migration narratives that mention legacy formats.
                if "Legacy" in line or "legacy" in line:
                    continue
                if "Sprint_YYYY_NN" in line:
                    continue
                findings.append(
                    {
                        "type": "sprint-template-drift",
                        "file": rel,
                        "line": idx,
                        "detail": "Use Sprint_YYYY_NN in active templates and examples.",
                    }
                )

    return findings


def write_outputs(out_md: Path, out_json: Path, findings: list[dict[str, Any]], counts: dict[str, int]) -> None:
    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    payload = {
        "generated_at_utc": timestamp,
        "finding_count": len(findings),
        "findings": findings,
        "tracked_counts": counts,
        "status": "PASS" if not findings else "ACTION_REQUIRED",
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("# Phase 4 Governance Maintenance (Latest)\n\n")
    lines.append(f"- Generated (UTC): {timestamp}\n")
    lines.append(f"- Status: {payload['status']}\n")
    lines.append(f"- Drift findings: {len(findings)}\n\n")

    lines.append("## Tracked Volume Snapshot\n\n")
    lines.append("| Area | Tracked Files |\n")
    lines.append("|---|---:|\n")
    for key in sorted(counts.keys()):
        lines.append(f"| {key} | {counts[key]} |\n")

    lines.append("\n## Drift Findings\n\n")
    if findings:
        lines.append("| Type | File | Line | Detail |\n")
        lines.append("|---|---|---:|---|\n")
        for finding in findings:
            lines.append(
                f"| {finding['type']} | {finding['file']} | {finding['line']} | {finding['detail']} |\n"
            )
    else:
        lines.append("- None.\n")

    lines.append("\n## Required Actions\n\n")
    if findings:
        lines.append("1. Fix all drift findings in active governance and process documents.\n")
        lines.append("1. Re-run this maintenance script and confirm zero findings.\n")
        lines.append("1. Capture closure in planning/Governance phase tracker artifacts.\n")
    else:
        lines.append("1. Keep weekly and monthly cadence unchanged.\n")
        lines.append("1. Continue publishing this latest report with automated reminders.\n")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()

    counts = {
        "planning": tracked_count("planning"),
        "FQT": tracked_count("FQT"),
        "independent_reviews/latest": tracked_count("independent_reviews/latest"),
        "docs": tracked_count("docs"),
        "Requirements": tracked_count("Requirements"),
        "Tests": tracked_count("Tests"),
    }

    markdown_files = scan_markdown_files()
    findings = detect_drift(markdown_files)

    out_md = (REPO_ROOT / args.out_md).resolve()
    out_json = (REPO_ROOT / args.out_json).resolve()
    write_outputs(out_md, out_json, findings, counts)

    print(f"Wrote {out_md.relative_to(REPO_ROOT).as_posix()}")
    print(f"Wrote {out_json.relative_to(REPO_ROOT).as_posix()}")

    if args.enforce and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

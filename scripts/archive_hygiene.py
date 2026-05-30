#!/usr/bin/env python3
"""Archive hygiene checks and archive-batch scaffolding."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ManagedArea:
    name: str
    root: str
    archive_dir: str
    candidate_globs: tuple[str, ...]
    active_allowlist: tuple[str, ...]


MANAGED_AREAS = (
    ManagedArea(
        name="planning evidence",
        root="planning",
        archive_dir="planning/archives",
        candidate_globs=(
            "Test_Execution_Summary_Sprint_*.md",
            "SESSION_COMPLETION_SUMMARY_*.md",
            "Smoke_Run_Evidence_*.md",
            "FQT_Test_Report_Sprint_*.md",
            "*_Completion_Report.md",
            "*_Completion_Summary.md",
            "Sprint_*_Execution_Log.md",
            "Sprint_*_Final_Validation_Summary.md",
        ),
        active_allowlist=(
            "planning/Test_Execution_Summary_Sprint_2026_01.md",
            "planning/Test_Execution_Summary_Sprint_2026_09.md",
            "planning/Test_Execution_Summary_Sprint_2026_10.md",
            "planning/Test_Execution_Summary_Sprint_2026_11.md",
            "planning/Sprint_2026_01_Final_Validation_Summary.md",
            "planning/FQT_Test_Report_Sprint_2026_11.md",
            "planning/Sprint_2026_12_Execution_Log.md",
            "planning/Sprint_2026_12_Final_Validation_Summary.md",
            "planning/Lane_C_Watchdog_Tuning_Completion_Report.md",
            "planning/S12_HMI_Completion_Summary.md",
        ),
    ),
    ManagedArea(
        name="planning feature-branch metadata",
        root="planning/feature_branches",
        archive_dir="planning/archives",
        candidate_globs=(
            "feature_sprint_2026_05.md",
            "Sprint_2026_05_PR_Template.md",
        ),
        active_allowlist=(),
    ),
    ManagedArea(
        name="legacy planning tracker surfaces",
        root="planning/issues",
        archive_dir="planning/archives",
        candidate_globs=(
            "Sprint_2026_05_06_Issue_Tracker.md",
        ),
        active_allowlist=(),
    ),
    ManagedArea(
        name="threat-alignment governance evidence",
        root="data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment",
        archive_dir="data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/archive",
        candidate_globs=(
            "*_execution_report.md",
            "*_audit.md",
            "*_sweep.md",
        ),
        active_allowlist=(),
    ),
)


@dataclass(frozen=True)
class ChangeRecord:
    status: str
    old_path: str | None
    new_path: str | None


def _run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def _normalize(path: str) -> str:
    return path.replace("\\", "/")


def _matches_any(path: str, patterns: Iterable[str]) -> bool:
    candidate = Path(path)
    return any(candidate.match(pattern) for pattern in patterns)


def _path_in_area(path: str, area: ManagedArea) -> bool:
    return path == area.root or path.startswith(area.root + "/")


def _path_in_archive(path: str, area: ManagedArea) -> bool:
    return path == area.archive_dir or path.startswith(area.archive_dir + "/")


def _is_candidate(path: str, area: ManagedArea) -> bool:
    if not _path_in_area(path, area) or _path_in_archive(path, area):
        return False
    return _matches_any(Path(path).name, area.candidate_globs)


def _is_allowlisted(path: str, area: ManagedArea) -> bool:
    return any(Path(path).match(pattern) for pattern in area.active_allowlist)


def _parse_name_status(output: str) -> list[ChangeRecord]:
    records: list[ChangeRecord] = []
    for raw_line in output.splitlines():
        if not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        status = parts[0]
        if status.startswith("R") or status.startswith("C"):
            records.append(
                ChangeRecord(status=status, old_path=_normalize(parts[1]), new_path=_normalize(parts[2]))
            )
        else:
            records.append(ChangeRecord(status=status, old_path=None, new_path=_normalize(parts[1])))
    return records


def _get_change_records(args: argparse.Namespace) -> list[ChangeRecord]:
    if args.staged:
        output = _run_git(["diff", "--cached", "--name-status", "--find-renames", "--diff-filter=ACMRD"])
        return _parse_name_status(output)
    if args.upstream:
        try:
            _run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"])
        except subprocess.CalledProcessError:
            return []
        output = _run_git(["diff", "--name-status", "--find-renames", "--diff-filter=ACMRD", "@{upstream}...HEAD"])
        return _parse_name_status(output)
    if args.changed_against:
        output = _run_git(
            ["diff", "--name-status", "--find-renames", "--diff-filter=ACMRD", f"{args.changed_against}...HEAD"]
        )
        return _parse_name_status(output)
    if args.paths:
        return [ChangeRecord(status="M", old_path=None, new_path=_normalize(path)) for path in args.paths]
    return []


def _describe_violation(path: str, area: ManagedArea) -> str:
    return (
        f"- {path}: matches archive-candidate pattern in {area.name} and is not under "
        f"{area.archive_dir} or the active allowlist"
    )


def command_check(args: argparse.Namespace) -> int:
    records = _get_change_records(args)
    violations: list[str] = []

    for record in records:
        for area in MANAGED_AREAS:
            if record.old_path and record.new_path and _is_candidate(record.old_path, area):
                if _path_in_archive(record.new_path, area):
                    continue
            if record.status.startswith("D") and record.new_path:
                if _is_candidate(record.new_path, area) and not _is_allowlisted(record.new_path, area):
                    violations.append(_describe_violation(record.new_path, area))
                continue
            current_path = record.new_path
            if not current_path:
                continue
            if _is_candidate(current_path, area) and not _is_allowlisted(current_path, area):
                violations.append(_describe_violation(current_path, area))

    if not violations:
        print("Archive hygiene check passed.")
        return 0

    print("Archive hygiene check found archive-candidate files outside approved active locations:")
    for violation in sorted(set(violations)):
        print(violation)
    print("Suggested action: move historical evidence into the appropriate archive folder or explicitly keep it active by updating the allowlist in scripts/archive_hygiene.py.")
    return 1 if args.enforce else 0


def _ensure_archive_root_readme(root_readme: Path, archive_root: str) -> None:
    if root_readme.exists():
        return
    root_readme.write_text(
        "# Archive Index\n\n"
        "## Purpose\n\n"
        "This folder stores historical artifacts that are no longer part of the active working set.\n\n"
        "## How to Use\n\n"
        "1. Move historical files into a dated folder such as `YYYY-MM/`.\n"
        "1. Add an entry to this index for each moved file or no-move sweep.\n"
        "1. Keep active controls and current baselines outside this archive.\n\n"
        "## Archive Entries\n\n"
        "Add entries here.\n",
        encoding="utf-8",
    )


def _ensure_batch_readme(batch_readme: Path, batch: str) -> None:
    if batch_readme.exists():
        return
    batch_readme.write_text(
        f"# Archive Batch {batch}\n\n"
        "## Scope\n\n"
        "Describe the historical files and sweep scope for this batch.\n\n"
        "## Files in This Batch\n\n"
        "- Add moved files here\n\n"
        "## Rationale\n\n"
        "Explain why the files were archived or why a no-move sweep was recorded.\n",
        encoding="utf-8",
    )


def command_scaffold(args: argparse.Namespace) -> int:
    archive_root = Path(args.archive_root)
    batch_dir = archive_root / args.batch
    note_path = batch_dir / args.note_name
    archive_root.mkdir(parents=True, exist_ok=True)
    batch_dir.mkdir(parents=True, exist_ok=True)
    _ensure_archive_root_readme(archive_root / "README.md", args.archive_root)
    _ensure_batch_readme(batch_dir / "README.md", args.batch)
    if note_path.exists():
        print(f"Archive note already exists: {note_path.as_posix()}")
        return 1
    note_path.write_text(
        f"# {args.title}\n\n"
        "## Purpose\n\n"
        "State why this sweep or archive batch was performed.\n\n"
        "## Files Moved In This Sweep\n\n"
        "- Add moved files here\n\n"
        "## Files Retained In Place\n\n"
        "- Add reviewed files that remain active\n\n"
        "## Required Follow-Up\n\n"
        "1. Update the archive root index with moved-file entries or a no-move sweep note.\n"
        "1. Update any active-folder README or checklist references that still point to pre-archive paths.\n"
        "1. Run markdownlint on the touched archive files and any updated references.\n",
        encoding="utf-8",
    )
    print(f"Created archive note template: {note_path.as_posix()}")
    print("Next steps:")
    print(f"- Update {archive_root.as_posix()}/README.md")
    print(f"- Update {batch_dir.as_posix()}/README.md")
    print(f"- Run: npx --yes markdownlint-cli {note_path.as_posix()} {batch_dir.as_posix()}/README.md {archive_root.as_posix()}/README.md")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Archive hygiene tooling.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check archive-candidate files in git changes.")
    source = check_parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--staged", action="store_true", help="Check staged changes.")
    source.add_argument("--upstream", action="store_true", help="Check changes relative to the current upstream branch.")
    source.add_argument("--changed-against", help="Check changes relative to the supplied git ref.")
    source.add_argument("--paths", nargs="+", help="Check the supplied paths.")
    check_parser.add_argument("--enforce", action="store_true", help="Return non-zero on violations.")
    check_parser.set_defaults(func=command_check)

    scaffold_parser = subparsers.add_parser("scaffold", help="Create an archive-batch note template.")
    scaffold_parser.add_argument("--archive-root", required=True, help="Archive root directory, for example planning/archives.")
    scaffold_parser.add_argument("--batch", required=True, help="Batch folder name, typically YYYY-MM.")
    scaffold_parser.add_argument("--note-name", required=True, help="Archive note filename.")
    scaffold_parser.add_argument("--title", required=True, help="Document title for the archive note.")
    scaffold_parser.set_defaults(func=command_scaffold)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

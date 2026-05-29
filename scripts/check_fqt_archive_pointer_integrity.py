#!/usr/bin/env python3
"""CI guard: prevent deleting archived FQT evidence without a matching pointer manifest."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ARCHIVE_PREFIX = "FQT/archive_dedup/"
POINTER_PREFIX = Path("FQT")
POINTER_NAME = "MANIFEST_POINTER.json"


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


def _deleted_or_moved_out_records(changed_against: str) -> list[str]:
    output = _run_git(["diff", "--name-status", "--find-renames", f"{changed_against}...HEAD"])
    candidate_paths: list[str] = []

    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]

        if status.startswith("D") and len(parts) >= 2:
            old_path = _normalize(parts[1])
            if old_path.startswith(ARCHIVE_PREFIX):
                candidate_paths.append(old_path)
            continue

        if (status.startswith("R") or status.startswith("C")) and len(parts) >= 3:
            old_path = _normalize(parts[1])
            new_path = _normalize(parts[2])
            # A rename/copy out of archive also counts as archive evidence removal.
            if old_path.startswith(ARCHIVE_PREFIX) and not new_path.startswith(ARCHIVE_PREFIX):
                candidate_paths.append(old_path)

    return candidate_paths


def _extract_run_name(archive_path: str) -> str | None:
    # Expected shape: FQT/archive_dedup/YYYY-MM-DD/<run_name>/...
    parts = archive_path.split("/")
    if len(parts) < 5:
        return None
    return parts[3]


def _pointer_exists(run_name: str) -> bool:
    pointer = POINTER_PREFIX / run_name / POINTER_NAME
    return pointer.exists() and pointer.is_file()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ensure archived evidence deletions preserve path-level pointer manifests."
    )
    parser.add_argument(
        "--changed-against",
        required=True,
        help="Git ref to diff against (for example origin/main).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    deleted_paths = _deleted_or_moved_out_records(args.changed_against)
    if not deleted_paths:
        print("FQT archive pointer integrity check passed: no archived evidence deletions detected.")
        return 0

    missing: list[str] = []
    checked_runs: set[str] = set()

    for archive_path in deleted_paths:
        run_name = _extract_run_name(archive_path)
        if not run_name:
            missing.append(f"{archive_path} (unable to parse run name)")
            continue
        if run_name in checked_runs:
            continue
        checked_runs.add(run_name)

        if not _pointer_exists(run_name):
            missing.append(f"{archive_path} -> expected pointer FQT/{run_name}/{POINTER_NAME}")

    if missing:
        print("FQT archive pointer integrity check failed.")
        print("Archived evidence is being removed without matching pointer manifests:")
        for item in missing:
            print(f"- {item}")
        return 1

    print(
        "FQT archive pointer integrity check passed: all archived evidence removals have matching pointer manifests."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

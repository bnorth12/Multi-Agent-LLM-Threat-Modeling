#!/usr/bin/env python3
"""Enforce Phase 3 hardening rules for the core traceability registry.

Checks:
1) Core table contains the `Audit Rationale` column and each row has a non-empty value.
2) Newly added core rows (vs --changed-against) satisfy promotion checklist gates.
3) Core rows reject wildcard/non-canonical IDs.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


REGISTRY_PATH = Path("Requirements/15_End_To_End_Traceability_Attributes_Registry.md")
CORE_HEADING = "## Core Registry Table"

WILDCARD_MARKERS = ("*", "?", "X", "TBD", "TODO", "UNKNOWN", "PLACEHOLDER")

SLICE_ID_RE = re.compile(r"^(?:S\d{2,3}-\d{3}|R\d{2}-\d{3})$")
CAPABILITY_ID_RE = re.compile(r"^C\d{2}-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
FUNCTION_ID_RE = re.compile(r"^F-[A-Z0-9_]+(?:-[A-Z0-9_]+)*$")
REQUIREMENT_ID_RE = re.compile(r"^(?:C\d{2}-[A-Z0-9]+(?:-[A-Z0-9]+)*|[A-Z]{2,}\d{0,2}-\d{2,4}[A-Z]?)$")


def _parse_table_cells(line: str) -> List[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator_row(line: str) -> bool:
    normalized = line.strip().replace("|", "").replace(":", "").replace("-", "")
    return normalized == ""


def _extract_core_table(md_text: str) -> Tuple[List[str], List[Dict[str, str]]]:
    lines = md_text.splitlines()
    start_idx = -1
    for idx, line in enumerate(lines):
        if line.strip() == CORE_HEADING:
            start_idx = idx
            break
    if start_idx == -1:
        raise ValueError(f"Missing heading: {CORE_HEADING}")

    table_lines: List[str] = []
    for line in lines[start_idx + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("## "):
            break
        if stripped.startswith("|"):
            table_lines.append(line)

    if len(table_lines) < 2:
        raise ValueError("Core registry table missing or incomplete")

    headers = _parse_table_cells(table_lines[0])
    rows: List[Dict[str, str]] = []
    for line in table_lines[1:]:
        if _is_separator_row(line):
            continue
        values = _parse_table_cells(line)
        if len(values) != len(headers):
            raise ValueError(f"Malformed table row (expected {len(headers)} cols): {line}")
        rows.append(dict(zip(headers, values)))
    return headers, rows


def _load_current_rows() -> Tuple[List[str], List[Dict[str, str]]]:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Missing registry file: {REGISTRY_PATH}")
    return _extract_core_table(REGISTRY_PATH.read_text(encoding="utf-8", errors="ignore"))


def _load_old_rows(changed_against: str) -> List[Dict[str, str]]:
    try:
        result = subprocess.run(
            ["git", "show", f"{changed_against}:{REGISTRY_PATH.as_posix()}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return []

    if result.returncode != 0:
        return []

    try:
        _, rows = _extract_core_table(result.stdout)
        return rows
    except Exception:
        return []


def _row_key(row: Dict[str, str]) -> Tuple[str, str, str, str]:
    return (
        row.get("Slice ID", ""),
        row.get("Capability ID", ""),
        row.get("Function ID", ""),
        row.get("Requirement ID", ""),
    )


def _contains_wildcard_or_placeholder(value: str) -> bool:
    upper = value.upper()
    return any(marker in upper for marker in WILDCARD_MARKERS)


def _validate_canonical_ids(row: Dict[str, str], errors: List[str], prefix: str) -> None:
    slice_id = row.get("Slice ID", "")
    capability_id = row.get("Capability ID", "")
    function_id = row.get("Function ID", "")
    requirement_id = row.get("Requirement ID", "")

    if not SLICE_ID_RE.fullmatch(slice_id):
        errors.append(f"{prefix}: non-canonical Slice ID '{slice_id}'")
    if not CAPABILITY_ID_RE.fullmatch(capability_id):
        errors.append(f"{prefix}: non-canonical Capability ID '{capability_id}'")
    if not FUNCTION_ID_RE.fullmatch(function_id):
        errors.append(f"{prefix}: non-canonical Function ID '{function_id}'")
    if not REQUIREMENT_ID_RE.fullmatch(requirement_id):
        errors.append(f"{prefix}: non-canonical Requirement ID '{requirement_id}'")

    for field_name in ("Slice ID", "Capability ID", "Function ID", "Requirement ID"):
        value = row.get(field_name, "")
        if _contains_wildcard_or_placeholder(value):
            errors.append(f"{prefix}: wildcard/placeholder token in {field_name} '{value}'")


def _validate_audit_rationale(headers: Sequence[str], rows: Sequence[Dict[str, str]], errors: List[str]) -> None:
    if "Audit Rationale" not in headers:
        errors.append("Core table is missing required 'Audit Rationale' column")
        return

    for idx, row in enumerate(rows, start=1):
        value = row.get("Audit Rationale", "").strip()
        if not value:
            errors.append(f"Row {idx} ({_row_key(row)}): missing Audit Rationale value")


def _validate_promotion_checklist_for_new_rows(
    new_rows: Sequence[Dict[str, str]],
    errors: List[str],
) -> None:
    for row in new_rows:
        key = _row_key(row)
        prefix = f"New row {key}"

        _validate_canonical_ids(row, errors, prefix)

        architecture = row.get("Architecture Artifact", "")
        design = row.get("Design Artifact", "")
        source = row.get("Source File Path", "")
        verification = row.get("Verification Artifact", "")
        test_artifact_id = row.get("Test Artifact ID", "")
        missing_legs = row.get("Missing Legs", "")
        process_failure = row.get("Process Failure", "")
        remediation = row.get("Remediation Action", "")
        rationale = row.get("Audit Rationale", "")

        if "planning/" in architecture.lower() or "planning/" in design.lower():
            errors.append(f"{prefix}: architecture/design anchors must be stable (no planning/*)")

        if not (
            source.startswith("src/")
            or source.startswith("frontend/")
            or source.startswith("scripts/")
        ):
            errors.append(
                f"{prefix}: Source File Path must be source-based (src/, frontend/, scripts/), got '{source}'"
            )

        if not verification.strip():
            errors.append(f"{prefix}: Verification Artifact is required")
        if not test_artifact_id.startswith("TST-"):
            errors.append(f"{prefix}: Test Artifact ID must start with 'TST-', got '{test_artifact_id}'")

        if missing_legs.strip().lower() != "none":
            errors.append(f"{prefix}: Missing Legs must be 'none', got '{missing_legs}'")
        if process_failure.strip().lower() != "no":
            errors.append(f"{prefix}: Process Failure must be 'no', got '{process_failure}'")
        if remediation.strip().lower() != "none":
            errors.append(f"{prefix}: Remediation Action must be 'none', got '{remediation}'")
        if not rationale.strip():
            errors.append(f"{prefix}: Audit Rationale is required")


def _write_report(
    report_json: str | None,
    changed_against: str | None,
    row_count: int,
    new_rows: Sequence[Dict[str, str]],
    errors: Sequence[str],
) -> None:
    if not report_json:
        return

    report_path = Path(report_json)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "fail" if errors else "pass",
        "changed_against": changed_against or "",
        "rows_scanned": row_count,
        "new_rows_count": len(new_rows),
        "new_rows": [
            {
                "slice_id": row.get("Slice ID", ""),
                "capability_id": row.get("Capability ID", ""),
                "function_id": row.get("Function ID", ""),
                "requirement_id": row.get("Requirement ID", ""),
            }
            for row in new_rows
        ],
        "errors": list(errors),
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run(changed_against: str | None, report_json: str | None) -> int:
    headers, current_rows = _load_current_rows()
    errors: List[str] = []

    # Rule 1: Audit rationale column/value presence for all core rows.
    _validate_audit_rationale(headers, current_rows, errors)

    # Rule 3: Global wildcard/non-canonical rejection for core IDs.
    for row in current_rows:
        _validate_canonical_ids(row, errors, prefix=f"Core row {_row_key(row)}")

    # Rule 2: Promotion checklist compliance for rows newly added to core.
    old_rows = _load_old_rows(changed_against) if changed_against else []
    old_keys = {_row_key(r) for r in old_rows}
    new_rows = [r for r in current_rows if _row_key(r) not in old_keys]
    if changed_against:
        _validate_promotion_checklist_for_new_rows(new_rows, errors)

    _write_report(
        report_json=report_json,
        changed_against=changed_against,
        row_count=len(current_rows),
        new_rows=new_rows,
        errors=errors,
    )

    if errors:
        print("[FAIL] Core registry hardening checks failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("[PASS] Core registry hardening checks passed")
    print(f"[INFO] Rows scanned: {len(current_rows)}")
    if changed_against:
        print(f"[INFO] Newly added rows vs {changed_against}: {len(new_rows)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify core registry hardening checks")
    parser.add_argument(
        "--changed-against",
        default="",
        help="Git ref for diff-aware new-row checks (e.g., origin/main or HEAD~1)",
    )
    parser.add_argument(
        "--report-json",
        default="",
        help="Optional path to write machine-readable JSON report",
    )
    args = parser.parse_args()
    return run(
        changed_against=args.changed_against.strip() or None,
        report_json=args.report_json.strip() or None,
    )


if __name__ == "__main__":
    sys.exit(main())

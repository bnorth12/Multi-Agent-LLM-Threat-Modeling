#!/usr/bin/env python3
"""Verify sprint issues are reflected in base architecture/design documentation.

This guard prevents trace-only updates by requiring capability/function and requirement
coverage in baseline architecture/design authorities.
"""

from __future__ import annotations

import re
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Set

from sprint_naming import parse_sprint_token

REQ_ID_PATTERN = re.compile(r"\b([A-Z]{2,}-\d+[A-Z]?)\b")
ACTIVE_STATUS_MARKERS = ("in progress", "in review", "open", "active")
EXCLUDED_STATUS_MARKERS = ("proposed", "defer", "deferred", "closed", "resolved", "complete", "completed")
ARCH_REQ_PREFIXES = {"GUI", "HITL", "INT", "ORCH", "PRJ", "RHMI", "RIC", "C"}
FIELDS = {
    "Parent Capability ID": re.compile(r"(?im)^\s*Parent Capability ID\s*:\s*(.+)$"),
    "Child Function ID": re.compile(r"(?im)^\s*Child Function ID\s*:\s*(.+)$"),
}

CAPABILITY_BASELINE = Path("docs/architecture/Capability_Hierarchy_Baseline.md")
FUNCTION_REGISTRY = Path("docs/architecture/Function_Hierarchy_Registry.md")
CAP_FUNC_MATRIX = Path("docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md")
HMI_BLUEPRINT = Path("docs/architecture/HMI_Architecture_Blueprint.md")
RUNTIME_DESIGN = Path("docs/design/software/Runtime_And_Orchestration_Design_Specification.md")
FLOW_PACKAGE = Path("docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md")


def sprint_issue_files(sprint_us: str, sprint_dash: str) -> List[Path]:
    issues_dir = Path("planning/issues")
    if not issues_dir.exists():
        return []
    files = set(issues_dir.glob(f"issue_{sprint_us}_*.md"))
    files.update(issues_dir.glob(f"issue_{sprint_dash}_*.md"))
    return sorted(files)


def extract_related_requirement_ids(text: str) -> Set[str]:
    section_match = re.search(r"(?ims)^##\s*related requirements\s*$\n(?P<body>.*?)(?:^##\s|\Z)", text)
    body = section_match.group("body") if section_match else text
    ids = set(REQ_ID_PATTERN.findall(body))
    filtered = {rid for rid in ids if not rid.startswith("S") and not rid.startswith("D-S")}
    return {
        rid
        for rid in filtered
        if rid.split("-", 1)[0] in ARCH_REQ_PREFIXES
    }


def issue_is_active(text: str) -> bool:
    lowered = text.lower()
    match = re.search(r"(?im)^\s*status\s*:\s*(.+)$", lowered)
    if not match:
        return True
    status_text = match.group(1)
    if any(token in status_text for token in EXCLUDED_STATUS_MARKERS):
        return False
    if any(token in status_text for token in ACTIVE_STATUS_MARKERS):
        return True
    return True


def extract_field(text: str, field: str) -> str:
    pattern = FIELDS[field]
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def main() -> int:
    parser = ArgumentParser(description="Verify architecture/design baseline coverage for sprint issues")
    parser.add_argument("--sprint", required=True, help="Sprint token (YYYY_NN or YYYY-NN)")
    args = parser.parse_args()

    token = parse_sprint_token(args.sprint)
    issues = sprint_issue_files(token.underscore, token.dash)
    if not issues:
        print(f"[arch-baseline] INFO: no issue files found for sprint {token.underscore}")
        return 0

    capability_text = load_text(CAPABILITY_BASELINE)
    function_text = load_text(FUNCTION_REGISTRY)
    matrix_text = load_text(CAP_FUNC_MATRIX)
    design_authority_text = "\n".join([
        load_text(HMI_BLUEPRINT),
        load_text(RUNTIME_DESIGN),
        load_text(FLOW_PACKAGE),
    ])

    warnings: List[str] = []

    for issue_file in issues:
        text = load_text(issue_file)
        if not issue_is_active(text):
            continue
        cap_id = extract_field(text, "Parent Capability ID")
        func_id = extract_field(text, "Child Function ID")
        req_ids = extract_related_requirement_ids(text)

        label = issue_file.name
        if cap_id and cap_id not in capability_text:
            warnings.append(f"{label}: Parent Capability ID '{cap_id}' is not present in {CAPABILITY_BASELINE.as_posix()}")
        if func_id and func_id not in function_text:
            warnings.append(f"{label}: Child Function ID '{func_id}' is not present in {FUNCTION_REGISTRY.as_posix()}")
        if func_id and func_id not in matrix_text:
            warnings.append(f"{label}: Child Function ID '{func_id}' is not present in {CAP_FUNC_MATRIX.as_posix()}")

        if req_ids:
            if not any(req_id in design_authority_text for req_id in req_ids):
                warnings.append(
                    f"{label}: none of related requirement IDs {sorted(req_ids)} appear in base architecture/design docs"
                )

    if warnings:
        print("[arch-baseline] FAIL: baseline architecture/design coverage gaps found")
        for item in warnings:
            print(f"[arch-baseline] WARN: {item}")
        return 1

    print(f"[arch-baseline] PASS: base architecture/design coverage verified for sprint {token.underscore}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify that active sprint issues cover required architecture/design document families.

This guard prevents narrow architecture updates by requiring each active issue to
target document families based on the related requirement prefixes.
"""

from __future__ import annotations

import re
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Set

from sprint_naming import parse_sprint_token

REQ_ID_PATTERN = re.compile(r"\b([A-Z]{2,}-\d+[A-Z]?)\b")
ACTIVE_STATUS_MARKERS = ("in progress", "in review", "open", "active")
EXCLUDED_STATUS_MARKERS = ("proposed", "defer", "deferred", "closed", "resolved", "complete", "completed")

DOC_FAMILIES: Dict[str, List[Path]] = {
    "baseline-hierarchy": [
        Path("docs/architecture/Capability_Hierarchy_Baseline.md"),
        Path("docs/architecture/Function_Hierarchy_Registry.md"),
        Path("docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md"),
    ],
    "hmi-architecture": [
        Path("docs/architecture/HMI_Architecture_Blueprint.md"),
        Path("docs/architecture/Multi_Agent_Function_And_Interface_Requirements_Matrix.md"),
        Path("docs/architecture/Multi_Agent_Interface_Control_Document.md"),
    ],
    "agent-architecture": [
        Path("docs/architecture/Multi_Agent_Logical_Decomposition.md"),
        Path("docs/architecture/Multi_Agent_Structural_Decomposition.md"),
        Path("docs/architecture/Multi_Agent_Functional_Decomposition.md"),
        Path("docs/architecture/Multi_Agent_Architecture_Decomposition_Package.md"),
    ],
    "runtime-design": [
        Path("docs/design/software/Runtime_And_Orchestration_Design_Specification.md"),
        Path("docs/design/software/Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md"),
        Path("docs/design/software/Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md"),
    ],
    "agent-design": [
        Path("docs/design/software/Agent_Subsystem_Design_Specification.md"),
    ],
    "interface-design": [
        Path("docs/design/system/External_Interface_And_Integration_Design_Package.md"),
    ],
    "flow-design": [
        Path("docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md"),
    ],
}

REQ_PREFIX_TO_FAMILIES: Dict[str, Set[str]] = {
    "ORCH": {"baseline-hierarchy", "agent-architecture", "runtime-design", "flow-design"},
    "INT": {"baseline-hierarchy", "hmi-architecture", "interface-design", "flow-design"},
    "GUI": {"baseline-hierarchy", "hmi-architecture", "interface-design", "flow-design"},
    "HITL": {"hmi-architecture", "runtime-design", "flow-design"},
    "RHMI": {"hmi-architecture", "interface-design", "flow-design"},
    "PRJ": {"baseline-hierarchy", "agent-architecture", "runtime-design", "interface-design", "agent-design", "flow-design"},
    "RIC": {"runtime-design", "flow-design"},
    "C": {"baseline-hierarchy", "agent-architecture", "runtime-design", "flow-design"},
}


def sprint_issue_files(sprint_us: str, sprint_dash: str) -> List[Path]:
    issues_dir = Path("planning/issues")
    if not issues_dir.exists():
        return []
    files = set(issues_dir.glob(f"issue_{sprint_us}_*.md"))
    files.update(issues_dir.glob(f"issue_{sprint_dash}_*.md"))
    return sorted(files)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


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


def extract_related_requirement_ids(text: str) -> Set[str]:
    section_match = re.search(r"(?ims)^##\s*related requirements\s*$\n(?P<body>.*?)(?:^##\s|\Z)", text)
    body = section_match.group("body") if section_match else text
    ids = set(REQ_ID_PATTERN.findall(body))
    return {rid for rid in ids if not rid.startswith("S") and not rid.startswith("D-S")}


def extract_allocated_module(text: str) -> str:
    match = re.search(r"(?im)^\s*Allocated Component/Module\s*:\s*(.+)$", text)
    if not match:
        return ""
    return match.group(1).strip()


def extract_remediation_targets(text: str) -> Set[str]:
    section_match = re.search(r"(?ims)^##\s*remediation targets\s*$\n(?P<body>.*?)(?:^##\s|\Z)", text)
    if not section_match:
        return set()

    targets: Set[str] = set()
    for line in section_match.group("body").splitlines():
        cleaned = line.strip()
        if not cleaned.startswith("-"):
            continue
        value = cleaned.lstrip("-").strip()
        if not value:
            continue
        targets.add(value)
    return targets


def families_for_requirements(requirement_ids: Set[str]) -> Set[str]:
    families: Set[str] = set()
    for rid in requirement_ids:
        prefix = rid.split("-", 1)[0]
        families.update(REQ_PREFIX_TO_FAMILIES.get(prefix, {"baseline-hierarchy", "flow-design"}))
    return families


def any_family_targeted(targets: Set[str], family_paths: List[Path]) -> bool:
    normalized = {item.replace("\\", "/") for item in targets}
    family_strings = {path.as_posix() for path in family_paths}
    return any(item in family_strings for item in normalized)


def family_has_requirement_evidence(family_paths: List[Path], requirement_ids: Set[str]) -> bool:
    if not requirement_ids:
        return True
    for path in family_paths:
        text = load_text(path)
        if any(rid in text for rid in requirement_ids):
            return True
    return False


def main() -> int:
    parser = ArgumentParser(description="Verify architecture/design document-family coverage for sprint issues")
    parser.add_argument("--sprint", required=True, help="Sprint token (YYYY_NN or YYYY-NN)")
    args = parser.parse_args()

    token = parse_sprint_token(args.sprint)
    issues = sprint_issue_files(token.underscore, token.dash)
    if not issues:
        print(f"[arch-surface] INFO: no issue files found for sprint {token.underscore}")
        return 0

    warnings: List[str] = []

    for issue_file in issues:
        text = load_text(issue_file)
        if not issue_is_active(text):
            continue

        req_ids = extract_related_requirement_ids(text)
        required_families = families_for_requirements(req_ids)
        if not required_families:
            continue

        targets = extract_remediation_targets(text)
        allocated = extract_allocated_module(text)
        if allocated:
            targets.add(allocated)

        label = issue_file.name
        for family in sorted(required_families):
            family_paths = DOC_FAMILIES.get(family, [])
            if not family_paths:
                continue

            if not any_family_targeted(targets, family_paths):
                warnings.append(
                    f"{label}: missing remediation target for document family '{family}'"
                )

            if not family_has_requirement_evidence(family_paths, req_ids):
                warnings.append(
                    f"{label}: none of related requirement IDs {sorted(req_ids)} appear in document family '{family}'"
                )

    if warnings:
        print("[arch-surface] FAIL: architecture/design document-family coverage gaps found")
        for item in warnings:
            print(f"[arch-surface] WARN: {item}")
        return 1

    print(f"[arch-surface] PASS: document-family coverage verified for sprint {token.underscore}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

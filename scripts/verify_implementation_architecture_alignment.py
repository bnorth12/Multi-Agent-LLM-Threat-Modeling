#!/usr/bin/env python3
"""Verify changed implementation surfaces are aligned with architecture/design targets.

This guard blocks implementation deltas when active sprint issues do not target the
 required architecture/design document families for the impacted surface.
"""

from __future__ import annotations

import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Set

from sprint_naming import parse_sprint_token

REQ_ID_PATTERN = re.compile(r"\b([A-Z]{2,}-\d+[A-Z]?)\b")
ACTIVE_STATUS_MARKERS = ("in progress", "in review", "open", "active")
EXCLUDED_STATUS_MARKERS = ("proposed", "defer", "deferred", "closed", "resolved", "complete", "completed")

DOC_FAMILIES: Dict[str, List[Path]] = {
    "hmi-architecture": [
        Path("docs/architecture/HMI_Architecture_Blueprint.md"),
        Path("docs/architecture/Multi_Agent_Function_And_Interface_Requirements_Matrix.md"),
        Path("docs/architecture/Multi_Agent_Interface_Control_Document.md"),
    ],
    "agent-architecture": [
        Path("docs/architecture/Multi_Agent_Logical_Decomposition.md"),
        Path("docs/architecture/Multi_Agent_Structural_Decomposition.md"),
    ],
    "runtime-design": [
        Path("docs/design/software/Runtime_And_Orchestration_Design_Specification.md"),
        Path("docs/design/software/Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md"),
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
        if value:
            targets.add(value)
    return targets


def changed_implementation_files(repo_root: Path) -> Set[str]:
    commands = [
        ["git", "diff", "--name-only", "HEAD", "--", "src", "frontend"],
        ["git", "diff", "--cached", "--name-only", "--", "src", "frontend"],
    ]
    changed: Set[str] = set()

    for command in commands:
        proc = subprocess.run(command, cwd=str(repo_root), text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            continue
        for line in proc.stdout.splitlines():
            item = line.strip().replace("\\", "/")
            if item:
                changed.add(item)
    return changed


def families_for_changed_files(paths: Set[str]) -> Dict[str, Set[str]]:
    family_to_paths: Dict[str, Set[str]] = {}
    for path in sorted(paths):
        families: Set[str] = set()
        if path.startswith("frontend/"):
            families.update({"hmi-architecture", "interface-design", "flow-design"})
        if path.startswith("src/threat_modeler/backend/") or path.startswith("src/threat_modeler/server/"):
            families.update({"runtime-design", "interface-design", "flow-design"})
        if path.startswith("src/threat_modeler/orchestrator"):
            families.update({"runtime-design", "agent-architecture", "flow-design"})
        if path.startswith("src/threat_modeler/agents/"):
            families.update({"agent-design", "agent-architecture", "flow-design"})
        if path.startswith("src/threat_modeler/ui/"):
            families.update({"hmi-architecture", "interface-design", "flow-design"})

        for family in families:
            family_to_paths.setdefault(family, set()).add(path)
    return family_to_paths


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
    parser = ArgumentParser(description="Verify implementation-to-architecture/design alignment for sprint")
    parser.add_argument("--sprint", required=True, help="Sprint token (YYYY_NN or YYYY-NN)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    token = parse_sprint_token(args.sprint)
    issues = sprint_issue_files(token.underscore, token.dash)
    if not issues:
        print(f"[impl-align] INFO: no issue files found for sprint {token.underscore}")
        return 0

    changed = changed_implementation_files(repo_root)
    impacted = families_for_changed_files(changed)
    if not impacted:
        print("[impl-align] PASS: no changed implementation files detected for guarded surfaces")
        return 0

    active_targets: Set[str] = set()
    active_requirements: Set[str] = set()
    for issue_file in issues:
        text = load_text(issue_file)
        if not issue_is_active(text):
            continue
        active_requirements.update(extract_related_requirement_ids(text))
        active_targets.update(extract_remediation_targets(text))
        allocated = extract_allocated_module(text)
        if allocated:
            active_targets.add(allocated)

    warnings: List[str] = []
    for family, changed_paths in sorted(impacted.items()):
        family_paths = DOC_FAMILIES.get(family, [])
        if not family_paths:
            continue

        if not any_family_targeted(active_targets, family_paths):
            warnings.append(
                "changed implementation files "
                f"{sorted(changed_paths)} require document family '{family}' to be targeted in active sprint issue remediation"
            )

        if not family_has_requirement_evidence(family_paths, active_requirements):
            warnings.append(
                "active sprint related requirements "
                f"{sorted(active_requirements)} have no evidence in required document family '{family}'"
            )

    if warnings:
        print("[impl-align] FAIL: implementation-to-architecture/design alignment gaps found")
        for item in warnings:
            print(f"[impl-align] WARN: {item}")
        return 1

    print("[impl-align] PASS: implementation-to-architecture/design alignment verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

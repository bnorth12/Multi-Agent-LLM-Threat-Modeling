#!/usr/bin/env python3
"""Verify administration governance controls tied to ADM-001..ADM-006."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CONTROLS = {
    "ADM-001": {
        "file": "Requirements/08_Feature_Branch_Checklist_Template.md",
        "tokens": [
            "Branch is linked to at least one planning issue.",
        ],
    },
    "ADM-002": {
        "file": "Requirements/08_Feature_Branch_Checklist_Template.md",
        "tokens": [
            "PR references related issue IDs.",
            "Related issue status is updated for merge readiness.",
        ],
    },
    "ADM-003": {
        "file": "Requirements/07_Release_Process.md",
        "tokens": [
            "Confirm each feature branch has a completed checklist artifact.",
            "Every included feature branch has a completed checklist artifact.",
        ],
    },
    "ADM-004": {
        "file": "Requirements/07_Release_Process.md",
        "tokens": [
            "Checklist bundle archived with release artifacts.",
        ],
    },
    "ADM-005": {
        "file": "Requirements/07_Release_Process.md",
        "tokens": [
            "Conduct Release Readiness Review",
            "Review checklist completion status for all included branches.",
        ],
    },
    "ADM-006": {
        "file": "Requirements/06_Project_Administration_Requirements.md",
        "tokens": [
            "schedule recurring backlog, branch, and release sync reviews at defined cadence",
        ],
    },
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def evaluate_controls(repo_root: Path) -> Dict[str, List[str]]:
    missing_by_control: Dict[str, List[str]] = {}
    for control_id, spec in REQUIRED_CONTROLS.items():
        target = repo_root / spec["file"]
        if not target.exists():
            missing_by_control[control_id] = [f"missing file: {spec['file']}"]
            continue

        text = read_text(target)
        missing_tokens = [token for token in spec["tokens"] if token not in text]
        if missing_tokens:
            missing_by_control[control_id] = missing_tokens

    return missing_by_control


def main() -> int:
    missing = evaluate_controls(REPO_ROOT)
    if missing:
        print("[adm-controls] FAIL: required administration controls are missing")
        for control_id in sorted(missing):
            print(f"- {control_id}")
            for item in missing[control_id]:
                print(f"  - missing token: {item}")
        return 1

    print("[adm-controls] PASS: ADM-001..ADM-006 governance controls verified")
    for control_id, spec in sorted(REQUIRED_CONTROLS.items()):
        print(f"- {control_id}: {spec['file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

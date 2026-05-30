#!/usr/bin/env python3
"""Build a simple dependency-aware multi-sprint portfolio staging note."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from sprint_naming import increment_sprint_token as increment_sprint_name
from sprint_naming import parse_sprint_token


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "independent_reviews" / "latest"
DEFAULT_SNAPSHOT_INDEX = REPO_ROOT / "independent_reviews" / "history" / "snapshot_index.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_sprint(sprint: str) -> str:
    return parse_sprint_token(sprint).dash


def increment_sprint_token(sprint: str, offset: int) -> str:
    return increment_sprint_name(sprint, offset, separator="_")


def discover_planning_doc(sprint: str) -> Path:
    candidates = [
        REPO_ROOT / "planning" / f"Sprint_{sprint}_Planning.md",
        REPO_ROOT / "planning" / f"Sprint_{sprint}_Remediation_Restart_Manifest.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def summarize_restart_manifest(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None

    phase_counts: Dict[str, int] = {}
    requirement_ids: List[str] = []
    issue_ids: List[str] = []

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not re.match(r"^\|\s*R\d{2}-\d{3}\s*\|", line):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 3:
            continue
        issue_id = cells[0]
        phase = cells[1]
        requirement_id = cells[2]
        issue_ids.append(issue_id)
        requirement_ids.append(requirement_id)
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "status": "ready",
        "total_items": len(issue_ids),
        "phase_counts": phase_counts,
        "issue_ids": issue_ids,
        "requirement_ids": requirement_ids,
    }


def latest_kpi_score(snapshot_index: List[Dict[str, Any]], sprint: str) -> Dict[str, Any]:
    normalized = normalize_sprint(sprint)
    filtered = [row for row in snapshot_index if str(row.get("sprint", "")) == normalized]
    source = filtered if filtered else snapshot_index
    latest = source[-1] if source else {}
    return {
        "source_count": len(source),
        "latest_timestamp": latest.get("timestamp"),
        "latest_score": float(latest.get("score", 0.0)),
        "full_chain_ratio": float(latest.get("full_chain_ratio", 0.0)),
        "issue_quality_ratio": float(latest.get("issue_quality_ratio", 0.0)),
        "critical_count": int(latest.get("critical_count", 0)),
        "major_count": int(latest.get("major_count", 0)),
    }


def read_plan_excerpt(path: Path, max_lines: int = 4) -> str:
    if not path.exists():
        return "missing"
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    return " | ".join(lines[:max_lines]) if lines else "empty"


def build_plan(sprint: str, snapshot_index: List[Dict[str, Any]]) -> Dict[str, Any]:
    sprint_token = parse_sprint_token(sprint)
    sprint_us = sprint_token.underscore
    current = latest_kpi_score(snapshot_index, sprint_us)
    next_sprint = increment_sprint_token(sprint_us, 1)
    parking_lot_sprint = "2026_99"

    planning_doc = discover_planning_doc(sprint_us)
    next_planning_doc = discover_planning_doc(next_sprint)
    closeout_doc = REPO_ROOT / "planning" / f"Sprint_{sprint_us}_Closure_Checklist.md"
    next_skills_doc = REPO_ROOT / "planning" / f"Sprint_{parking_lot_sprint}_Parking_Lot_Skills_Layer_and_Avionics_Specialization.md"
    concept_doc = REPO_ROOT / "planning" / f"Sprint_{parking_lot_sprint}_Parking_Lot_Threat_Model_Abstractions_and_Compositional_Flows.md"
    restart_manifest = summarize_restart_manifest(REPO_ROOT / "planning" / f"Sprint_{sprint_us}_Remediation_Restart_Manifest.md")

    risk_level = "low"
    if current["latest_score"] < 45:
        risk_level = "high"
    elif current["latest_score"] < 60:
        risk_level = "moderate"

    gates = [
        {
            "sprint": sprint_us,
            "gate": "execution-plan",
            "document": str(planning_doc.relative_to(REPO_ROOT)),
            "status": "ready" if planning_doc.exists() else "missing",
            "excerpt": read_plan_excerpt(planning_doc),
        },
        {
            "sprint": next_sprint,
            "gate": "carryover-plan",
            "document": str(next_planning_doc.relative_to(REPO_ROOT)),
            "status": "ready" if next_planning_doc.exists() else "missing",
            "excerpt": read_plan_excerpt(next_planning_doc),
        },
        {
            "sprint": parking_lot_sprint,
            "gate": "skills-parking-lot",
            "document": str(next_skills_doc.relative_to(REPO_ROOT)),
            "status": "ready" if next_skills_doc.exists() else "missing",
            "excerpt": read_plan_excerpt(next_skills_doc),
        },
        {
            "sprint": parking_lot_sprint,
            "gate": "concept-parking-lot",
            "document": str(concept_doc.relative_to(REPO_ROOT)),
            "status": "ready" if concept_doc.exists() else "missing",
            "excerpt": read_plan_excerpt(concept_doc),
        },
    ]

    return {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": sprint_us,
        "current_health": current,
        "risk_level": risk_level,
        "planning_doc": {
            "path": str(planning_doc.relative_to(REPO_ROOT)),
            "status": "ready" if planning_doc.exists() else "missing",
            "excerpt": read_plan_excerpt(planning_doc),
        },
        "restart_manifest": restart_manifest,
        "portfolio_sequence": [sprint_us, next_sprint, parking_lot_sprint],
        "gates": gates,
        "governance_checkpoints": [
            "Use the remediation restart manifest as the portfolio intake source before generating issue trackers.",
            "Allocate every manifest item into an execution sprint before remediation implementation begins.",
            "Hold current sprint closeout until the current sprint evidence bundle is certified or conditionally certified.",
            "Treat 2026_99 as a parking-lot lane for non-remediation work so speculative scope does not collide with remediation execution.",
        ],
    }


def write_report(out_dir: Path, result: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = REPO_ROOT / "independent_reviews" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "multi_sprint_portfolio_plan_latest.json"
    md_path = out_dir / "multi_sprint_portfolio_plan_latest.md"
    history_path = history_dir / "multi_sprint_portfolio_plan.jsonl"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    md_lines = [
        "# Multi-Sprint Portfolio Plan",
        "",
        f"- Generated: {result['generated_at']}",
        f"- Sprint: {result['sprint']}",
        f"- Risk Level: {result['risk_level']}",
        f"- Latest Health: {float(result['current_health'].get('latest_score', 0.0)):.1f}%",
        f"- Current Full-Chain Ratio: {float(result['current_health'].get('full_chain_ratio', 0.0)):.3f}",
        f"- Current Issue Quality Ratio: {float(result['current_health'].get('issue_quality_ratio', 0.0)):.3f}",
        "",
        "## Intake Source",
    ]
    restart_manifest = result.get("restart_manifest")
    if restart_manifest:
        md_lines.extend(
            [
                f"- Manifest: {restart_manifest['path']}",
                f"- Total items: {restart_manifest['total_items']}",
                f"- Phase counts: {json.dumps(restart_manifest['phase_counts'], sort_keys=True)}",
                "",
            ]
        )
    else:
        md_lines.extend(["- Restart manifest: not found", ""])
    md_lines.extend([
        "## Planned Gates",
    ])
    for gate in result["gates"]:
        md_lines.extend(
            [
                f"- {gate['sprint']} / {gate['gate']} / {gate['status']}",
                f"  document: {gate['document']}",
                f"  excerpt: {gate['excerpt']}",
            ]
        )
    md_lines.extend(["", "## Governance Checkpoints"])
    md_lines.extend([f"- {checkpoint}" for checkpoint in result["governance_checkpoints"]])
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    with history_path.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps(result))
        history_file.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a multi-sprint portfolio staging plan")
    parser.add_argument("--sprint", default="2026_12", help="Sprint identifier (YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN)")
    parser.add_argument("--snapshot-index", default=str(DEFAULT_SNAPSHOT_INDEX))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot_index)
    if not snapshot_path.exists():
        print(f"ERROR: snapshot index not found: {snapshot_path}")
        return 2

    snapshot_index = load_json(snapshot_path)
    result = build_plan(args.sprint, snapshot_index)
    write_report(Path(args.out_dir), result)

    print("Multi-sprint portfolio planning complete")
    print(f"- sprint: {args.sprint}")
    print(f"- risk level: {result['risk_level']}")
    print(f"- sequence: {', '.join(result['portfolio_sequence'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

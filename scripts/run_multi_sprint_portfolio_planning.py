#!/usr/bin/env python3
"""Build a simple dependency-aware multi-sprint portfolio staging note."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "local_reviews" / "latest"
DEFAULT_SNAPSHOT_INDEX = REPO_ROOT / "local_reviews" / "history" / "snapshot_index.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_sprint(sprint: str) -> str:
    return sprint.replace("_", "-")


def increment_sprint_token(sprint: str, offset: int) -> str:
    year, suffix = sprint.split("_", 1)
    return f"{year}_{int(suffix) + offset:02d}"


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
    current = latest_kpi_score(snapshot_index, sprint)
    next_sprint = increment_sprint_token(sprint, 1)
    next_next_sprint = increment_sprint_token(sprint, 2)

    planning_doc = REPO_ROOT / "planning" / f"Sprint_{sprint}_Planning.md"
    closeout_doc = REPO_ROOT / "planning" / f"Sprint_{sprint}_Closure_Checklist.md"
    next_skills_doc = REPO_ROOT / "planning" / f"Sprint_{next_sprint}_Skills_Layer_and_Avionics_Specialization.md"
    concept_doc = REPO_ROOT / "planning" / f"Sprint_{next_next_sprint}_Concept_Review_Threat_Model_Abstractions_and_Compositional_Flows.md"

    risk_level = "low"
    if current["latest_score"] < 45:
        risk_level = "high"
    elif current["latest_score"] < 60:
        risk_level = "moderate"

    gates = [
        {
            "sprint": sprint,
            "gate": "closeout",
            "document": str(closeout_doc.relative_to(REPO_ROOT)),
            "status": "ready" if closeout_doc.exists() else "missing",
            "excerpt": read_plan_excerpt(closeout_doc),
        },
        {
            "sprint": next_sprint,
            "gate": "skills-layer",
            "document": str(next_skills_doc.relative_to(REPO_ROOT)),
            "status": "ready" if next_skills_doc.exists() else "missing",
            "excerpt": read_plan_excerpt(next_skills_doc),
        },
        {
            "sprint": next_next_sprint,
            "gate": "concept-review",
            "document": str(concept_doc.relative_to(REPO_ROOT)),
            "status": "ready" if concept_doc.exists() else "missing",
            "excerpt": read_plan_excerpt(concept_doc),
        },
    ]

    return {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": sprint,
        "current_health": current,
        "risk_level": risk_level,
        "planning_doc": {
            "path": str(planning_doc.relative_to(REPO_ROOT)),
            "status": "ready" if planning_doc.exists() else "missing",
            "excerpt": read_plan_excerpt(planning_doc),
        },
        "portfolio_sequence": [gate["sprint"] for gate in gates],
        "gates": gates,
        "governance_checkpoints": [
            "Hold closeout until the current sprint evidence bundle is certified or conditionally certified.",
            "Advance the next sprint only after the skills-layer specialization doc is ready.",
            "Use the concept review as the runway guard before any broader portfolio expansion.",
        ],
    }


def write_report(out_dir: Path, result: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = REPO_ROOT / "local_reviews" / "history"
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
        "## Planned Gates",
    ]
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
    parser.add_argument("--sprint", default="2026_12")
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

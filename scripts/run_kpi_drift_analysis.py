#!/usr/bin/env python3
"""Analyze KPI drift from local snapshot and backfill artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT_INDEX = REPO_ROOT / "local_reviews" / "history" / "snapshot_index.json"
DEFAULT_BACKFILL = REPO_ROOT / "local_reviews" / "latest" / "kpi_trend_scoreboard_backfill.json"
DEFAULT_OUT_DIR = REPO_ROOT / "local_reviews" / "latest"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_sprint(sprint: str) -> str:
    return sprint.replace("_", "-")


def score_delta(current: Dict[str, Any], previous: Dict[str, Any], key: str) -> float:
    return round(float(current.get(key, 0.0)) - float(previous.get(key, 0.0)), 4)


def summarize_snapshots(snapshots: List[Dict[str, Any]], backfill: Dict[str, Any], sprint: str) -> Dict[str, Any]:
    normalized_sprint = normalize_sprint(sprint)
    filtered = [snap for snap in snapshots if str(snap.get("sprint", "")) == normalized_sprint]
    source = filtered if filtered else snapshots
    if not source:
        raise ValueError(f"No KPI snapshots found for sprint {sprint}")

    ordered = sorted(source, key=lambda item: str(item.get("timestamp", "")))
    latest = ordered[-1]
    previous = ordered[-2] if len(ordered) > 1 else ordered[-1]
    recent_window = ordered[-5:]
    window_start = recent_window[0]

    backfill_entries = backfill.get("entries", []) if isinstance(backfill, dict) else []
    backfill_latest = backfill_entries[-1] if backfill_entries else {}

    score = float(latest.get("score", 0.0))
    previous_score = float(previous.get("score", 0.0))
    window_delta = round(score - float(window_start.get("score", 0.0)), 4)
    drift_state = "stable"
    if window_delta > 0.5:
        drift_state = "improving"
    elif window_delta < -0.5:
        drift_state = "regressing"

    inflection_window = None
    for item in reversed(recent_window[:-1]):
        if float(item.get("score", 0.0)) != previous_score:
            inflection_window = {
                "timestamp": item.get("timestamp"),
                "score": float(item.get("score", 0.0)),
            }
            break

    result = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": normalized_sprint,
        "source_count": len(source),
        "latest_snapshot": latest,
        "previous_snapshot": previous,
        "score_delta": round(score - previous_score, 4),
        "window_delta": window_delta,
        "drift_state": drift_state,
        "health_range": {
            "min": min(float(item.get("score", 0.0)) for item in recent_window),
            "max": max(float(item.get("score", 0.0)) for item in recent_window),
        },
        "trend_deltas": {
            "critical_count": int(latest.get("critical_count", 0)) - int(previous.get("critical_count", 0)),
            "major_count": int(latest.get("major_count", 0)) - int(previous.get("major_count", 0)),
            "minor_count": int(latest.get("minor_count", 0)) - int(previous.get("minor_count", 0)),
            "informational_count": int(latest.get("informational_count", 0)) - int(previous.get("informational_count", 0)),
            "req_impl_ratio": score_delta(latest, previous, "req_impl_ratio"),
            "req_verify_ratio": score_delta(latest, previous, "req_verify_ratio"),
            "req_arch_ratio": score_delta(latest, previous, "req_arch_ratio"),
            "full_chain_ratio": score_delta(latest, previous, "full_chain_ratio"),
            "issue_quality_ratio": score_delta(latest, previous, "issue_quality_ratio"),
        },
        "backfill_reference": {
            "generated_at": backfill.get("generated_at"),
            "entry_count": backfill.get("entry_count"),
            "latest_commit": backfill_latest.get("commit_short"),
            "latest_score": backfill_latest.get("overall_health"),
        },
        "recent_window": recent_window,
        "inflection_window": inflection_window,
        "recommendations": [
            "Keep tracing recent drift windows against the latest committed review snapshot.",
            "Use the backfill reference as a long-horizon baseline when explaining current health shifts.",
        ],
    }
    return result


def write_report(out_dir: Path, result: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = REPO_ROOT / "local_reviews" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "kpi_drift_analysis_latest.json"
    md_path = out_dir / "kpi_drift_analysis_latest.md"
    history_path = history_dir / "kpi_drift_analysis.jsonl"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    latest = result["latest_snapshot"]
    previous = result["previous_snapshot"]
    md_lines = [
        "# KPI Drift Analysis",
        "",
        f"- Generated: {result['generated_at']}",
        f"- Sprint: {result['sprint']}",
        f"- Snapshot Count: {result['source_count']}",
        f"- Drift State: {result['drift_state']}",
        f"- Latest Score: {float(latest.get('score', 0.0)):.1f}%",
        f"- Previous Score: {float(previous.get('score', 0.0)):.1f}%",
        f"- Score Delta: {result['score_delta']:+.1f} pts",
        f"- Window Delta: {result['window_delta']:+.1f} pts",
        "",
        "## Trend Deltas",
    ]
    for key, value in result["trend_deltas"].items():
        if isinstance(value, float):
            md_lines.append(f"- {key}: {value:+.4f}")
        else:
            md_lines.append(f"- {key}: {value:+d}")
    md_lines.extend(
        [
            "",
            "## Backfill Reference",
            f"- Generated: {result['backfill_reference'].get('generated_at')}",
            f"- Entry Count: {result['backfill_reference'].get('entry_count')}",
            f"- Latest Commit: {result['backfill_reference'].get('latest_commit')}",
            f"- Latest Score: {result['backfill_reference'].get('latest_score')}",
            "",
            "## Recommendations",
        ]
    )
    md_lines.extend([f"- {item}" for item in result["recommendations"]])
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    with history_path.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps(result))
        history_file.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze KPI drift from local snapshot history")
    parser.add_argument("--sprint", default="2026_12")
    parser.add_argument("--snapshot-index", default=str(DEFAULT_SNAPSHOT_INDEX))
    parser.add_argument("--backfill", default=str(DEFAULT_BACKFILL))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot_index)
    backfill_path = Path(args.backfill)
    if not snapshot_path.exists():
        print(f"ERROR: snapshot index not found: {snapshot_path}")
        return 2
    if not backfill_path.exists():
        print(f"ERROR: backfill scoreboard not found: {backfill_path}")
        return 2

    snapshots = load_json(snapshot_path)
    backfill = load_json(backfill_path)
    result = summarize_snapshots(snapshots, backfill, args.sprint)
    write_report(Path(args.out_dir), result)

    print("KPI drift analysis complete")
    print(f"- sprint: {result['sprint']}")
    print(f"- state: {result['drift_state']}")
    print(f"- score delta: {result['score_delta']:+.1f} pts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

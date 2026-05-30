import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple


def run_command(cwd: Path, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=check)


def get_commit_rows(repo_root: Path, branch: str, max_commits: int) -> List[Dict[str, str]]:
    proc = run_command(
        repo_root,
        ["git", "log", branch, "--first-parent", "--reverse", "--format=%H|%cI|%s|%P"],
    )
    raw_rows = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if max_commits > 0 and len(raw_rows) > max_commits:
        raw_rows = raw_rows[-max_commits:]

    rows: List[Dict[str, str]] = []
    for meta in raw_rows:
        parts = meta.split("|", 3)
        if len(parts) < 4:
            continue
        parents = [parent for parent in parts[3].split() if parent]
        rows.append(
            {
                "commit": parts[0],
                "timestamp": parts[1],
                "subject": parts[2],
                "parent_count": str(len(parents)),
                "event_type": "merge" if len(parents) > 1 else "commit",
            }
        )
    return rows


def safe_remove_worktree(repo_root: Path, worktree_path: Path) -> None:
    try:
        run_command(repo_root, ["git", "worktree", "remove", "--force", str(worktree_path)], check=False)
    except Exception:
        pass
    if worktree_path.exists():
        shutil.rmtree(worktree_path, ignore_errors=True)


def replay_commits(
    repo_root: Path,
    python_exe: Path,
    commits: List[Dict[str, str]],
    sprint: str,
    policy_profile: str,
    replay_timeout_seconds: int,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    worktree_path = Path(tempfile.mkdtemp(prefix="independent-review-backfill-"))
    script_source = repo_root / "scripts" / "independent_repo_review.py"
    policy_source = repo_root / "config" / "independent_review_policy_profiles.json"
    sprint_dash = sprint.replace("_", "-")

    safe_remove_worktree(repo_root, worktree_path)
    run_command(repo_root, ["git", "worktree", "add", "--detach", str(worktree_path), "main"])

    results: List[Dict[str, Any]] = []
    errors: List[str] = []

    try:
        for idx, meta in enumerate(commits, start=1):
            print(
                f"[backfill] Replaying {idx}/{len(commits)} {meta['commit'][:7]} ({meta['event_type']}): {meta['subject']}",
                flush=True,
            )
            run_command(repo_root, ["git", "-C", str(worktree_path), "checkout", "--quiet", meta["commit"]])

            worktree_script = worktree_path / "scripts" / "independent_repo_review.py"
            worktree_script.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(script_source, worktree_script)

            if policy_source.exists():
                worktree_policy = worktree_path / "config" / "independent_review_policy_profiles.json"
                worktree_policy.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(policy_source, worktree_policy)

            for relative in ["independent_reviews/latest", "independent_reviews/history"]:
                (worktree_path / relative).mkdir(parents=True, exist_ok=True)

            cmd = [
                str(python_exe),
                str(worktree_script),
                "--sprint",
                sprint,
                "--run-context",
                "manual",
                "--report-mode",
                "update",
                "--policy-profile",
                policy_profile,
                "--enforcement-mode",
                "off",
                "--trend-window",
                "3",
                "--out-dir",
                "independent_reviews/latest",
            ]
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(worktree_path),
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=replay_timeout_seconds,
                )
            except subprocess.TimeoutExpired:
                errors.append(
                    f"{meta['commit'][:7]} ({idx}/{len(commits)}): replay timed out after {replay_timeout_seconds}s"
                )
                continue

            if proc.returncode != 0:
                detail = (proc.stderr or proc.stdout or "").strip()
                errors.append(
                    f"{meta['commit'][:7]} ({idx}/{len(commits)}): replay failed with exit {proc.returncode}: {detail}"
                )
                continue

            json_path = worktree_path / "independent_reviews" / "latest" / f"independent_review_{sprint_dash}_manual.json"
            if not json_path.exists():
                errors.append(f"{meta['commit'][:7]} ({idx}/{len(commits)}): expected report json missing")
                continue

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            snapshot = payload.get("trend_snapshot", {})
            severity = payload.get("severity_summary", {})

            results.append(
                {
                    "event_index": idx,
                    "event_type": meta["event_type"],
                    "commit": meta["commit"],
                    "commit_short": meta["commit"][:7],
                    "event_timestamp": meta["timestamp"],
                    "subject": meta["subject"],
                    "overall_health": float(payload.get("overall_score", 0.0)),
                    "req_impl_ratio": float(snapshot.get("req_impl_ratio", 0.0)),
                    "req_verify_ratio": float(snapshot.get("req_verify_ratio", 0.0)),
                    "req_arch_ratio": float(snapshot.get("req_arch_ratio", 0.0)),
                    "full_chain_ratio": float(snapshot.get("full_chain_ratio", 0.0)),
                    "issue_quality_ratio": float(snapshot.get("issue_quality_ratio", 0.0)),
                    "critical_count": len(severity.get("critical", [])),
                    "major_count": len(severity.get("major", [])),
                    "minor_count": len(severity.get("minor", [])),
                    "informational_count": len(severity.get("informational", [])),
                }
            )
    finally:
        safe_remove_worktree(repo_root, worktree_path)

    for idx in range(1, len(results)):
        previous = results[idx - 1]
        current = results[idx]
        current["delta_health"] = round(current["overall_health"] - previous["overall_health"], 1)
        current["delta_full_chain_pts"] = round((current["full_chain_ratio"] - previous["full_chain_ratio"]) * 100.0, 1)
        current["delta_impl_pts"] = round((current["req_impl_ratio"] - previous["req_impl_ratio"]) * 100.0, 1)
        current["delta_verify_pts"] = round((current["req_verify_ratio"] - previous["req_verify_ratio"]) * 100.0, 1)
        current["delta_arch_pts"] = round((current["req_arch_ratio"] - previous["req_arch_ratio"]) * 100.0, 1)
        current["delta_issue_quality_pts"] = round(
            (current["issue_quality_ratio"] - previous["issue_quality_ratio"]) * 100.0,
            1,
        )
        current["delta_critical_major"] = (
            (current["critical_count"] + current["major_count"])
            - (previous["critical_count"] + previous["major_count"])
        )

    return results, errors


def format_pct(value: float) -> str:
    return f"{value * 100.0:.1f}%"


def write_scoreboard(repo_root: Path, sprint: str, entries: List[Dict[str, Any]], errors: List[str]) -> Tuple[Path, Path]:
    latest_dir = repo_root / "independent_reviews" / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    json_path = latest_dir / "kpi_trend_scoreboard_backfill.json"
    md_path = latest_dir / "kpi_trend_scoreboard_backfill.md"

    payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": sprint,
        "entry_count": len(entries),
        "entries": entries,
        "errors": errors,
        "method": "One-time synthetic backfill by replaying current review logic against historical commits.",
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# KPI Trend Scoreboard (Backfill)")
    lines.append("")
    lines.append(f"- Generated: {payload['generated_at']}")
    lines.append(f"- Sprint scope: {sprint.replace('_', '-')}")
    lines.append(f"- Replayed commits: {len(entries)}")
    lines.append("- Method: synthetic replay of current independent review logic against historical commit trees")
    lines.append("")

    if entries:
        first = entries[0]
        last = entries[-1]
        lines.append("## Health Trajectory")
        lines.append(f"- Start ({first['commit_short']}): {first['overall_health']:.1f}%")
        lines.append(f"- End ({last['commit_short']}): {last['overall_health']:.1f}%")
        lines.append(f"- Net change: {last['overall_health'] - first['overall_health']:+.1f} pts")
        lines.append("")

    lines.append("## Event Scoreboard")
    lines.append("| # | Time | Event | Commit | Health | Impl | Verify | Arch | Full Chain | Issue Quality | C+M | Delta Health |")
    lines.append("|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in entries:
        delta_health = row.get("delta_health", 0.0)
        lines.append(
            "| "
            f"{row['event_index']} | {row['event_timestamp']} | {row['event_type']} | {row['commit_short']} | "
            f"{row['overall_health']:.1f}% | {format_pct(row['req_impl_ratio'])} | {format_pct(row['req_verify_ratio'])} | "
            f"{format_pct(row['req_arch_ratio'])} | {format_pct(row['full_chain_ratio'])} | {format_pct(row['issue_quality_ratio'])} | "
            f"{row['critical_count'] + row['major_count']} | {delta_health:+.1f} |"
        )

    lines.append("")
    if errors:
        lines.append("## Replay Gaps")
        lines.append("Some commits could not be replayed; those points are omitted from the scoreboard.")
        lines.extend([f"- {item}" for item in errors])
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def write_overtime_report(repo_root: Path, sprint: str, entries: List[Dict[str, Any]], errors: List[str]) -> Path:
    latest_dir = repo_root / "independent_reviews" / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    report_path = latest_dir / "independent_review_backfill_over_time.md"

    lines: List[str] = []
    lines.append("# Independent Review Backfill Over-Time View")
    lines.append("")
    lines.append(f"- Generated: {dt.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Sprint scope: {sprint.replace('_', '-')}")
    lines.append(f"- Backfill points: {len(entries)}")
    lines.append("")

    if not entries:
        lines.append("No replay points were generated.")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path

    first = entries[0]
    last = entries[-1]
    worst = min(entries, key=lambda item: item["overall_health"])
    best = max(entries, key=lambda item: item["overall_health"])

    lines.append("## Executive Narrative")
    lines.append(
        "This one-time backfill replays the current governance review model over historical commits to estimate the KPI trajectory before remediation. "
        f"Across {len(entries)} events, overall health moves from {first['overall_health']:.1f}% to {last['overall_health']:.1f}% "
        f"({last['overall_health'] - first['overall_health']:+.1f} points). "
        f"The lowest observed health is {worst['overall_health']:.1f}% at {worst['commit_short']}, and the highest is {best['overall_health']:.1f}% at {best['commit_short']}."
    )
    lines.append("")
    lines.append(
        "The KPI perspective indicates how the repository arrived at the current pre-remediation posture: "
        f"implementation coverage is now {format_pct(last['req_impl_ratio'])}, verification is {format_pct(last['req_verify_ratio'])}, "
        f"architecture/design traceability is {format_pct(last['req_arch_ratio'])}, full-chain completeness is {format_pct(last['full_chain_ratio'])}, "
        f"and issue-governance quality is {format_pct(last['issue_quality_ratio'])}."
    )
    lines.append("")

    inflections = [item for item in entries[1:] if abs(item.get("delta_health", 0.0)) >= 2.0]
    lines.append("## Notable Inflection Points")
    if inflections:
        for item in inflections[-15:]:
            lines.append(
                f"- {item['event_timestamp']} | {item['event_type']} | {item['commit_short']} | "
                f"health delta {item.get('delta_health', 0.0):+.1f} | {item['subject']}"
            )
    else:
        lines.append("- No health inflection points above +/-2.0 were observed in the replay window.")
    lines.append("")

    lines.append("## Current Pre-Remediation Baseline")
    lines.append(f"- Commit: {last['commit']} ({last['commit_short']})")
    lines.append(f"- Event time: {last['event_timestamp']}")
    lines.append(f"- Overall health: {last['overall_health']:.1f}%")
    lines.append(f"- Implementation coverage: {format_pct(last['req_impl_ratio'])}")
    lines.append(f"- Verification coverage: {format_pct(last['req_verify_ratio'])}")
    lines.append(f"- Architecture/design traceability: {format_pct(last['req_arch_ratio'])}")
    lines.append(f"- Full source-to-evidence chain completeness: {format_pct(last['full_chain_ratio'])}")
    lines.append(f"- Issue governance quality: {format_pct(last['issue_quality_ratio'])}")
    lines.append(f"- Critical+major findings: {last['critical_count'] + last['major_count']}")
    lines.append("")

    if errors:
        lines.append("## Replay Limitations")
        lines.append(
            "Some historical points could not be replayed. The report still reflects the replayed event sequence and remains useful for directional drift analysis."
        )
        lines.extend([f"- {item}" for item in errors])
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="One-time KPI backfill across historical commits")
    parser.add_argument("--branch", type=str, default="main", help="Branch to replay from oldest to newest")
    parser.add_argument("--sprint", type=str, default="2026_12", help="Sprint identifier for generated review files")
    parser.add_argument("--policy-profile", type=str, default="strict", help="Policy profile passed to independent review")
    parser.add_argument("--max-commits", type=int, default=0, help="Optional cap on number of replayed commits; 0 means all")
    parser.add_argument("--replay-timeout-seconds", type=int, default=180, help="Per-commit timeout for synthetic replay execution")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    python_exe = Path(sys.executable).resolve()

    commits = get_commit_rows(repo_root, args.branch, args.max_commits)
    if not commits:
        print("[backfill] No commits found to replay.")
        return 2

    print(f"[backfill] Replaying {len(commits)} commit(s) from {args.branch}...")
    entries, errors = replay_commits(
        repo_root=repo_root,
        python_exe=python_exe,
        commits=commits,
        sprint=args.sprint,
        policy_profile=args.policy_profile,
        replay_timeout_seconds=max(30, args.replay_timeout_seconds),
    )

    json_path, scoreboard_path = write_scoreboard(repo_root, args.sprint, entries, errors)
    report_path = write_overtime_report(repo_root, args.sprint, entries, errors)

    print("[backfill] Complete")
    print(f"[backfill] Replayed points: {len(entries)}")
    print(f"[backfill] Replay errors: {len(errors)}")
    print(f"[backfill] Scoreboard JSON: {json_path.as_posix()}")
    print(f"[backfill] Scoreboard Markdown: {scoreboard_path.as_posix()}")
    print(f"[backfill] Over-time report: {report_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

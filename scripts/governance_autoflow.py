import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


def run_command(cwd: Path, args: List[str]) -> int:
    proc = subprocess.run(args, cwd=str(cwd), text=True, check=False)
    return proc.returncode


def current_branch(repo_root: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=False,
    )
    return (proc.stdout or "").strip() or "unknown"


def load_routing_map(path: Path) -> Dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    contexts = raw.get("contexts", {})
    if not contexts:
        raise ValueError(f"Routing map at '{path.as_posix()}' does not define contexts.")
    return raw


def resolve_profile(branch: str, explicit: str, routing: Dict[str, Any]) -> str:
    if explicit:
        return explicit

    env_profile = (os.getenv("INDEPENDENT_REVIEW_PROFILE") or "").strip()
    if env_profile:
        return env_profile

    selection = routing.get("profile_selection", {})
    for rule in selection.get("rules", []):
        pattern = str(rule.get("match", ""))
        if pattern and re.search(pattern, branch):
            return str(rule.get("profile", "default"))

    return str(selection.get("default_profile", "default"))


def append_execution_ledger(repo_root: Path, entry: Dict[str, Any]) -> None:
    latest_dir = repo_root / "local_reviews" / "latest"
    history_dir = repo_root / "local_reviews" / "history"
    latest_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)

    latest_json = latest_dir / "governance_execution_ledger_latest.json"
    latest_md = latest_dir / "governance_execution_ledger_latest.md"
    history_jsonl = history_dir / "governance_execution_ledger.jsonl"

    latest_json.write_text(json.dumps(entry, indent=2), encoding="utf-8")

    md_lines = [
        "# Governance Execution Ledger (Latest)",
        "",
        f"- Timestamp: {entry['timestamp']}",
        f"- Context: {entry['context']}",
        f"- Branch: {entry['branch']}",
        f"- Policy Profile: {entry['policy_profile']}",
        f"- Enforcement Mode: {entry['enforcement_mode']}",
        f"- Outcome: {entry['outcome']}",
        f"- Exit Code: {entry['exit_code']}",
        "",
        "## Agent Chain",
    ]
    if entry.get("agent_chain"):
        md_lines.extend([f"- {item}" for item in entry["agent_chain"]])
    else:
        md_lines.append("- none")
    md_lines.append("")
    md_lines.append("## Skill Chain")
    if entry.get("skill_chain"):
        md_lines.extend([f"- {item}" for item in entry["skill_chain"]])
    else:
        md_lines.append("- none")
    md_lines.append("")
    md_lines.append("## Commands")
    for item in entry.get("commands", []):
        md_lines.append(f"- {' '.join(item)}")
    md_lines.append("")

    latest_md.write_text("\n".join(md_lines), encoding="utf-8")

    with history_jsonl.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry))
        f.write("\n")


def build_review_command(
    repo_root: Path,
    sprint: str,
    run_context: str,
    profile: str,
    enforcement_mode: str,
    trend_window: int,
    out_dir: str,
) -> List[str]:
    return [
        sys.executable,
        str(repo_root / "scripts" / "independent_repo_review.py"),
        "--sprint",
        sprint,
        "--run-context",
        run_context,
        "--report-mode",
        "update",
        "--policy-profile",
        profile,
        "--enforcement-mode",
        enforcement_mode,
        "--trend-window",
        str(max(1, trend_window)),
        "--out-dir",
        out_dir,
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run governance autoflow by repository context")
    parser.add_argument(
        "--context",
        choices=["planning", "pre-commit", "pre-merge-commit", "pre-push", "closeout", "portfolio"],
        required=True,
        help="Governance execution context",
    )
    parser.add_argument("--sprint", type=str, default="2026_12", help="Sprint identifier (YYYY_MM)")
    parser.add_argument("--policy-profile", type=str, default="", help="Explicit policy profile override")
    parser.add_argument("--trend-window", type=int, default=5, help="Trend window for independent review")
    parser.add_argument("--out-dir", type=str, default="local_reviews/latest", help="Output directory")
    parser.add_argument(
        "--routing-map",
        type=str,
        default="config/governance_autoflow_routing.json",
        help="Path to JSON routing map",
    )
    parser.add_argument(
        "--hook-fail-mode",
        choices=["profile", "warn"],
        default="profile",
        help="Failure behavior; warn continues and records warning outcome",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    routing_map_path = repo_root / args.routing_map
    routing = load_routing_map(routing_map_path)
    context_cfg = routing["contexts"].get(args.context)
    if context_cfg is None:
        raise ValueError(f"Context '{args.context}' not found in routing map: {routing_map_path.as_posix()}")

    branch = current_branch(repo_root)
    profile = resolve_profile(branch, args.policy_profile, routing)

    run_context = str(context_cfg.get("run_context", "manual"))
    enforcement_mode = str(context_cfg.get("enforcement_mode", "off"))
    configured_trend_window = int(context_cfg.get("trend_window", args.trend_window))
    agent_chain = [str(item) for item in context_cfg.get("agent_chain", [])]
    skill_chain = [str(item) for item in context_cfg.get("skill_chain", [])]

    print("[governance-autoflow] Context:", args.context)
    print("[governance-autoflow] Branch:", branch)
    print("[governance-autoflow] Policy profile:", profile)
    print("[governance-autoflow] Enforcement mode:", enforcement_mode)
    print("[governance-autoflow] Agent chain:", ", ".join(agent_chain) if agent_chain else "none")
    print("[governance-autoflow] Skill chain:", ", ".join(skill_chain) if skill_chain else "none")

    commands: List[List[str]] = []
    review_cmd = build_review_command(
        repo_root=repo_root,
        sprint=args.sprint,
        run_context=run_context,
        profile=profile,
        enforcement_mode=enforcement_mode,
        trend_window=configured_trend_window,
        out_dir=args.out_dir,
    )
    commands.append(review_cmd)
    rc = run_command(repo_root, review_cmd)

    outcome = "success"
    exit_code = rc
    if rc != 0:
        if args.hook_fail_mode == "warn":
            outcome = "warning"
            exit_code = 0
            print("[governance-autoflow] WARNING: review step failed; continuing because --hook-fail-mode=warn")
        else:
            outcome = "failed"

    ledger_entry: Dict[str, Any] = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "context": args.context,
        "branch": branch,
        "policy_profile": profile,
        "enforcement_mode": enforcement_mode,
        "run_context": run_context,
        "trend_window": configured_trend_window,
        "agent_chain": agent_chain,
        "skill_chain": skill_chain,
        "commands": commands,
        "outcome": outcome,
        "exit_code": exit_code,
    }
    append_execution_ledger(repo_root, ledger_entry)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

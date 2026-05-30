import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


def run_command(cwd: Path, args: List[str], label: str) -> Dict[str, Any]:
    started_at = dt.datetime.now().isoformat(timespec="seconds")
    started_perf = time.perf_counter()
    print(f"[governance-autoflow] Stage {label}: starting")
    proc = subprocess.run(args, cwd=str(cwd), text=True, check=False)
    duration_seconds = round(time.perf_counter() - started_perf, 3)
    ended_at = dt.datetime.now().isoformat(timespec="seconds")
    print(f"[governance-autoflow] Stage {label}: {proc.returncode}")
    return {
        "command": args,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": duration_seconds,
        "exit_code": proc.returncode,
        "status": "success" if proc.returncode == 0 else "failed",
    }


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
    md_lines.append("## Agent Stage Results")
    if entry.get("agent_stage_results"):
        for stage in entry["agent_stage_results"]:
            md_lines.append(
                f"- {stage['order']}. {stage['name']} | status={stage['status']} | mode={stage['execution_mode']} | duration={stage['duration_seconds']:.3f}s"
            )
            if stage.get("notes"):
                md_lines.append(f"  note: {stage['notes']}")
    else:
        md_lines.append("- none")
    md_lines.append("")
    md_lines.append("## Skill Stage Results")
    if entry.get("skill_stage_results"):
        for stage in entry["skill_stage_results"]:
            md_lines.append(
                f"- {stage['order']}. {stage['name']} | status={stage['status']} | mode={stage['execution_mode']} | duration={stage['duration_seconds']:.3f}s"
            )
            if stage.get("notes"):
                md_lines.append(f"  note: {stage['notes']}")
    else:
        md_lines.append("- none")
    md_lines.append("")
    md_lines.append("## Commands")
    for index, item in enumerate(entry.get("commands", []), start=1):
        stage_names = ", ".join(item.get("stage_labels", [])) if item.get("stage_labels") else ", ".join(item.get("stage_names", [])) if item.get("stage_names") else "none"
        md_lines.append(
            f"- [{index}] key={item.get('command_key', 'unknown')} status={item['status']} exit={item['exit_code']} duration={item['duration_seconds']:.3f}s stages={stage_names} :: {' '.join(item['command'])}"
        )
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


def build_stage_command(
    stage_name: str,
    context: str,
    repo_root: Path,
    sprint: str,
    run_context: str,
    profile: str,
    enforcement_mode: str,
    trend_window: int,
    out_dir: str,
) -> Dict[str, Any] | None:
    if stage_name == "repo-governance-autoflow-orchestrator":
        return None

    if stage_name in {"independent-review-orchestrator", "independent-repo-review"}:
        return {
            "command_key": "independent-review",
            "command": build_review_command(
                repo_root=repo_root,
                sprint=sprint,
                run_context=run_context,
                profile=profile,
                enforcement_mode=enforcement_mode,
                trend_window=trend_window,
                out_dir=out_dir,
            ),
            "notes": "Executed via the shared independent review engine.",
        }

    if stage_name in {"requirements-baseline-steward", "sprint-intake-gatekeeper", "source-to-evidence-traceability-auditor", "source-to-evidence-traceability"}:
        command_args = [
            sys.executable,
            str(repo_root / "scripts" / "verify_sprint_traceability.py"),
            "--sprint",
            sprint,
        ]
        if stage_name in {"source-to-evidence-traceability-auditor", "source-to-evidence-traceability"}:
            command_args.append("--audit")
        return {
            "command_key": "traceability",
            "command": command_args,
            "notes": "Executed via sprint traceability verification.",
        }

    if stage_name in {"verification-coverage-planner", "sprint-execution-compliance-monitor"}:
        return {
            "command_key": "traceability-audit",
            "command": [
                sys.executable,
                str(repo_root / "scripts" / "verify_sprint_traceability.py"),
                "--sprint",
                sprint,
                "--audit",
            ],
            "notes": "Executed via sprint traceability audit mode.",
        }

    if stage_name == "kpi-drift-analyst":
        return {
            "command_key": "kpi-drift-analysis",
            "command": [
                sys.executable,
                str(repo_root / "scripts" / "run_kpi_drift_analysis.py"),
                "--sprint",
                sprint,
            ],
            "notes": "Executed via KPI drift analysis runner.",
        }

    if stage_name == "sprint-closeout-certifier":
        return {
            "command_key": "sprint-closeout-certification",
            "command": [
                sys.executable,
                str(repo_root / "scripts" / "run_sprint_closeout_certification.py"),
                "--sprint",
                sprint,
            ],
            "notes": "Executed via sprint closeout certification runner.",
        }

    if stage_name == "multi-sprint-portfolio-planner":
        return {
            "command_key": "multi-sprint-portfolio-planning",
            "command": [
                sys.executable,
                str(repo_root / "scripts" / "run_multi_sprint_portfolio_planning.py"),
                "--sprint",
                sprint,
            ],
            "notes": "Executed via multi-sprint portfolio planning runner.",
        }

    if stage_name == "remediation-readiness":
        return {
            "command_key": "remediation-readiness",
            "command": [
                sys.executable,
                str(repo_root / "scripts" / "run_remediation_readiness.py"),
                "--sprint",
                sprint,
            ],
            "notes": "Executed via remediation readiness analysis.",
        }

    if stage_name == "architecture-contract-enforcer":
        return {
            "command_key": "dependency-boundary",
            "command": [
                sys.executable,
                str(repo_root / "scripts" / "verify_dependency_boundary.py"),
            ],
            "notes": "Executed via dependency boundary guard.",
        }

    if stage_name == "artifact-lineage-auditor":
        archive_args = [
            sys.executable,
            str(repo_root / "scripts" / "archive_hygiene.py"),
            "check",
        ]
        if context in {"pre-commit", "pre-merge-commit"}:
            archive_args.extend(["--staged", "--enforce"])
        else:
            archive_args.extend(["--upstream", "--enforce"])
        return {
            "command_key": "artifact-hygiene",
            "command": archive_args,
            "notes": "Executed via archive hygiene guard.",
        }

    if stage_name == "governance-policy-compiler":
        return {
            "command_key": "policy-validation",
            "command": [
                sys.executable,
                str(repo_root / "scripts" / "validate_cross_domain_exception_policy.py"),
            ],
            "notes": "Executed via cross-domain policy validation.",
        }

    return None


def plan_stage_invocations(
    names: List[str],
    kind: str,
    context: str,
    repo_root: Path,
    sprint: str,
    run_context: str,
    profile: str,
    enforcement_mode: str,
    trend_window: int,
    out_dir: str,
) -> List[Dict[str, Any]]:
    plans: List[Dict[str, Any]] = []
    for order, name in enumerate(names, start=1):
        command_plan = build_stage_command(
            stage_name=name,
            context=context,
            repo_root=repo_root,
            sprint=sprint,
            run_context=run_context,
            profile=profile,
            enforcement_mode=enforcement_mode,
            trend_window=trend_window,
            out_dir=out_dir,
        )
        plans.append(
            {
                "order": order,
                "name": name,
                "kind": kind,
                "command_key": command_plan["command_key"] if command_plan else None,
                "command": command_plan["command"] if command_plan else None,
                "notes": command_plan["notes"] if command_plan else "Declared route stage; no discrete command is wired yet.",
            }
        )
    return plans


def execute_planned_commands(plans: List[Dict[str, Any]], repo_root: Path) -> List[Dict[str, Any]]:
    command_records: List[Dict[str, Any]] = []
    command_index_by_key: Dict[str, int] = {}

    for plan in plans:
        command = plan.get("command")
        command_key = plan.get("command_key")
        if not command or not command_key:
            continue
        if command_key in command_index_by_key:
            continue

        command_result = run_command(repo_root, command, label=command_key)
        command_result["command_key"] = command_key
        command_result["stage_names"] = []
        command_result["stage_labels"] = []
        command_records.append(command_result)
        command_index_by_key[command_key] = len(command_records)

    for plan in plans:
        command_key = plan.get("command_key")
        if not command_key or command_key not in command_index_by_key:
            continue
        stage_names = command_records[command_index_by_key[command_key] - 1]["stage_names"]
        if plan["name"] not in stage_names:
            stage_names.append(plan["name"])
        stage_label = f"{plan['kind']}:{plan['name']}"
        stage_labels = command_records[command_index_by_key[command_key] - 1]["stage_labels"]
        if stage_label not in stage_labels:
            stage_labels.append(stage_label)

    return command_records


def build_stage_results(
    plans: List[Dict[str, Any]],
    command_records: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    command_index_by_key = {record["command_key"]: index + 1 for index, record in enumerate(command_records)}
    command_result_by_key = {record["command_key"]: record for record in command_records}
    results: List[Dict[str, Any]] = []

    for plan in plans:
        name = plan["name"]
        order = plan["order"]
        command_key = plan.get("command_key")
        command_result = command_result_by_key.get(command_key)

        if name == "repo-governance-autoflow-orchestrator":
            status = "success"
            execution_mode = "direct"
            duration_seconds = 0.0
            started_at = command_result["started_at"] if command_result else dt.datetime.now().isoformat(timespec="seconds")
            ended_at = command_result["ended_at"] if command_result else started_at
            command_ref = None
            notes = "Context router executed locally before stage dispatch."
        elif command_result is not None:
            status = command_result["status"]
            execution_mode = "direct"
            duration_seconds = command_result["duration_seconds"]
            started_at = command_result["started_at"]
            ended_at = command_result["ended_at"]
            command_ref = command_index_by_key[command_key]
            notes = plan["notes"]
        else:
            status = "declared"
            execution_mode = "declared-only"
            duration_seconds = 0.0
            started_at = dt.datetime.now().isoformat(timespec="seconds")
            ended_at = started_at
            command_ref = None
            notes = plan["notes"]

        results.append(
            {
                "order": order,
                "name": name,
                "kind": plan["kind"],
                "status": status,
                "execution_mode": execution_mode,
                "started_at": started_at,
                "ended_at": ended_at,
                "duration_seconds": duration_seconds,
                "command_ref": command_ref,
                "command_key": command_key,
                "notes": notes,
            }
        )

    return results


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

    agent_plans = plan_stage_invocations(
        names=agent_chain,
        kind="agent",
        context=args.context,
        repo_root=repo_root,
        sprint=args.sprint,
        run_context=run_context,
        profile=profile,
        enforcement_mode=enforcement_mode,
        trend_window=configured_trend_window,
        out_dir=args.out_dir,
    )
    skill_plans = plan_stage_invocations(
        names=skill_chain,
        kind="skill",
        context=args.context,
        repo_root=repo_root,
        sprint=args.sprint,
        run_context=run_context,
        profile=profile,
        enforcement_mode=enforcement_mode,
        trend_window=configured_trend_window,
        out_dir=args.out_dir,
    )
    all_plans = agent_plans + skill_plans

    command_results = execute_planned_commands(all_plans, repo_root)
    command_exit_codes = [result["exit_code"] for result in command_results]
    rc = max(command_exit_codes) if command_exit_codes else 0

    outcome = "success"
    exit_code = rc
    if rc != 0:
        if args.hook_fail_mode == "warn":
            outcome = "warning"
            exit_code = 0
            print("[governance-autoflow] WARNING: one or more stage commands failed; continuing because --hook-fail-mode=warn")
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
        "agent_stage_results": build_stage_results(agent_plans, command_results),
        "skill_stage_results": build_stage_results(skill_plans, command_results),
        "commands": command_results,
        "outcome": outcome,
        "exit_code": exit_code,
    }
    append_execution_ledger(repo_root, ledger_entry)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

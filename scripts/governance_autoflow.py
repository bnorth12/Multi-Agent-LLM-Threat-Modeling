import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


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


def auto_profile(branch: str, explicit: str) -> str:
    if explicit:
        return explicit
    if branch == "main" or branch.startswith("release/"):
        return "strict"
    return "default"


def context_to_run_context(context: str) -> str:
    mapping = {
        "planning": "manual",
        "pre-commit": "pre-commit",
        "pre-merge-commit": "pre-merge-commit",
        "pre-push": "pre-push",
        "closeout": "manual",
        "portfolio": "manual",
    }
    return mapping[context]


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
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    branch = current_branch(repo_root)
    profile = auto_profile(branch, args.policy_profile)

    run_context = context_to_run_context(args.context)
    enforcement_mode = "auto" if args.context in {"pre-merge-commit", "pre-push"} else "off"

    print("[governance-autoflow] Context:", args.context)
    print("[governance-autoflow] Branch:", branch)
    print("[governance-autoflow] Policy profile:", profile)
    print("[governance-autoflow] Enforcement mode:", enforcement_mode)

    review_cmd = [
        sys.executable,
        str(repo_root / "scripts" / "independent_repo_review.py"),
        "--sprint",
        args.sprint,
        "--run-context",
        run_context,
        "--report-mode",
        "update",
        "--policy-profile",
        profile,
        "--enforcement-mode",
        enforcement_mode,
        "--trend-window",
        str(max(1, args.trend_window)),
        "--out-dir",
        args.out_dir,
    ]

    rc = run_command(repo_root, review_cmd)
    if rc != 0:
        return rc

    # Start of extended implementation: route placeholders for newly scaffolded governance skills.
    if args.context in {"planning", "portfolio", "closeout"}:
        print("[governance-autoflow] Next route stage (scaffolded): sprint planning and portfolio governance skills")
    if args.context in {"pre-commit", "pre-merge-commit", "pre-push"}:
        print("[governance-autoflow] Next route stage (scaffolded): requirements, architecture, verification, and KPI drift skills")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

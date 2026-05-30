import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


MISSING_REQ_RE = re.compile(r"Requirement\s+([A-Z]+-\d+[A-Z]?)\s+referenced by sprint artifacts but not documented", re.IGNORECASE)
MISSING_TEST_RE = re.compile(r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+is missing explicit test evidence", re.IGNORECASE)
MISSING_FUNCTION_ROOT_RE = re.compile(r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+references child function\s+([A-Z0-9_-]+)\s+not defined", re.IGNORECASE)
MISSING_REGISTRY_LINK_RE = re.compile(r"Issue\s+((?:S\d{2}-\d+)|(?:R\d{2}-\d{3}))\s+requirement\s+([A-Z]+-\d+[A-Z]?)\s+has no aligned row in\s+Requirements/15_End_To_End_Traceability_Attributes_Registry\.md", re.IGNORECASE)


def summarize(lines: List[str]) -> Dict[str, List[str]]:
    missing_reqs = sorted({m.group(1) for line in lines for m in [MISSING_REQ_RE.search(line)] if m})
    missing_tests = sorted({m.group(1) for line in lines for m in [MISSING_TEST_RE.search(line)] if m})
    missing_function_roots = sorted(
        {f"{m.group(1)}:{m.group(2)}" for line in lines for m in [MISSING_FUNCTION_ROOT_RE.search(line)] if m}
    )
    missing_registry_links = sorted(
        {f"{m.group(1)}:{m.group(2)}" for line in lines for m in [MISSING_REGISTRY_LINK_RE.search(line)] if m}
    )
    return {
        "missing_requirement_docs": missing_reqs,
        "missing_test_evidence": missing_tests,
        "missing_function_root_links": missing_function_roots,
        "missing_registry_links": missing_registry_links,
    }


def write_outputs(repo_root: Path, out_dir: str, sprint: str, verify_exit: int, output_lines: List[str], summary: Dict[str, List[str]]) -> None:
    out_root = repo_root / out_dir
    out_root.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "sprint": sprint,
        "verify_exit_code": verify_exit,
        "missing_requirement_docs": summary["missing_requirement_docs"],
        "missing_test_evidence": summary["missing_test_evidence"],
        "missing_function_root_links": summary["missing_function_root_links"],
        "missing_registry_links": summary["missing_registry_links"],
    }

    (out_root / "traceability_blocker_backlog_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines: List[str] = [
        "# Traceability Blocker Backlog (Latest)",
        "",
        f"- Timestamp: {payload['timestamp']}",
        f"- Sprint: {sprint}",
        f"- Source verifier exit code: {verify_exit}",
        "",
        "## Missing Requirement Documentation IDs",
    ]

    reqs = summary["missing_requirement_docs"]
    if reqs:
        lines.extend([f"- {item}" for item in reqs])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Issues Missing Explicit Test Evidence",
    ])

    issues = summary["missing_test_evidence"]
    if issues:
        lines.extend([f"- {item}" for item in issues])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Missing Function Root Links (Issue:Function)",
    ])

    function_roots = summary["missing_function_root_links"]
    if function_roots:
        lines.extend([f"- {item}" for item in function_roots])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Missing Requirements/15 Registry Links (Issue:Requirement)",
    ])

    registry_links = summary["missing_registry_links"]
    if registry_links:
        lines.extend([f"- {item}" for item in registry_links])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Suggested Remediation Order",
        "1. Resolve missing requirement-documentation IDs in a dedicated requirements commit.",
        "2. Create missing function hierarchy entries in docs/architecture/Function_Hierarchy_Registry.md grouped by parent capability.",
        "3. Add or update Requirements/15 registry rows for missing issue/requirement links with architecture/design/implementation/verification references.",
        "4. Add explicit test evidence references for remaining issue files in a separate evidence commit.",
        "5. Re-run sprint traceability validation and capture post-remediation output.",
        "",
        "## Raw Verification Output (Tail)",
    ])

    tail = output_lines[-80:] if len(output_lines) > 80 else output_lines
    if tail:
        lines.extend([f"- {line}" for line in tail])
    else:
        lines.append("- no output")

    (out_root / "traceability_blocker_backlog_latest.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a blocker backlog from sprint traceability validation output")
    parser.add_argument("--sprint", type=str, required=True, help="Sprint identifier (YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN)")
    parser.add_argument("--out-dir", type=str, default="independent_reviews/latest", help="Output directory")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    verify_script = repo_root / "scripts" / "verify_sprint_traceability.py"

    proc = subprocess.run(
        [sys.executable, str(verify_script), "--sprint", args.sprint],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=False,
    )

    merged = []
    if proc.stdout:
        merged.extend(proc.stdout.splitlines())
    if proc.stderr:
        merged.extend(proc.stderr.splitlines())

    summary = summarize(merged)
    write_outputs(repo_root, args.out_dir, args.sprint, proc.returncode, merged, summary)

    print("Traceability blocker backlog generated:")
    print(f"- Sprint: {args.sprint}")
    print(f"- Missing requirement docs: {len(summary['missing_requirement_docs'])}")
    print(f"- Missing explicit test evidence: {len(summary['missing_test_evidence'])}")
    print(f"- Missing function root links: {len(summary['missing_function_root_links'])}")
    print(f"- Missing registry links: {len(summary['missing_registry_links'])}")
    print(f"- Source verifier exit code: {proc.returncode}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

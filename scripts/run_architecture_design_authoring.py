import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Dict, List


REQ_ID_RE = re.compile(r"\b[A-Z]+-\d+[A-Z]?\b")


def find_remediation_plan(repo_root: Path, sprint: str, explicit_path: str) -> Path:
    if explicit_path:
        candidate = repo_root / explicit_path
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"Remediation plan not found: {candidate.as_posix()}")

    patterns = [
        f"planning/issues/issue_{sprint}_*.md",
        f"planning/issues/issue_{sprint.replace('_', '-')}_*.md",
        f"planning/issues/issue_{sprint.replace('-', '_')}_*.md",
        "planning/Sprint_Remediation_Issue_*.md",
        f"planning/Sprint_{sprint}_Remediation_*.md",
    ]
    for pattern in patterns:
        candidates = sorted(
            repo_root.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for candidate in candidates:
            text = candidate.read_text(encoding="utf-8", errors="ignore")
            if "## Remediation Targets" in text:
                return candidate
        if candidates:
            return candidates[0]

    joined_patterns = ", ".join(patterns)
    raise FileNotFoundError(f"No remediation plan matches: {joined_patterns}")


def parse_evidence_targets(lines: List[str]) -> List[str]:
    targets: List[str] = []
    capture = False
    for line in lines:
        stripped = line.strip()
        if stripped in {"## Evidence Targets", "## Remediation Targets"}:
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture and stripped.startswith("- "):
            targets.append(stripped[2:].strip())
    return targets


def build_workpack(repo_root: Path, plan_path: Path) -> Dict[str, object]:
    lines = plan_path.read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines)
    requirement_ids = sorted(set(REQ_ID_RE.findall(text)))
    targets = parse_evidence_targets(lines)

    architecture_targets = sorted([t for t in targets if t.startswith("docs/architecture/") or t.startswith("docs/design/")])
    implementation_targets = sorted([t for t in targets if t.startswith("src/") or t.startswith("frontend/src/") or t.startswith("scripts/")])
    verification_targets = sorted([t for t in targets if t.startswith("Tests/") or t.startswith("test_reports/")])

    gaps: List[str] = []
    if implementation_targets and not architecture_targets:
        gaps.append("Implementation evidence exists without architecture/design targets.")
    if requirement_ids and not architecture_targets:
        gaps.append("Requirement IDs are present but architecture/design references are missing from evidence targets.")
    if implementation_targets and not verification_targets:
        gaps.append("Implementation targets are listed without verification targets.")

    if requirement_ids and architecture_targets:
        missing_requirement_evidence: Dict[str, List[str]] = {}
        for req_id in requirement_ids:
            evidence_hits: List[str] = []
            for rel in architecture_targets:
                target = repo_root / rel
                if not target.exists():
                    continue
                text = target.read_text(encoding="utf-8", errors="ignore")
                if req_id in text:
                    evidence_hits.append(rel)
            if not evidence_hits:
                missing_requirement_evidence[req_id] = []

        if missing_requirement_evidence:
            for req_id in sorted(missing_requirement_evidence):
                gaps.append(
                    f"Requirement {req_id} is not found in architecture/design authority targets listed by remediation plan."
                )

    return {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "plan_path": plan_path.as_posix(),
        "requirement_ids": requirement_ids,
        "architecture_targets": architecture_targets,
        "implementation_targets": implementation_targets,
        "verification_targets": verification_targets,
        "gaps": gaps,
    }


def write_outputs(repo_root: Path, out_dir: str, workpack: Dict[str, object]) -> None:
    out_root = repo_root / out_dir
    out_root.mkdir(parents=True, exist_ok=True)

    json_path = out_root / "architecture_design_authoring_workpack_latest.json"
    md_path = out_root / "architecture_design_authoring_workpack_latest.md"

    json_path.write_text(json.dumps(workpack, indent=2), encoding="utf-8")

    lines: List[str] = [
        "# Architecture/Design Authoring Workpack (Latest)",
        "",
        f"- Timestamp: {workpack['timestamp']}",
        f"- Remediation Plan: {workpack['plan_path']}",
        "",
        "## Requirement Scope",
    ]

    req_ids = workpack["requirement_ids"]
    if req_ids:
        lines.extend([f"- {item}" for item in req_ids])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Architecture/Design Targets",
    ])

    arch_targets = workpack["architecture_targets"]
    if arch_targets:
        lines.extend([f"- {item}" for item in arch_targets])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Implementation Targets",
    ])

    impl_targets = workpack["implementation_targets"]
    if impl_targets:
        lines.extend([f"- {item}" for item in impl_targets])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Verification Targets",
    ])

    verify_targets = workpack["verification_targets"]
    if verify_targets:
        lines.extend([f"- {item}" for item in verify_targets])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Disposition Decision Template",
        "- Decision required: update architecture/design to match implementation OR change implementation to match architecture/design.",
        "- Selected path:",
        "- Decision rationale:",
        "- Approval reference:",
        "- Verification rerun evidence path:",
        "",
        "## Detected Gaps",
    ])

    gaps = workpack["gaps"]
    if gaps:
        lines.extend([f"- {item}" for item in gaps])
    else:
        lines.append("- none")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate architecture/design authoring workpack for remediation execution")
    parser.add_argument("--sprint", type=str, default="2026_12", help="Sprint identifier (YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN)")
    parser.add_argument("--out-dir", type=str, default="independent_reviews/latest", help="Output directory")
    parser.add_argument(
        "--remediation-plan",
        type=str,
        default="",
        help="Optional workspace-relative path to a remediation sprint markdown file",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Return non-zero when workpack gaps are detected",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    plan_path = find_remediation_plan(repo_root, args.sprint, args.remediation_plan)
    workpack = build_workpack(repo_root, plan_path)
    write_outputs(repo_root, args.out_dir, workpack)

    print("Architecture/design authoring workpack generated:")
    print(f"- Plan: {plan_path.as_posix()}")
    print(f"- Requirement IDs: {len(workpack['requirement_ids'])}")
    print(f"- Architecture/design targets: {len(workpack['architecture_targets'])}")
    print(f"- Implementation targets: {len(workpack['implementation_targets'])}")
    print(f"- Verification targets: {len(workpack['verification_targets'])}")
    print(f"- Gaps: {len(workpack['gaps'])}")
    if args.enforce and workpack["gaps"]:
        print("Architecture/design authoring workpack enforcement failed due to detected gaps.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

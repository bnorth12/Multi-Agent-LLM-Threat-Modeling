import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List


GENERIC_ID_RE = re.compile(r"\b(?:C\d{2}-[A-Z0-9-]+|[A-Z]{2,}-\d+[A-Z]?)\b")
CAPABILITY_ID_RE = re.compile(r"\bC\d{2}-[A-Z0-9-]+\b")
FUNCTION_PREFIXES = (
    "GUI-",
    "HITL-",
    "RIC-",
    "RHMI-",
    "ORCH-",
    "INT-",
    "ADM-",
    "PRJ-",
)


def find_remediation_plans(repo_root: Path, sprint: str, explicit_path: str) -> List[Path]:
    if explicit_path:
        candidate = repo_root / explicit_path
        if candidate.exists():
            return [candidate]
        raise FileNotFoundError(f"Remediation plan not found: {candidate.as_posix()}")

    patterns = [
        "planning/Sprint_Remediation_*.md",
        f"planning/Sprint_{sprint}_Remediation_*.md",
    ]
    discovered: List[Path] = []
    for pattern in patterns:
        discovered.extend(sorted(repo_root.glob(pattern)))

    unique_plans: List[Path] = []
    seen: set[str] = set()
    for candidate in discovered:
        key = candidate.as_posix()
        if key in seen:
            continue
        seen.add(key)
        unique_plans.append(candidate)

    if unique_plans:
        return unique_plans

    raise FileNotFoundError(f"No remediation plan matches: {', '.join(patterns)}")


def canonical_plan_priority(plan_path: Path) -> tuple[int, str]:
    name = plan_path.name
    # Prefer canonical issue-scoped plan naming when multiple files model the same slice.
    if name.startswith("Sprint_Remediation_"):
        return (0, name)
    return (1, name)


def parse_targets(lines: List[str]) -> Dict[str, List[str]]:
    targets: Dict[str, List[str]] = {
        "architecture": [],
        "design": [],
        "implementation": [],
        "verification": [],
    }
    capture = False
    for line in lines:
        stripped = line.strip()
        if stripped == "## Evidence Targets":
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if not capture or not stripped.startswith("- "):
            continue
        item = stripped[2:].strip()
        if item.startswith(("docs/architecture/", "docs/system/")):
            targets["architecture"].append(item)
        elif item.startswith("docs/design/"):
            targets["design"].append(item)
        elif item.startswith(("src/", "frontend/src/", "scripts/")):
            targets["implementation"].append(item)
        elif item.startswith(("Tests/", "test_reports/")):
            targets["verification"].append(item)
    return targets


def extract_chain_notes(plan_text: str) -> Dict[str, Any]:
    all_ids = sorted(set(GENERIC_ID_RE.findall(plan_text)))
    capability_ids = sorted(set(CAPABILITY_ID_RE.findall(plan_text)))
    function_ids = sorted(
        {
            item
            for item in all_ids
            if item.startswith(FUNCTION_PREFIXES)
        }
    )
    requirement_ids = sorted(
        {
            item
            for item in all_ids
            if item not in capability_ids and item not in function_ids
        }
    )
    if not requirement_ids and function_ids:
        # Some remediation slices encode governing requirements using function-level IDs.
        requirement_ids = function_ids.copy()
    issue_match = re.search(r"GitHub issue:\s*#(\d+)", plan_text)
    tracker_match = re.search(r"Sprint tracker key:\s*(S\d{2}-\d+)", plan_text)
    title_match = re.search(r"Title:\s*(.+)", plan_text)
    return {
        "capability_ids": capability_ids,
        "function_ids": function_ids,
        "requirement_ids": requirement_ids,
        "issue_id": f"#{issue_match.group(1)}" if issue_match else (requirement_ids[0] if requirement_ids else ""),
        "tracker_key": tracker_match.group(1) if tracker_match else "",
        "title": title_match.group(1).strip() if title_match else "",
    }


def select_path(architecture: List[str], design: List[str], implementation: List[str]) -> Dict[str, str]:
    if implementation and not (architecture or design):
        return {
            "path": "implementation-first reconciliation",
            "rationale": "Implementation targets exist but no issue-scoped architecture/design artifact is yet present, so the design layer must reconcile to the as-built implementation before closeout.",
        }
    if architecture and not implementation:
        return {
            "path": "architecture-first",
            "rationale": "Architecture targets are established and code changes have not been scoped as the primary driver, so implementation should be brought into conformance with architecture intent.",
        }
    if design and not implementation:
        return {
            "path": "design-first",
            "rationale": "Software design targets exist without implementation targets dominating the remediation scope, so implementation should follow the design baseline.",
        }
    if implementation:
        return {
            "path": "implementation-first reconciliation",
            "rationale": "Implementation targets are in scope and the issue-specific disposition package must reconcile architecture/design to the as-built code before the review chain can close.",
        }
    return {
        "path": "architecture-first",
        "rationale": "No explicit implementation targets were detected; defaulting to the architecture baseline.",
    }


def remediation_actions_for_missing_legs(missing_legs: List[str]) -> List[Dict[str, str]]:
    action_map = {
        "capability": "Map governing capability IDs and add them to sprint evidence targets and issue-scoped disposition artifacts.",
        "function": "Map governing function IDs and link them to requirement and design references before closeout.",
        "requirement": "Establish explicit requirement IDs for this slice and update tracker plus traceability matrix references.",
        "architecture": "Author or update architecture references that explain the as-built behavior for the selected path.",
        "design": "Author or update design references so implementation behavior is constrained and reviewer-auditable.",
        "implementation": "Identify and execute focused implementation deltas that satisfy requirement and design intent.",
        "verification": "Add and run automated/manual verification artifacts proving the final chain state.",
    }
    actions: List[Dict[str, str]] = []
    for leg in missing_legs:
        actions.append(
            {
                "missing_leg": leg,
                "required_action": action_map.get(leg, "Define and execute a corrective action for this missing chain leg."),
            }
        )
    return actions


def build_workpack(repo_root: Path, plan_path: Path) -> Dict[str, Any]:
    lines = plan_path.read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines)
    plan_meta = extract_chain_notes(text)
    targets = parse_targets(lines)
    disposition = select_path(targets["architecture"], targets["design"], targets["implementation"])

    chain = []
    governing_ids = plan_meta["requirement_ids"] or ["unmapped-requirement"]
    for req_id in governing_ids:
        chain.append(
            {
                "capability_refs": plan_meta["capability_ids"],
                "function_refs": plan_meta["function_ids"],
                "requirement_id": req_id,
                "source_refs": [plan_path.as_posix()],
                "architecture_refs": targets["architecture"] or ["docs/architecture/HMI_Architecture_Blueprint.md"],
                "design_refs": targets["design"] or [
                    "docs/design/software/Runtime_And_Orchestration_Design_Specification.md",
                    "docs/design/software/Agent_Subsystem_Design_Specification.md",
                ],
                "implementation_refs": targets["implementation"],
                "verification_refs": targets["verification"],
                "status": "complete" if (targets["architecture"] or targets["design"]) and targets["implementation"] and targets["verification"] else "partial",
            }
        )

    missing_legs: List[str] = []
    if not plan_meta["capability_ids"]:
        missing_legs.append("capability")
    if not plan_meta["function_ids"]:
        missing_legs.append("function")
    if not plan_meta["requirement_ids"]:
        missing_legs.append("requirement")
    if not targets["architecture"]:
        missing_legs.append("architecture")
    if not targets["design"]:
        missing_legs.append("design")
    if not targets["implementation"]:
        missing_legs.append("implementation")
    if not targets["verification"]:
        missing_legs.append("verification")

    remediation_actions = remediation_actions_for_missing_legs(missing_legs)

    return {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "plan_path": plan_path.as_posix(),
        "issue_id": plan_meta["issue_id"],
        "tracker_key": plan_meta["tracker_key"],
        "title": plan_meta["title"],
        "selected_path": disposition["path"],
        "rationale": disposition["rationale"],
        "chain": chain,
        "capability_refs": plan_meta["capability_ids"],
        "function_refs": plan_meta["function_ids"],
        "architecture_refs": targets["architecture"],
        "design_refs": targets["design"],
        "implementation_refs": targets["implementation"],
        "verification_refs": targets["verification"],
        "missing_legs": missing_legs,
        "remediation_actions": remediation_actions,
    }


def write_outputs(repo_root: Path, out_dir: str, workpack: Dict[str, Any], stem: str, make_latest: bool) -> None:
    out_root = repo_root / out_dir
    out_root.mkdir(parents=True, exist_ok=True)

    json_path = out_root / f"issue_design_disposition_{stem}.json"
    md_path = out_root / f"issue_design_disposition_{stem}.md"

    json_path.write_text(json.dumps(workpack, indent=2), encoding="utf-8")

    lines: List[str] = [
        "# Issue Design / Disposition Package (Latest)",
        "",
        f"- Timestamp: {workpack['timestamp']}",
        f"- Remediation Plan: {workpack['plan_path']}",
        f"- Issue: {workpack['issue_id']} ({workpack['tracker_key']})",
        f"- Selected Reconciliation Path: {workpack['selected_path']}",
        f"- Rationale: {workpack['rationale']}",
        "",
        "## Requirement-to-Evidence Chain",
    ]

    chain = workpack["chain"]
    if chain:
        for item in chain:
            lines.extend(
                [
                    f"- {item['requirement_id']} | status={item['status']}",
                    f"  - Capability: {', '.join(item['capability_refs']) if item['capability_refs'] else 'none'}",
                    f"  - Function: {', '.join(item['function_refs']) if item['function_refs'] else 'none'}",
                    f"  - Source: {', '.join(item['source_refs'])}",
                    f"  - Architecture: {', '.join(item['architecture_refs'])}",
                    f"  - Design: {', '.join(item['design_refs'])}",
                    f"  - Implementation: {', '.join(item['implementation_refs']) if item['implementation_refs'] else 'none'}",
                    f"  - Verification: {', '.join(item['verification_refs']) if item['verification_refs'] else 'none'}",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Missing Legs",
        ]
    )
    if workpack["missing_legs"]:
        lines.extend([f"- {item}" for item in workpack["missing_legs"]])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Remediation Planning Actions",
        ]
    )
    remediation_actions = workpack.get("remediation_actions", [])
    if remediation_actions:
        for action in remediation_actions:
            lines.extend(
                [
                    f"- Missing leg: {action.get('missing_leg', 'unknown')}",
                    f"  - Required action: {action.get('required_action', 'define corrective action')}",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Approval / Closeout Notes",
            "- Selected path must be preserved in execution logs and closeout evidence.",
            "- If a future remediation is architecture-first or design-first, this artifact should show that explicitly rather than defaulting to implementation-led reconciliation.",
        ]
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")

    if make_latest:
        (out_root / "issue_design_disposition_latest.json").write_text(json.dumps(workpack, indent=2), encoding="utf-8")
        (out_root / "issue_design_disposition_latest.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an issue-level architecture/design disposition package")
    parser.add_argument("--sprint", type=str, default="2026_12", help="Sprint identifier (YYYY_MM)")
    parser.add_argument("--out-dir", type=str, default="local_reviews/latest", help="Output directory")
    parser.add_argument(
        "--remediation-plan",
        type=str,
        default="",
        help="Optional workspace-relative path to a remediation sprint markdown file",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    plan_paths = find_remediation_plans(repo_root, args.sprint, args.remediation_plan)
    plan_paths = sorted(plan_paths, key=canonical_plan_priority)
    combined_index: List[Dict[str, Any]] = []
    seen_slices: set[tuple[str, str]] = set()

    for plan_path in plan_paths:
        workpack = build_workpack(repo_root, plan_path)
        slice_key = (workpack.get("issue_id", ""), workpack.get("tracker_key", ""))
        if slice_key in seen_slices:
            continue
        seen_slices.add(slice_key)
        stem = plan_path.stem
        combined_index.append(
            {
                "plan_path": plan_path.as_posix(),
                "issue_id": workpack["issue_id"],
                "tracker_key": workpack["tracker_key"],
                "selected_path": workpack["selected_path"],
                "missing_legs": workpack["missing_legs"],
                "artifact_stem": stem,
                "workpack": workpack,
            }
        )

    for index, item in enumerate(combined_index, start=1):
        write_outputs(
            repo_root,
            args.out_dir,
            item["workpack"],
            stem=item["artifact_stem"],
            make_latest=index == len(combined_index),
        )

    out_root = repo_root / args.out_dir
    out_root.mkdir(parents=True, exist_ok=True)
    index_json = out_root / "issue_design_disposition_index.json"
    index_md = out_root / "issue_design_disposition_index.md"
    index_json.write_text(
        json.dumps(
            {
                "plans": [
                    {
                        "plan_path": item["plan_path"],
                        "issue_id": item["issue_id"],
                        "tracker_key": item["tracker_key"],
                        "selected_path": item["selected_path"],
                        "missing_legs": item["missing_legs"],
                        "artifact_stem": item["artifact_stem"],
                    }
                    for item in combined_index
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    index_lines = [
        "# Issue Design / Disposition Index",
        "",
        f"- Sprint: {args.sprint}",
        f"- Plan count: {len(combined_index)}",
        "",
        "## Generated Artifacts",
    ]
    for item in combined_index:
        index_lines.extend(
            [
                f"- {item['artifact_stem']}",
                f"  - Plan: {item['plan_path']}",
                f"  - Issue: {item['issue_id']} ({item['tracker_key']})",
                f"  - Selected path: {item['selected_path']}",
                f"  - Missing legs: {', '.join(item['missing_legs']) if item['missing_legs'] else 'none'}",
            ]
        )
    index_md.write_text("\n".join(index_lines), encoding="utf-8")

    print("Issue design/disposition packages generated:")
    for item in combined_index:
        print(f"- Plan: {item['plan_path']}")
        print(f"  Issue: {item['issue_id']} ({item['tracker_key']})")
        print(f"  Selected path: {item['selected_path']}")
        print(f"  Missing legs: {', '.join(item['missing_legs']) if item['missing_legs'] else 'none'}")
        print(f"  Artifact stem: {item['artifact_stem']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

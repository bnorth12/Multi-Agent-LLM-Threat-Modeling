#!/usr/bin/env python3
"""Triages unimplemented requirements into needed vs deletion candidates.

Outputs:
- independent_reviews/latest/unimplemented_requirement_triage_<target_sprint>.json
- independent_reviews/latest/unimplemented_requirement_triage_<target_sprint>.md
- planning/work_items/Unimplemented_Requirements_Backlog.md (upserted auto section)
- planning/issues/Sprint_<target_sprint>_Issue_Tracker.md (upserted auto section)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

AUTO_SECTION_START = "<!-- AUTO-UNIMPLEMENTED-TRIAGE:START -->"
AUTO_SECTION_END = "<!-- AUTO-UNIMPLEMENTED-TRIAGE:END -->"
BACKLOG_SECTION_START = "<!-- AUTO-UNIMPLEMENTED-BACKLOG:START -->"
BACKLOG_SECTION_END = "<!-- AUTO-UNIMPLEMENTED-BACKLOG:END -->"

TRACKER_HEADER = (
    "| ID | GitHub Issue | Type | Priority | Status | Summary | Related Requirements | Primary Files |"
)
TRACKER_DIVIDER = "|---|---|---|---|---|---|---|---|"

BACKLOG_COLUMNS = [
    "Backlog Key",
    "Requirement ID",
    "Name",
    "Level",
    "Scope",
    "Source",
    "Status",
    "Target Sprint",
    "GitHub Issue",
    "Notes",
]

REQ_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")

PREFIX_METADATA: Dict[str, Dict[str, str]] = {
    "PRJ": {"level": "System/Project", "scope": "Threat Modeler platform"},
    "INT": {"level": "Interface Contract", "scope": "Cross-component interfaces"},
    "C01": {"level": "Subsystem Component", "scope": "Orchestrator and state management"},
    "C02": {"level": "Agent Component", "scope": "Agent 1 Input Normalizer"},
    "C03": {"level": "Agent Component", "scope": "Agent 2 Context Builder"},
    "C04": {"level": "Agent Component", "scope": "Agent 3 Trust Boundary Analyzer"},
    "C05": {"level": "Agent Component", "scope": "Agent 4 STRIDE Scoring"},
    "C06": {"level": "Agent Component", "scope": "Agent 5 Threat Generation"},
    "C07": {"level": "Agent Component", "scope": "Agent 6 STIX Packaging"},
    "C08": {"level": "Agent Component", "scope": "Agent 7 Mitigation Mapping"},
    "C09": {"level": "Agent Component", "scope": "Agent 8 Diagram Generation"},
    "C10": {"level": "Agent Component", "scope": "Agent 9 Report Generation"},
    "C11": {"level": "Subsystem Component", "scope": "Model adapter and provider selection"},
    "C12": {"level": "Subsystem Component", "scope": "HITL gate and audit services"},
    "GUI": {"level": "UI Requirement", "scope": "Operator GUI/HMI"},
    "RHMI": {"level": "UI/API Requirement", "scope": "React HMI and backend API"},
    "HITL": {"level": "Workflow Requirement", "scope": "Human-in-the-loop gates and state"},
    "ADM": {"level": "Process/Governance", "scope": "Administration governance controls"},
    "VS": {"level": "Verification Requirement", "scope": "Verification strategy and evidence"},
    "RIC": {"level": "Runtime Contract", "scope": "Runtime state and input contracts"},
    "PRM": {"level": "Prompt Governance", "scope": "Prompt authoring and behavior controls"},
    "SCR": {"level": "Sprint Registry", "scope": "Sprint tracking status entries"},
}


def sprint_tokens(sprint: str) -> Tuple[str, str]:
    return sprint.replace("_", "-"), sprint.replace("-", "_")


def review_json_path(repo_root: Path, sprint: str, explicit: str) -> Path:
    if explicit:
        path = Path(explicit)
        return path if path.is_absolute() else repo_root / path
    sprint_dash, _ = sprint_tokens(sprint)
    return repo_root / "independent_reviews" / "latest" / f"independent_review_{sprint_dash}_pre-push.json"


def compact(text: str, limit: int = 170) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def md_escape(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def parse_bl_keys(raw_keys: List[str]) -> List[str]:
    keys: List[str] = []
    for raw in raw_keys:
        for part in raw.split(","):
            key = part.strip()
            if key:
                keys.append(key)
    deduped: List[str] = []
    for key in keys:
        if key not in deduped:
            deduped.append(key)
    return deduped


def parse_table_row(line: str) -> List[str]:
    if not line.startswith("|"):
        return []
    parts = [p.strip() for p in line.strip().strip("|").split("|")]
    return parts


def read_backlog_entries(backlog_path: Path) -> Tuple[str, str, List[Dict[str, str]]]:
    text = backlog_path.read_text(encoding="utf-8") if backlog_path.exists() else ""
    if BACKLOG_SECTION_START not in text or BACKLOG_SECTION_END not in text:
        return text, "", []

    section = text.split(BACKLOG_SECTION_START, 1)[1].split(BACKLOG_SECTION_END, 1)[0]
    entries: List[Dict[str, str]] = []
    for raw in section.splitlines():
        line = raw.strip()
        if not line.startswith("| BL-"):
            continue
        values = parse_table_row(line)
        if len(values) != len(BACKLOG_COLUMNS):
            continue
        row = {BACKLOG_COLUMNS[idx]: values[idx] for idx in range(len(BACKLOG_COLUMNS))}
        entries.append(row)
    return text, section, entries


def render_backlog_section_lines(now_iso: str, source_sprint: str, entries: List[Dict[str, str]]) -> List[str]:
    lines = [
        "## Automated Backlog Intake",
        "",
        f"- Last generated: {now_iso}",
        f"- Source sprint review: {source_sprint}",
        f"- Needed + unimplemented items: {len(entries)}",
        "",
        "| " + " | ".join(BACKLOG_COLUMNS) + " |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in entries:
        lines.append("| " + " | ".join(md_escape(row.get(col, "")) for col in BACKLOG_COLUMNS) + " |")
    return lines


def upsert_backlog_section(backlog_text: str, section_lines: List[str]) -> str:
    block = "\n".join([BACKLOG_SECTION_START, *section_lines, BACKLOG_SECTION_END])
    if BACKLOG_SECTION_START in backlog_text and BACKLOG_SECTION_END in backlog_text:
        before = backlog_text.split(BACKLOG_SECTION_START, 1)[0].rstrip()
        after = backlog_text.split(BACKLOG_SECTION_END, 1)[1].lstrip()
        return f"{before}\n\n{block}\n\n{after}".rstrip() + "\n"
    return backlog_text.rstrip() + "\n\n" + block + "\n"


def source_hint(source_refs: List[str]) -> str:
    if not source_refs:
        return "n/a"
    first = source_refs[0].replace("\\", "/")
    token = "/Requirements/"
    idx = first.find(token)
    if idx >= 0:
        return first[idx + 1 :]
    return Path(first).name


def normalize_prefix(req_id: str) -> str:
    return req_id.split("-", 1)[0] if "-" in req_id else req_id


def metadata_from_requirement(req_id: str, description: str, source_refs: List[str]) -> Dict[str, str]:
    major = req_id.split("-", 1)[0] if "-" in req_id else req_id
    major = major if major in PREFIX_METADATA else normalize_prefix(req_id)
    if major.startswith("C") and major not in PREFIX_METADATA:
        major = "C01"

    meta = PREFIX_METADATA.get(major, {"level": "Requirement", "scope": "General system behavior"})

    if " SHALL " in description:
        lhs, rhs = description.split(" SHALL ", 1)
        rhs = rhs.rstrip(".").strip()
        name = f"{lhs.strip()}: {compact(rhs, 92)}"
    elif "|" in description:
        name = description.split("|", 1)[0].strip() or req_id
    else:
        name = compact(description, 72)

    if not name:
        name = req_id

    return {
        "requirement_name": name,
        "requirement_level": meta["level"],
        "requirement_scope": meta["scope"],
        "source_hint": source_hint(source_refs),
    }


def issue_slug(req_id: str) -> str:
    return req_id.replace("-", "_")


def build_backlog_entry(item: Dict[str, str], target_sprint: str, idx: int) -> Dict[str, str]:
    backlog_key = f"BL-{target_sprint[-3:]}-{idx:03d}"
    title = f"Backlog candidate for {item['requirement_id']} implementation"
    return {
        "backlog_key": backlog_key,
        "requirement_id": item["requirement_id"],
        "title": title,
        "summary": compact(item["description"], 120),
        "requirement_name": item["requirement_name"],
        "requirement_level": item["requirement_level"],
        "requirement_scope": item["requirement_scope"],
        "source_hint": item["source_hint"],
    }


def triage_reason_unneeded(req_id: str, description: str) -> str:
    desc = description.strip()
    lower = desc.lower()

    if not REQ_ID_PATTERN.match(req_id):
        return "non-standard requirement identifier format"

    if "00x" in req_id.lower():
        return "placeholder requirement identifier"

    if req_id in {"INT-10", "INT-11"}:
        return "legacy transitional alias; prefer canonical zero-padded INT IDs"

    if desc.endswith(".md") and "shall" not in lower:
        return "document pointer entry rather than a normative requirement"

    if any(token in lower for token in ["delivered", "in progress", "active", "deferred", "s07-"]):
        return "status-marker entry rather than a normative requirement"

    if "|" in desc and "shall" not in lower:
        return "compound status/contract row not normalized as a requirement statement"

    return ""


def classify_requirement(req_id: str, description: str) -> Dict[str, str]:
    unneeded_reason = triage_reason_unneeded(req_id, description)
    if unneeded_reason:
        return {"classification": "deletion-candidate", "reason": unneeded_reason}

    return {
        "classification": "needed-unimplemented",
        "reason": "normative requirement appears active but lacks implementation evidence",
    }


def build_issue_draft(req_id: str, description: str, target_sprint: str, idx: int) -> Dict[str, str]:
    short = compact(description, 120)
    issue_key = f"S99-{idx:03d}"
    title = f"[{target_sprint}] Implement {req_id} trace-backed delivery"
    body = (
        f"Requirement {req_id} is currently classified as needed but unimplemented by automated triage.\n\n"
        f"Requirement text:\n{description}\n\n"
        "Plan:\n"
        "1. Confirm architecture/design allocation in authoritative docs.\n"
        "2. Implement or wire delivery code in the owning module.\n"
        "3. Add executable verification evidence (test or qualification evidence).\n"
        "4. Update traceability matrices and rerun governance autoflow.\n"
    )
    issue_file = f"planning/issues/issue_{target_sprint}_{issue_key}_{issue_slug(req_id)}.md"

    return {
        "issue_key": issue_key,
        "title": title,
        "summary": short,
        "requirement_id": req_id,
        "issue_body": body,
        "issue_file": issue_file,
    }


def upsert_section(text: str, section_lines: List[str]) -> str:
    block = "\n".join([AUTO_SECTION_START, *section_lines, AUTO_SECTION_END])
    if AUTO_SECTION_START in text and AUTO_SECTION_END in text:
        before = text.split(AUTO_SECTION_START, 1)[0].rstrip()
        after = text.split(AUTO_SECTION_END, 1)[1].lstrip()
        return f"{before}\n\n{block}\n\n{after}".rstrip() + "\n"
    return text.rstrip() + "\n\n" + block + "\n"


def tracker_preamble(target_sprint: str, now_iso: str) -> str:
    return "\n".join(
        [
            f"# Sprint {target_sprint} Issue Tracker",
            "",
            f"Date: {now_iso[:10]}",
            "Status: Open",
            "Sprint Goal: Close needed unimplemented requirements and triage deletion candidates.",
            "",
            "## Active Issues",
            "",
            TRACKER_HEADER,
            TRACKER_DIVIDER,
            "",
            "## Closure Policy",
            "",
            "A sprint issue may be closed only when implementation, verification, and traceability evidence are all present.",
        ]
    )


def build_tracker_auto_section(issue_drafts: List[Dict[str, str]]) -> List[str]:
    lines = [
        "## Automated Intake Candidates (Needed + Unimplemented)",
        "",
        TRACKER_HEADER,
        TRACKER_DIVIDER,
    ]

    for draft in issue_drafts:
        lines.append(
            "| "
            + " | ".join(
                [
                    draft["issue_key"],
                    "TBA",
                    "Remediation / Implementation",
                    "P0",
                    "Planned",
                    draft["summary"].replace("|", "\\|"),
                    draft["requirement_id"],
                    draft["issue_file"],
                ]
            )
            + " |"
        )

    if not issue_drafts:
        lines.append("| S99-000 | TBA | Remediation / Implementation | P1 | Planned | No needed unimplemented requirements were found by triage. | n/a | n/a |")

    lines.extend(
        [
            "",
            "## Automated Deletion Candidates",
            "",
            "See independent_reviews/latest/unimplemented_requirement_triage_2026_099.md for deletion-candidate rationale.",
        ]
    )
    return lines


def tracker_section_from_backlog(entries: List[Dict[str, str]], sprint: str) -> List[str]:
    rows = [row for row in entries if row.get("Target Sprint") == sprint and row.get("Status") != "Backlog"]
    lines = [
        "## Automated Intake Candidates (Needed + Unimplemented)",
        "",
        TRACKER_HEADER,
        TRACKER_DIVIDER,
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("Backlog Key", ""),
                    row.get("GitHub Issue", "Deferred"),
                    "Remediation / Implementation",
                    "P0",
                    row.get("Status", "Planned"),
                    compact(row.get("Name", ""), 120),
                    row.get("Requirement ID", ""),
                    f"planning/issues/issue_{sprint}_{row.get('Backlog Key', '').replace('-', '_')}_{row.get('Requirement ID', '').replace('-', '_')}.md",
                ]
            )
            + " |"
        )
    if not rows:
        lines.append(
            "| BL-000 | Deferred (Backlog) | Remediation / Implementation | P1 | Backlog | No sprint-committed backlog candidates selected. | n/a | planning/work_items/Unimplemented_Requirements_Backlog.md |"
        )
    lines.extend(
        [
            "",
            "## Automated Deletion Candidates",
            "",
            "See independent_reviews/latest/unimplemented_requirement_triage_2026_099.md for deletion-candidate rationale.",
        ]
    )
    return lines


def load_latest_triage_details(repo_root: Path) -> Dict[str, Dict[str, str]]:
    triage_files = sorted((repo_root / "independent_reviews" / "latest").glob("unimplemented_requirement_triage_*.json"))
    if not triage_files:
        return {}
    latest = triage_files[-1]
    payload = json.loads(latest.read_text(encoding="utf-8"))
    details: Dict[str, Dict[str, str]] = {}
    for item in payload.get("needed_unimplemented", []):
        req_id = item.get("requirement_id")
        if not req_id:
            continue
        details[req_id] = item
    return details


def suggested_action_for_backlog_to_github(executed: bool, issue_ref: str) -> str:
    if executed and issue_ref.startswith("#"):
        return "Validate labels/body in GitHub and keep status as GitHub Created."
    if issue_ref.startswith("Failed:"):
        return "Fix gh auth/labels or command error, then rerun backlog-to-github for this BL key."
    if not executed:
        return "Human-review this row and rerun backlog-to-github with --execute-gh when approved."
    return "Review result details and rerun backlog-to-github for this BL key if needed."


def render_backlog_to_github_plan_md(
    *,
    now_iso: str,
    execute_gh: bool,
    github_repo: str,
    selected_bl_keys: List[str],
    created_rows: List[Dict[str, str]],
    details_by_req: Dict[str, Dict[str, str]],
) -> str:
    created_count = sum(1 for row in created_rows if str(row.get("github_issue", "")).startswith("#"))
    failed_count = sum(1 for row in created_rows if str(row.get("github_issue", "")).startswith("Failed:"))

    lines: List[str] = [
        "# Backlog To GitHub Plan",
        "",
        f"- Generated: {now_iso}",
        "- Mode: backlog-to-github",
        f"- Execute gh: {execute_gh}",
        f"- GitHub repo override: {github_repo or 'default gh context'}",
        f"- Selected BL keys: {len(selected_bl_keys)}",
        f"- Processed rows: {len(created_rows)}",
        f"- Created issue refs: {created_count}",
        f"- Failed rows: {failed_count}",
        "",
        "## Human Review Checklist",
        "",
        "1. Confirm requirement metadata (name, level, scope, text) matches source intent.",
        "2. Confirm suggested action aligns with current state before changing status.",
        "3. Confirm GitHub issue refs and sprint labels are correct for each row.",
        "",
        "## Row-Level Plan",
        "",
        "| Backlog Key | Requirement ID | Name | Level | Scope | Source | Requirement Text | Target Sprint | GitHub Issue | Suggested Action |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    for row in created_rows:
        req_id = row.get("requirement_id", "")
        detail = details_by_req.get(req_id, {})
        req_text = detail.get("description", "")
        req_name = detail.get("requirement_name", "")
        req_level = detail.get("requirement_level", "")
        req_scope = detail.get("requirement_scope", "")
        req_source = detail.get("source_hint", "")
        issue_ref = row.get("github_issue", "")
        action = suggested_action_for_backlog_to_github(bool(row.get("executed")), issue_ref)

        lines.append(
            "| "
            + " | ".join(
                [
                    md_escape(row.get("backlog_key", "")),
                    md_escape(req_id),
                    md_escape(req_name),
                    md_escape(req_level),
                    md_escape(req_scope),
                    md_escape(req_source),
                    md_escape(req_text),
                    md_escape(row.get("target_sprint", "")),
                    md_escape(issue_ref),
                    md_escape(action),
                ]
            )
            + " |"
        )

    if not created_rows:
        lines.append("| n/a | n/a | none | n/a | n/a | n/a | n/a | n/a | n/a | No rows processed. |")

    lines.extend(["", "## Selected Backlog Keys", ""])
    for key in selected_bl_keys:
        lines.append(f"- {key}")
    if not selected_bl_keys:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def run_backlog_to_sprint(repo_root: Path, args: argparse.Namespace) -> int:
    bl_keys = parse_bl_keys(args.bl_keys)
    if not bl_keys:
        raise SystemExit("--bl-keys is required for mode backlog-to-sprint")
    if not args.commit_sprint:
        raise SystemExit("--commit-sprint is required for mode backlog-to-sprint")

    backlog_path = repo_root / "planning" / "work_items" / "Unimplemented_Requirements_Backlog.md"
    backlog_text, _section, entries = read_backlog_entries(backlog_path)
    if not entries:
        raise SystemExit(f"No backlog entries found in {backlog_path.as_posix()}")

    selected = [row for row in entries if row.get("Backlog Key") in bl_keys]
    if not selected:
        raise SystemExit("No matching BL keys were found in backlog")

    details_by_req = load_latest_triage_details(repo_root)
    sprint_us = args.commit_sprint.replace("-", "_")
    issues_dir = repo_root / "planning" / "issues"
    issues_dir.mkdir(parents=True, exist_ok=True)

    for row in entries:
        if row.get("Backlog Key") in bl_keys:
            row["Status"] = "Sprint Committed"
            row["Target Sprint"] = sprint_us
            if row.get("GitHub Issue", "").strip().lower() in {"deferred", "draft ready", ""}:
                row["GitHub Issue"] = "Pending Create"

    for row in selected:
        req_id = row.get("Requirement ID", "")
        detail = details_by_req.get(req_id, {})
        issue_stub = issues_dir / f"issue_{sprint_us}_{row.get('Backlog Key', '').replace('-', '_')}_{req_id.replace('-', '_')}.md"
        issue_stub.write_text(
            "\n".join(
                [
                    f"# {row.get('Backlog Key')} - {req_id}",
                    "",
                    f"Sprint: {sprint_us}",
                    f"Status: Sprint Committed",
                    f"GitHub Issue: Pending Create",
                    f"Requirement Level: {row.get('Level', '')}",
                    f"Requirement Scope: {row.get('Scope', '')}",
                    f"Requirement Source: {row.get('Source', '')}",
                    "",
                    "## Requirement Summary",
                    "",
                    f"- Name: {row.get('Name', '')}",
                    f"- ID: {req_id}",
                    f"- Text: {detail.get('description', '')}",
                    "",
                    "## Planned Work",
                    "",
                    "1. Confirm architecture/design allocation.",
                    "2. Implement requirement in owning module.",
                    "3. Add verification evidence.",
                    "4. Update traceability and rerun governance autoflow.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    now_iso = dt.datetime.now().isoformat(timespec="seconds")
    section_lines = render_backlog_section_lines(now_iso=now_iso, source_sprint=args.sprint or "n/a", entries=entries)
    backlog_path.write_text(upsert_backlog_section(backlog_text, section_lines), encoding="utf-8")

    tracker_path = repo_root / "planning" / "issues" / f"Sprint_{sprint_us}_Issue_Tracker.md"
    if tracker_path.exists():
        tracker_text = tracker_path.read_text(encoding="utf-8")
    else:
        tracker_text = tracker_preamble(sprint_us, now_iso)
    tracker_text = upsert_section(tracker_text, tracker_section_from_backlog(entries, sprint_us))
    tracker_path.write_text(tracker_text, encoding="utf-8")

    print("Backlog-to-sprint complete:")
    print(f"- Commit sprint: {sprint_us}")
    print(f"- Selected BL keys: {', '.join(bl_keys)}")
    print(f"- Updated backlog: {backlog_path.as_posix()}")
    print(f"- Updated tracker: {tracker_path.as_posix()}")
    print(f"- Issue stubs written under: {issues_dir.as_posix()}")
    return 0


def run_backlog_to_github(repo_root: Path, args: argparse.Namespace) -> int:
    bl_keys = parse_bl_keys(args.bl_keys)
    if not bl_keys:
        raise SystemExit("--bl-keys is required for mode backlog-to-github")

    backlog_path = repo_root / "planning" / "work_items" / "Unimplemented_Requirements_Backlog.md"
    backlog_text, _section, entries = read_backlog_entries(backlog_path)
    if not entries:
        raise SystemExit(f"No backlog entries found in {backlog_path.as_posix()}")

    selected = [row for row in entries if row.get("Backlog Key") in bl_keys]
    if not selected:
        raise SystemExit("No matching BL keys were found in backlog")

    details_by_req = load_latest_triage_details(repo_root)
    now_stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_path = repo_root / "independent_reviews" / "latest" / f"backlog_to_github_plan_{now_stamp}.json"
    plan_md_path = repo_root / "independent_reviews" / "latest" / f"backlog_to_github_plan_{now_stamp}.md"

    created: List[Dict[str, str]] = []
    for row in selected:
        req_id = row.get("Requirement ID", "")
        sprint_target = row.get("Target Sprint", "")
        if row.get("Status") != "Sprint Committed":
            continue
        if args.commit_sprint and sprint_target != args.commit_sprint.replace("-", "_"):
            continue

        detail = details_by_req.get(req_id, {})
        title = f"[{sprint_target}] Implement {req_id} ({row.get('Backlog Key')})"
        body = (
            f"Backlog key: {row.get('Backlog Key')}\n"
            f"Requirement ID: {req_id}\n"
            f"Level: {row.get('Level')}\n"
            f"Scope: {row.get('Scope')}\n"
            f"Source: {row.get('Source')}\n\n"
            f"Requirement text:\n{detail.get('description', '')}\n"
        )

        issue_ref = "Draft Ready"
        if args.execute_gh:
            cmd = ["gh", "issue", "create", "--title", title, "--body", body, "--label", "backlog"]
            if sprint_target:
                cmd.extend(["--label", f"sprint-{sprint_target}"])
            if args.github_repo:
                cmd.extend(["-R", args.github_repo])
            proc = subprocess.run(cmd, cwd=str(repo_root), text=True, capture_output=True, check=False)
            if proc.returncode == 0:
                out = proc.stdout.strip()
                issue_ref = out.rsplit("/", 1)[-1] if out else "Created"
                if issue_ref.isdigit():
                    issue_ref = f"#{issue_ref}"
            else:
                issue_ref = f"Failed: {proc.stderr.strip()[:120]}"

        row["GitHub Issue"] = issue_ref
        row["Status"] = "GitHub Created" if args.execute_gh and issue_ref.startswith("#") else "Sprint Committed"
        created.append(
            {
                "backlog_key": row.get("Backlog Key", ""),
                "requirement_id": req_id,
                "target_sprint": sprint_target,
                "title": title,
                "github_issue": issue_ref,
                "executed": bool(args.execute_gh),
            }
        )

    now_iso = dt.datetime.now().isoformat(timespec="seconds")
    plan_payload = {
        "generated_at": now_iso,
        "mode": "backlog-to-github",
        "execute_gh": bool(args.execute_gh),
        "github_repo": args.github_repo,
        "selected_bl_keys": bl_keys,
        "results": created,
    }
    plan_path.write_text(json.dumps(plan_payload, indent=2), encoding="utf-8")
    plan_md_path.write_text(
        render_backlog_to_github_plan_md(
            now_iso=now_iso,
            execute_gh=bool(args.execute_gh),
            github_repo=args.github_repo,
            selected_bl_keys=bl_keys,
            created_rows=created,
            details_by_req=details_by_req,
        ),
        encoding="utf-8",
    )

    section_lines = render_backlog_section_lines(now_iso=now_iso, source_sprint=args.sprint or "n/a", entries=entries)
    backlog_path.write_text(upsert_backlog_section(backlog_text, section_lines), encoding="utf-8")

    tracker_sprints = sorted({row.get("Target Sprint", "") for row in selected if row.get("Target Sprint", "")})
    for sprint_us in tracker_sprints:
        tracker_path = repo_root / "planning" / "issues" / f"Sprint_{sprint_us}_Issue_Tracker.md"
        if tracker_path.exists():
            tracker_text = tracker_path.read_text(encoding="utf-8")
        else:
            tracker_text = tracker_preamble(sprint_us, now_iso)
        tracker_text = upsert_section(tracker_text, tracker_section_from_backlog(entries, sprint_us))
        tracker_path.write_text(tracker_text, encoding="utf-8")

    print("Backlog-to-github complete:")
    print(f"- Selected BL keys: {', '.join(bl_keys)}")
    print(f"- GitHub execution enabled: {bool(args.execute_gh)}")
    print(f"- Updated backlog: {backlog_path.as_posix()}")
    print(f"- Wrote plan: {plan_path.as_posix()}")
    print(f"- Wrote human-readable plan: {plan_md_path.as_posix()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Triages unimplemented requirements and generates sprint intake plans")
    parser.add_argument(
        "--mode",
        choices=["triage", "backlog-to-sprint", "backlog-to-github"],
        default="triage",
        help="Workflow mode: triage, backlog-to-sprint, or backlog-to-github",
    )
    parser.add_argument("--sprint", default="", help="Source sprint for independent review input (e.g., 2026_013)")
    parser.add_argument(
        "--target-sprint",
        default="2026_099",
        help="Target sprint for generated issue plans (default: 2026_099)",
    )
    parser.add_argument("--commit-sprint", default="", help="Sprint to commit selected backlog items into")
    parser.add_argument(
        "--bl-keys",
        nargs="*",
        default=[],
        help="Selected backlog keys (BL-xxx-yyy), supports space and comma separated values",
    )
    parser.add_argument("--execute-gh", action="store_true", help="Execute gh issue create (default is dry-run plan only)")
    parser.add_argument("--github-repo", default="", help="Optional GitHub repo override in owner/repo format")
    parser.add_argument("--review-json", default="", help="Optional path to independent review JSON")
    parser.add_argument("--max-items", type=int, default=120, help="Maximum backlog candidates to generate")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]

    if args.mode == "backlog-to-sprint":
        return run_backlog_to_sprint(repo_root, args)

    if args.mode == "backlog-to-github":
        return run_backlog_to_github(repo_root, args)

    if not args.sprint:
        raise SystemExit("--sprint is required for mode triage")

    review_path = review_json_path(repo_root, args.sprint, args.review_json)
    if not review_path.exists():
        raise SystemExit(f"Review JSON not found: {review_path.as_posix()}")

    payload = json.loads(review_path.read_text(encoding="utf-8"))
    req_desc: Dict[str, str] = payload.get("requirement_descriptions", {})
    req_trace: Dict[str, Dict[str, List[str]]] = payload.get("requirement_traceability", {})
    req_without_impl: List[str] = payload.get("req_without_impl", [])

    triaged: List[Dict[str, str]] = []
    needed: List[Dict[str, str]] = []
    deletion: List[Dict[str, str]] = []

    for req_id in sorted(dict.fromkeys(req_without_impl)):
        description = req_desc.get(req_id, "")
        trace_entry = req_trace.get(req_id, {})
        source_refs = trace_entry.get("source_refs", []) if isinstance(trace_entry, dict) else []
        metadata = metadata_from_requirement(req_id=req_id, description=description, source_refs=source_refs)
        result = classify_requirement(req_id, description)
        row = {
            "requirement_id": req_id,
            "description": description,
            "requirement_name": metadata["requirement_name"],
            "requirement_level": metadata["requirement_level"],
            "requirement_scope": metadata["requirement_scope"],
            "source_hint": metadata["source_hint"],
            "source_refs": source_refs,
            "classification": result["classification"],
            "reason": result["reason"],
        }
        triaged.append(row)
        if result["classification"] == "needed-unimplemented":
            needed.append(row)
        else:
            deletion.append(row)

    backlog_entries: List[Dict[str, str]] = []
    for idx, item in enumerate(needed[: max(0, args.max_items)], start=1):
        backlog_entries.append(build_backlog_entry(item=item, target_sprint=args.target_sprint, idx=idx))

    out_root = repo_root / "independent_reviews" / "latest"
    out_root.mkdir(parents=True, exist_ok=True)

    target_sprint_us = args.target_sprint.replace("-", "_")
    out_json = out_root / f"unimplemented_requirement_triage_{target_sprint_us}.json"
    out_md = out_root / f"unimplemented_requirement_triage_{target_sprint_us}.md"

    now_iso = dt.datetime.now().isoformat(timespec="seconds")
    out_payload = {
        "generated_at": now_iso,
        "source_sprint": args.sprint,
        "target_sprint": args.target_sprint,
        "review_source": review_path.as_posix(),
        "counts": {
            "unimplemented_total": len(req_without_impl),
            "triaged_total": len(triaged),
            "needed_unimplemented": len(needed),
            "deletion_candidates": len(deletion),
            "backlog_entries_generated": len(backlog_entries),
            "issue_drafts_generated": 0,
        },
        "needed_unimplemented": needed,
        "deletion_candidates": deletion,
        "backlog_entries": backlog_entries,
    }
    out_json.write_text(json.dumps(out_payload, indent=2), encoding="utf-8")

    lines: List[str] = [
        f"# Unimplemented Requirement Triage - Target Sprint {args.target_sprint}",
        "",
        f"- Generated: {now_iso}",
        f"- Source sprint: {args.sprint}",
        f"- Source review: {review_path.as_posix()}",
        f"- Unimplemented requirements scanned: {len(req_without_impl)}",
        f"- Needed + unimplemented: {len(needed)}",
        f"- Deletion candidates: {len(deletion)}",
        f"- Backlog entries generated: {len(backlog_entries)}",
        "- GitHub issue creation: deferred until sprint planning",
        "",
        "## Needed + Unimplemented (Backlog Candidates)",
        "",
        "| Backlog Key | Requirement ID | Name | Level | Scope | Source | Requirement Text | Reason |",
        "|---|---|---|---|---|---|---|---|",
    ]

    backlog_by_req = {d["requirement_id"]: d["backlog_key"] for d in backlog_entries}
    for item in needed:
        lines.append(
            "| "
            + " | ".join(
                [
                    backlog_by_req.get(item["requirement_id"], "n/a"),
                    item["requirement_id"],
                    md_escape(item["requirement_name"]),
                    item["requirement_level"],
                    md_escape(item["requirement_scope"]),
                    md_escape(item["source_hint"]),
                    md_escape(item["description"]),
                    md_escape(item["reason"]),
                ]
            )
            + " |"
        )

    if not needed:
        lines.append("| n/a | n/a | none | n/a | n/a | n/a | n/a | n/a |")

    lines.extend(
        [
            "",
            "## Deletion Candidates",
            "",
            "| Requirement ID | Name | Level | Scope | Source | Requirement Text | Deletion Rationale |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for item in deletion:
        lines.append(
            "| "
            + " | ".join(
                [
                    item["requirement_id"],
                    md_escape(item["requirement_name"]),
                    item["requirement_level"],
                    md_escape(item["requirement_scope"]),
                    md_escape(item["source_hint"]),
                    md_escape(item["description"]),
                    md_escape(item["reason"]),
                ]
            )
            + " |"
        )
    if not deletion:
        lines.append("| n/a | none | n/a | n/a | n/a | n/a | n/a |")

    lines.extend(["", "## Backlog Entries", ""])
    for entry in backlog_entries:
        lines.append(
            f"- {entry['backlog_key']}: {entry['title']} ({entry['requirement_id']})"
        )
    if not backlog_entries:
        lines.append("- none")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    backlog_path = repo_root / "planning" / "work_items" / "Unimplemented_Requirements_Backlog.md"
    if backlog_path.exists():
        backlog_text = backlog_path.read_text(encoding="utf-8")
    else:
        backlog_text = "\n".join(
            [
                "# Unimplemented Requirements Backlog",
                "",
                "Purpose: hold approved unimplemented requirements as backlog candidates until a sprint commits them.",
                "",
                "GitHub issue creation policy: create GitHub issues only when items are selected for a committed sprint.",
            ]
        )

    backlog_section_lines = [
        "## Automated Backlog Intake",
        "",
        f"- Last generated: {now_iso}",
        f"- Source sprint review: {args.sprint}",
        f"- Needed + unimplemented items: {len(backlog_entries)}",
        "",
        "| Backlog Key | Requirement ID | Name | Level | Scope | Source | Status | Target Sprint | GitHub Issue | Notes |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for entry in backlog_entries:
        backlog_section_lines.append(
            "| "
            + " | ".join(
                [
                    entry["backlog_key"],
                    entry["requirement_id"],
                    md_escape(entry["requirement_name"]),
                    entry["requirement_level"],
                    md_escape(entry["requirement_scope"]),
                    md_escape(entry["source_hint"]),
                    "Backlog",
                    "Unscheduled",
                    "Deferred",
                    "Approved triage candidate; promote during sprint planning.",
                ]
            )
            + " |"
        )

    backlog_block = "\n".join([BACKLOG_SECTION_START, *backlog_section_lines, BACKLOG_SECTION_END])
    if BACKLOG_SECTION_START in backlog_text and BACKLOG_SECTION_END in backlog_text:
        before = backlog_text.split(BACKLOG_SECTION_START, 1)[0].rstrip()
        after = backlog_text.split(BACKLOG_SECTION_END, 1)[1].lstrip()
        backlog_text = f"{before}\n\n{backlog_block}\n\n{after}".rstrip() + "\n"
    else:
        backlog_text = backlog_text.rstrip() + "\n\n" + backlog_block + "\n"

    backlog_path.write_text(backlog_text, encoding="utf-8")

    tracker_path = repo_root / "planning" / "issues" / f"Sprint_{target_sprint_us}_Issue_Tracker.md"
    if tracker_path.exists():
        tracker_text = tracker_path.read_text(encoding="utf-8")
    else:
        tracker_text = tracker_preamble(target_sprint_us, now_iso)

    tracker_section = [
        "## Automated Intake Candidates (Needed + Unimplemented)",
        "",
        TRACKER_HEADER,
        TRACKER_DIVIDER,
    ]
    for entry in backlog_entries:
        tracker_section.append(
            "| "
            + " | ".join(
                [
                    entry["backlog_key"],
                    "Deferred (Backlog)",
                    "Remediation / Implementation",
                    "P0",
                    "Backlog",
                    md_escape(entry["summary"]),
                    entry["requirement_id"],
                    "planning/work_items/Unimplemented_Requirements_Backlog.md",
                ]
            )
            + " |"
        )
    if not backlog_entries:
        tracker_section.append(
            "| BL-000 | Deferred (Backlog) | Remediation / Implementation | P1 | Backlog | No needed unimplemented requirements were found by triage. | n/a | planning/work_items/Unimplemented_Requirements_Backlog.md |"
        )
    tracker_section.extend(
        [
            "",
            "## Automated Deletion Candidates",
            "",
            "See independent_reviews/latest/unimplemented_requirement_triage_2026_099.md for deletion-candidate rationale.",
        ]
    )
    tracker_path.write_text(upsert_section(tracker_text, tracker_section), encoding="utf-8")

    print("Unimplemented requirement triage complete:")
    print(f"- Source review: {review_path.as_posix()}")
    print(f"- Target sprint: {args.target_sprint}")
    print(f"- Unimplemented scanned: {len(req_without_impl)}")
    print(f"- Needed + unimplemented: {len(needed)}")
    print(f"- Deletion candidates: {len(deletion)}")
    print(f"- Backlog entries generated: {len(backlog_entries)}")
    print("- GitHub issue creation deferred until sprint planning")
    print(f"- Wrote: {out_json.as_posix()}")
    print(f"- Wrote: {out_md.as_posix()}")
    print(f"- Updated: {backlog_path.as_posix()}")
    print(f"- Updated: {tracker_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

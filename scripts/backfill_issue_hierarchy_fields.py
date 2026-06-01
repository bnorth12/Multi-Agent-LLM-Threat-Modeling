#!/usr/bin/env python3
"""Backfill missing hierarchy fields into generated sprint issue artifacts.

This utility updates sprint issue markdown files that were generated without the
required hierarchy metadata so independent review can validate the full issue
artifact shape.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
ISSUE_GLOB = "issue_2026_102_*.md"


PARENT_CAPABILITY_BY_FAMILY: Dict[str, str] = {
    "C02": "C02-A01-001",
    "C03": "C03-A02-001",
    "C04": "C04-A03-001",
    "C05": "C05-A04-001",
    "C06": "C06-A05-001",
    "C07": "C07-A06-001",
    "C08": "C08-A07-001",
    "C09": "C09-A08-001",
    "C11": "C11-LLM-001",
    "C12": "C12-HITL-001",
    "GUI": "C13-UI-001",
    "RHMI": "C13-UI-001",
    "HITL": "C12-HITL-001",
    "PRJ": "C16-PRJ-001",
    "VS": "C14-VER-001",
    "PRM": "C17-PRM-001",
    "RIC": "C01-STATE-001",
}


PARENT_FUNCTION_BY_FAMILY: Dict[str, str] = {
    "C02": "F-C02-A01-INPUT-NORMALIZER-L1",
    "C03": "F-C03-A02-CONTEXT-BUILDER-L1",
    "C04": "F-C04-A03-TRUST-BOUNDARY-L1",
    "C05": "F-C05-A04-STRIDE-L1",
    "C06": "F-C06-A05-THREAT-GENERATOR-L1",
    "C07": "F-C07-A06-STIX-L1",
    "C08": "F-C08-A07-MITIGATION-L1",
    "C09": "F-C09-A08-DIAGRAM-L1",
    "C11": "F-LLM-TRACEABILITY-L1",
    "C12": "F-HITL-GATE-CONTROL",
    "GUI": "F-UI-TRACEABILITY-L1",
    "RHMI": "F-UI-TRACEABILITY-L1",
    "HITL": "F-HITL-GATE-CONTROL",
    "PRJ": "F-PRJ-TRACEABILITY-L1",
    "VS": "F-VER-TRACEABILITY-L1",
    "PRM": "F-PRM-TRACEABILITY-L1",
    "RIC": "F-RIC-TRACEABILITY-L1",
}


ALLOCATED_MODULE_BY_FAMILY: Dict[str, str] = {
    "C02": "src/threat_modeler/agents/agent_01_input_normalizer.py",
    "C03": "src/threat_modeler/agents/agent_02_context_builder.py",
    "C04": "src/threat_modeler/agents/agent_03_trust_boundary_validator.py",
    "C05": "src/threat_modeler/agents/agent_04_stride_scorer.py",
    "C06": "src/threat_modeler/agents/agent_05_threat_generator.py",
    "C07": "src/threat_modeler/agents/agent_06_stix_packager.py",
    "C08": "src/threat_modeler/agents/agent_07_mitigation_generator.py",
    "C09": "src/threat_modeler/agents/agent_08_diagram_generator.py",
    "C11": "src/threat_modeler/llm/openai_compatible_adapter.py",
    "C12": "src/threat_modeler/hitl/service.py",
    "GUI": "frontend/src/App.tsx",
    "RHMI": "frontend/src/App.tsx",
    "HITL": "src/threat_modeler/hitl/service.py",
    "PRJ": "src/threat_modeler/orchestrator.py",
    "VS": "scripts/verify_sprint_traceability.py",
    "PRM": "src/threat_modeler/backend/prompt_store.py",
    "RIC": "src/threat_modeler/backend/run_manager.py",
}


VERIFICATION_METHOD_BY_FAMILY: Dict[str, str] = {
    "C02": "Automated integration and governance verification",
    "C03": "Automated integration and governance verification",
    "C04": "Automated integration and governance verification",
    "C05": "Automated integration and governance verification",
    "C06": "Automated integration and governance verification",
    "C07": "Automated integration and governance verification",
    "C08": "Automated integration and governance verification",
    "C09": "Automated integration and governance verification",
    "C11": "Live adapter validation and governance verification",
    "C12": "Workflow state verification",
    "GUI": "UI functional and API integration verification",
    "RHMI": "UI functional and API integration verification",
    "HITL": "Workflow state verification",
    "PRJ": "End-to-end governance verification",
    "VS": "Artifact-based verification evidence",
    "PRM": "Prompt governance inspection and unit verification",
    "RIC": "Runtime contract verification",
}


DATA_FLOW_BY_FAMILY: Dict[str, str] = {
    "C02": "DF-C02-A01-TRACE",
    "C03": "DF-C03-A02-TRACE",
    "C04": "DF-C04-A03-TRACE",
    "C05": "DF-C05-A04-TRACE",
    "C06": "DF-C06-A05-TRACE",
    "C07": "DF-C07-A06-TRACE",
    "C08": "DF-C08-A07-TRACE",
    "C09": "DF-C09-A08-TRACE",
    "C11": "DF-LLM-TRACE",
    "C12": "DF-HITL-TRACE",
    "GUI": "DF-UI-TRACE",
    "RHMI": "DF-UI-TRACE",
    "HITL": "DF-HITL-TRACE",
    "PRJ": "DF-PRJ-TRACE",
    "VS": "DF-VER-TRACE",
    "PRM": "DF-PRM-TRACE",
    "RIC": "DF-RIC-TRACE",
}


def family_for_requirement(req_id: str) -> str:
    return req_id.split("-", 1)[0] if req_id else ""


def requirement_identifier(path: Path, text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Requirement ID:"):
            return stripped.split(":", 1)[1].strip()

    stem = path.stem
    parts = stem.split("_")
    for idx, part in enumerate(parts):
        if part in {"BL", "RHMI", "RIC", "PRJ", "PRM", "VS", "GUI", "HITL"}:
            candidate = "-".join(parts[idx:idx + 2])
            if candidate:
                return candidate
    for token in parts:
        if token.startswith("C") or token.startswith("HITL") or token.startswith("PRJ") or token.startswith("RHMI") or token.startswith("RIC") or token.startswith("PRM") or token.startswith("VS") or token.startswith("GUI"):
            if token.startswith("C") and len(token) >= 4:
                return token.replace("_", "-")
    return ""


def insert_hierarchy_block(text: str, req_id: str, family: str) -> Tuple[str, bool]:
    if "Parent Capability ID:" in text:
        return text, False

    parent_capability = PARENT_CAPABILITY_BY_FAMILY.get(family, f"{family}-001")
    parent_function = PARENT_FUNCTION_BY_FAMILY.get(family, f"F-{family}-TRACEABILITY-L1")
    child_function = f"F-{req_id.replace('-', '_')}-TRACE-L2"
    allocated_module = ALLOCATED_MODULE_BY_FAMILY.get(family, "planning/issues/Sprint_2026_102_Issue_Tracker.md")
    verification_method = VERIFICATION_METHOD_BY_FAMILY.get(family, "Governance traceability verification")
    data_flow_id = DATA_FLOW_BY_FAMILY.get(family, f"DF-{req_id.replace('-', '_')}")

    lines = text.splitlines()
    result: List[str] = []
    inserted = False
    for line in lines:
        result.append(line)
        if line.startswith("Requirement Source:") and not inserted:
            result.extend(
                [
                    f"Requirement ID: {req_id}",
                    f"Parent Capability ID: {parent_capability}",
                    f"Parent Function ID: {parent_function}",
                    f"Child Function ID: {child_function}",
                    "Decomposition Level: L2",
                    f"Allocated Component/Module: {allocated_module}",
                    f"Verification Method: {verification_method}",
                    f"Data-Flow ID: {data_flow_id}",
                ]
            )
            inserted = True
    if not inserted:
        return text, False
    return "\n".join(result) + ("\n" if text.endswith("\n") else ""), True


def target_files() -> Iterable[Path]:
    yield from sorted((REPO_ROOT / "planning" / "issues").glob(ISSUE_GLOB))


def main() -> int:
    updated = 0
    skipped = 0
    for path in target_files():
        text = path.read_text(encoding="utf-8")
        req_id = requirement_identifier(path, text)
        if not req_id:
            skipped += 1
            continue

        family = family_for_requirement(req_id)
        rewritten, changed = insert_hierarchy_block(text, req_id, family)
        if changed:
            path.write_text(rewritten, encoding="utf-8")
            updated += 1
        else:
            skipped += 1

    print("Hierarchy field backfill complete:")
    print(f"- Updated files: {updated}")
    print(f"- Skipped files: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

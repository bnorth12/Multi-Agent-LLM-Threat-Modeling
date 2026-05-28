"""Agent 09 — Human Report Writer."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .base import BaseAgent
from ..state import FrameworkState

_REQUIRED_SECTIONS = [
    "Executive Summary",
    "System Scope and Description",
    "Trust Boundaries",
    "Data Flow Diagrams",
    "STRIDE Findings",
    "Top Threats",
    "Mitigation Mapping and Residual Risk",
    "Appendix",
]

_SECTION_ALIASES: dict[str, list[str]] = {
    "System Scope and Description": ["System Scope"],
    "Mitigation Mapping and Residual Risk": ["Mitigation Mapping"],
}


def _extract_section(markdown: str, heading: str, aliases: list[str] | None = None) -> str:
    headings = [heading] + (aliases or [])
    lines = markdown.splitlines()

    start_index = -1
    for idx, line in enumerate(lines):
        normalized = line.strip().lower()
        for candidate in headings:
            if normalized == f"## {candidate}".lower():
                start_index = idx + 1
                break
        if start_index >= 0:
            break

    if start_index < 0:
        return ""

    end_index = len(lines)
    for idx in range(start_index, len(lines)):
        if re.match(r"^##\s+", lines[idx].strip()):
            end_index = idx
            break

    return "\n".join(lines[start_index:end_index]).strip()


def _default_section_content(state: FrameworkState, heading: str) -> str:
    graph = state.canonical_graph_dict()
    system = graph.get("system", {}) if isinstance(graph.get("system"), dict) else {}
    interfaces = graph.get("interfaces", []) if isinstance(graph.get("interfaces"), list) else []
    threats = graph.get("threats", []) if isinstance(graph.get("threats"), list) else []
    trust_boundaries = graph.get("trust_boundaries", []) if isinstance(graph.get("trust_boundaries"), list) else []

    if heading == "Executive Summary":
        return (
            "This report summarizes the modeled system threat posture using canonical artifacts. "
            f"The current model contains {len(interfaces)} interfaces, {len(threats)} threats, "
            f"and {len(trust_boundaries)} trust boundaries."
        )

    if heading == "System Scope and Description":
        return "\n".join(
            [
                f"- System Name: {system.get('name', 'Unknown')}",
                f"- Description: {system.get('description', 'Not provided')}",
                f"- Mission Criticality: {system.get('mission_criticality', 'Not provided')}",
                f"- Safety Criticality: {system.get('safety_criticality', 'Not provided')}",
            ]
        )

    if heading == "Trust Boundaries":
        if not trust_boundaries:
            return "No trust boundaries were provided in canonical evidence."
        lines = []
        for boundary in trust_boundaries[:12]:
            if isinstance(boundary, dict):
                lines.append(f"- {boundary.get('name', boundary.get('id', 'Unnamed boundary'))}")
        return "\n".join(lines) if lines else "No trust boundaries were provided in canonical evidence."

    if heading == "Data Flow Diagrams":
        if not state.mermaid_diagrams:
            return "No diagrams were produced in this run."
        lines = [f"Generated diagrams: {len(state.mermaid_diagrams)}"]
        for level, code in list(state.mermaid_diagrams.items())[:3]:
            lines.extend(["", f"### {level}", "```mermaid", code.strip(), "```"])
        return "\n".join(lines).strip()

    if heading == "STRIDE Findings":
        table = [
            "| Interface | S | T | R | I | D | E |",
            "|---|---|---|---|---|---|---|",
        ]
        for interface in interfaces[:20]:
            if not isinstance(interface, dict):
                continue
            stride = interface.get("stride", {}) if isinstance(interface.get("stride"), dict) else {}
            table.append(
                "| "
                + f"{interface.get('name', interface.get('id', 'unnamed'))} | "
                + f"{stride.get('S', 0)} | {stride.get('T', 0)} | {stride.get('R', 0)} | "
                + f"{stride.get('I', 0)} | {stride.get('D', 0)} | {stride.get('E', 0)} |"
            )
        return "\n".join(table)

    if heading == "Top Threats":
        if not threats:
            return "No threats were generated in canonical evidence."
        lines = []
        for threat in threats[:10]:
            if isinstance(threat, dict):
                name = threat.get("name", threat.get("id", "Unnamed threat"))
                summary = threat.get("description", "No description provided")
                lines.append(f"- {name}: {summary}")
        return "\n".join(lines) if lines else "No threats were generated in canonical evidence."

    if heading == "Mitigation Mapping and Residual Risk":
        return "\n".join(
            [
                "| Threat | Mitigations | Residual Risk |",
                "|---|---|---|",
                "| Populate from approved threat and mitigation artifacts | Pending | Pending |",
            ]
        )

    if heading == "Appendix":
        return "\n".join(
            [
                f"- Messages captured: {len(state.messages)}",
                f"- Mermaid diagram levels: {len(state.mermaid_diagrams)}",
                f"- STIX bundle present: {'yes' if state.stix_bundle else 'no'}",
            ]
        )

    return ""


def _normalize_report_markdown(state: FrameworkState, llm_response: str) -> str:
    source = (llm_response or "").strip()
    graph = state.canonical_graph_dict()
    system = graph.get("system", {}) if isinstance(graph.get("system"), dict) else {}
    system_name = str(system.get("name", "System")).strip() or "System"

    title = f"# Threat Model Report - {system_name}"
    sections: list[str] = [title, ""]

    for heading in _REQUIRED_SECTIONS:
        content = _extract_section(source, heading, _SECTION_ALIASES.get(heading, []))
        if not content:
            content = _default_section_content(state, heading)
        sections.append(f"## {heading}")
        sections.append(content.strip() if content.strip() else "No content provided.")
        sections.append("")

    return "\n".join(sections).strip() + "\n"


@dataclass
class ReportWriterAgent(BaseAgent):
    display_name: str = "Report Writer"
    stage_id: str = "agent_09"
    _prompt_filename: str = "agent_09_human_report_writer.txt"
    _fixture_filename: str = "agent_09_output.md"

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        missing = [
            s
            for s in _REQUIRED_SECTIONS
            if s.lower() not in llm_response.lower()
            and not any(alias.lower() in llm_response.lower() for alias in _SECTION_ALIASES.get(s, []))
        ]
        if missing:
            state.record_message(
                self.stage_id,
                f"Report Writer: missing required sections: {missing}",
            )
        state.final_report = _normalize_report_markdown(state, llm_response)
        return state

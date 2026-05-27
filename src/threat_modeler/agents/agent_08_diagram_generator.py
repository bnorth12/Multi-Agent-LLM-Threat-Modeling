"""Agent 08 — Diagram Generator."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from .base import BaseAgent
from ..exports import export_mermaid
from ..state import FrameworkState

_SECTION_PATTERN = re.compile(
    r"MERMAID_LEVEL(\d+)\s*:?\s*```mermaid(.*?)```", re.DOTALL
)
_MERMAID_BLOCK_PATTERN = re.compile(r"```mermaid\s*(.*?)```", re.DOTALL)


def _safe_node_id(raw: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_]", "_", raw or "node")
    token = re.sub(r"_+", "_", token).strip("_")
    if not token:
        token = "node"
    if token[0].isdigit():
        token = f"n_{token}"
    return token


def _escaped_label(raw: str) -> str:
    return str(raw or "").replace('"', "'")


def _level_indices(diagrams: dict[str, str]) -> list[int]:
    out: list[int] = []
    for key in diagrams.keys():
        match = re.fullmatch(r"level_(\d+)", key)
        if match:
            out.append(int(match.group(1)))
    return out


@dataclass
class DiagramGeneratorAgent(BaseAgent):
    display_name: str = "Diagram Generator"
    stage_id: str = "agent_08"
    _prompt_filename: str = "agent_08_diagram_generator.txt"
    _fixture_filename: str = "agent_08_output.txt"

    @staticmethod
    def _target_diagram_count(state: FrameworkState) -> int:
        if state.canonical_graph is None:
            return 1
        graph = state.canonical_graph
        interface_count = len(graph.interfaces)
        component_count = len(graph.components)
        subsystem_count = len(graph.subsystems)
        # Scale decomposition budget with graph density; cap at 12 levels for now.
        return max(
            2,
            min(
                12,
                max(
                    math.ceil(interface_count / 6),
                    math.ceil(component_count / 8),
                    math.ceil(subsystem_count / 4),
                ),
            ),
        )

    def _build_interface_slice_diagram(
        self,
        interfaces: list,
        level_index: int,
        start_ordinal: int,
        end_ordinal: int,
        total_interfaces: int,
    ) -> str:
        lines: list[str] = [
            "flowchart TD",
            f"  subgraph LEGEND[\"Auto Diagram Level {level_index}\"]",
            f"    L1[\"Interfaces {start_ordinal}-{end_ordinal} of {total_interfaces}\"]",
            "  end",
        ]

        node_id_by_name: dict[str, str] = {}

        def ensure_node(raw_name: str) -> str:
            key = str(raw_name or "unknown")
            if key in node_id_by_name:
                return node_id_by_name[key]
            candidate = _safe_node_id(key)
            suffix = 2
            original = candidate
            while candidate in node_id_by_name.values():
                candidate = f"{original}_{suffix}"
                suffix += 1
            node_id_by_name[key] = candidate
            lines.append(f"  {candidate}[\"{_escaped_label(key)}\"]")
            return candidate

        for interface in interfaces:
            from_id = ensure_node(getattr(interface, "from_node", "unknown_from"))
            to_id = ensure_node(getattr(interface, "to_node", "unknown_to"))
            stride = getattr(interface, "stride", None)
            stride_label = ""
            if stride is not None:
                stride_label = (
                    f" S:{getattr(stride, 'S', 0)}"
                    f" T:{getattr(stride, 'T', 0)}"
                    f" R:{getattr(stride, 'R', 0)}"
                    f" I:{getattr(stride, 'I', 0)}"
                    f" D:{getattr(stride, 'D', 0)}"
                    f" E:{getattr(stride, 'E', 0)}"
                )
            label = _escaped_label(
                f"{getattr(interface, 'name', '')} [{getattr(interface, 'protocol', 'unknown')}]".strip()
                + stride_label
            )
            lines.append(f"  {from_id} -->|\"{label}\"| {to_id}")

        return "\n".join(lines).strip()

    def _augment_diagrams(self, state: FrameworkState, diagrams: dict[str, str]) -> dict[str, str]:
        if state.canonical_graph is None:
            return diagrams
        target = self._target_diagram_count(state)
        if len(diagrams) >= target:
            return diagrams

        graph = state.canonical_graph
        interfaces = list(graph.interfaces)
        if not interfaces:
            return diagrams

        chunk_size = max(6, math.ceil(len(interfaces) / max(1, target - 1)))
        existing_levels = _level_indices(diagrams)
        next_level = max(existing_levels) + 1 if existing_levels else 0

        for start in range(0, len(interfaces), chunk_size):
            if len(diagrams) >= target:
                break
            end = min(start + chunk_size, len(interfaces))
            key = f"level_{next_level}"
            if key in diagrams:
                next_level += 1
                continue
            diagrams[key] = self._build_interface_slice_diagram(
                interfaces=interfaces[start:end],
                level_index=next_level,
                start_ordinal=start + 1,
                end_ordinal=end,
                total_interfaces=len(interfaces),
            )
            next_level += 1

        if len(diagrams) < target:
            state.record_message(
                self.stage_id,
                (
                    f"Diagram Generator: generated {len(diagrams)} diagram levels; "
                    f"target was {target} based on graph complexity."
                ),
            )
        return diagrams

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        diagrams: dict[str, str] = {}
        for match in _SECTION_PATTERN.finditer(llm_response):
            level = f"level_{match.group(1)}"
            diagrams[level] = match.group(2).strip()

        if not diagrams:
            blocks = [match.group(1).strip() for match in _MERMAID_BLOCK_PATTERN.finditer(llm_response)]
            if blocks:
                for index, block in enumerate(blocks, start=0):
                    diagrams[f"level_{index}"] = block

        if not diagrams and state.canonical_graph is not None:
            diagrams = {"level_0": export_mermaid(state.canonical_graph).strip()}
            state.record_message(self.stage_id, "Diagram Generator: used canonical graph fallback export.")

        if diagrams:
            diagrams = self._augment_diagrams(state, diagrams)

        if diagrams:
            state.mermaid_diagrams = diagrams
        else:
            state.record_message(self.stage_id, "Diagram Generator: no mermaid diagram content found in response.")
        return state

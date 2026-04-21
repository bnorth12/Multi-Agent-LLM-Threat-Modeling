"""Parsing interfaces for architecture text and table inputs."""

from dataclasses import dataclass, field
import re
from typing import Any

from ..models.canonical import (
    CanonicalThreatModelGraph,
    Component,
    DataFlow,
    GraphMetadata,
    Subsystem,
    SystemContext,
)


@dataclass
class ParserInput:
    raw_text: str = ""
    tables: list[dict[str, Any]] = field(default_factory=list)


class ParserInterface:
    def normalize(self, payload: ParserInput) -> CanonicalThreatModelGraph:
        text_lines = [line.strip() for line in payload.raw_text.splitlines() if line.strip()]
        system_name = text_lines[0] if text_lines else "Parsed System"
        system_description = " ".join(text_lines[1:3]) if len(text_lines) > 1 else "Parsed from raw architecture input."

        default_subsystem = Subsystem(
            id="subsystem_core",
            name="Core Subsystem",
            description="Default subsystem created by parser normalization.",
            parent_system=system_name,
        )

        components = self._components_from_tables(payload.tables)
        if not components:
            components = [
                Component(
                    id="component_primary",
                    name="Primary Component",
                    parent_subsystem=default_subsystem.id,
                    hardware="unknown",
                    software_modules=[],
                    description="Default component created by parser normalization.",
                )
            ]

        data_flows = self._flows_from_text(text_lines)
        data_flows.extend(self._flows_from_tables(payload.tables))
        if not data_flows:
            data_flows = [
                DataFlow(
                    id="df_input_to_primary",
                    from_node="user.input",
                    to_node=components[0].id,
                    protocol="internal",
                    data_items=["raw_text", "tables"],
                )
            ]

        return CanonicalThreatModelGraph(
            metadata=GraphMetadata(status="parsed", model_level="system"),
            system=SystemContext(
                name=system_name,
                description=system_description,
                mission_criticality="undetermined",
                safety_criticality="undetermined",
            ),
            subsystems=[default_subsystem],
            components=components,
            data_flows=data_flows,
        )

    def _components_from_tables(self, tables: list[dict[str, Any]]) -> list[Component]:
        components: list[Component] = []
        for index, row in enumerate(tables, start=1):
            name = self._first_str(row, ["component", "component_name", "name"])
            if not name:
                continue

            component_id = self._first_str(row, ["component_id", "id"]) or self._deterministic_id("component", name, index)
            parent_subsystem = self._first_str(row, ["parent_subsystem", "subsystem_id"]) or "subsystem_core"
            hardware = self._first_str(row, ["hardware", "platform"]) or "unknown"
            description = self._first_str(row, ["description", "notes"]) or "Parsed from table input."
            software_modules = self._extract_software_modules(row)

            components.append(
                Component(
                    id=component_id,
                    name=name,
                    parent_subsystem=parent_subsystem,
                    hardware=hardware,
                    software_modules=software_modules,
                    description=description,
                )
            )
        return components

    def _flows_from_text(self, text_lines: list[str]) -> list[DataFlow]:
        flows: list[DataFlow] = []
        pattern = re.compile(r"^(?P<from>[^-]+)->(?P<to>[^:]+)(?::(?P<protocol>.+))?$")
        for index, line in enumerate(text_lines, start=1):
            match = pattern.match(line.replace(" ", ""))
            if not match:
                continue

            from_node = match.group("from")
            to_node = match.group("to")
            protocol = match.group("protocol") or "unknown"
            flow_id = self._deterministic_id("df", f"{from_node}-{to_node}", index)
            flows.append(
                DataFlow(
                    id=flow_id,
                    from_node=from_node,
                    to_node=to_node,
                    protocol=protocol,
                    data_items=["parsed_text"],
                )
            )
        return flows

    def _flows_from_tables(self, tables: list[dict[str, Any]]) -> list[DataFlow]:
        flows: list[DataFlow] = []
        for index, row in enumerate(tables, start=1):
            from_node = self._first_str(row, ["from_node", "source", "from"])
            to_node = self._first_str(row, ["to_node", "target", "to"])
            if not from_node or not to_node:
                continue

            flow_id = self._first_str(row, ["flow_id", "id"]) or self._deterministic_id("df", f"{from_node}-{to_node}", index)
            protocol = self._first_str(row, ["protocol", "transport"]) or "unknown"
            data_items = self._split_list(self._first_str(row, ["data_items", "data", "payload"]))

            flows.append(
                DataFlow(
                    id=flow_id,
                    from_node=from_node,
                    to_node=to_node,
                    protocol=protocol,
                    data_items=data_items,
                )
            )
        return flows

    @staticmethod
    def _first_str(row: dict[str, Any], keys: list[str]) -> str:
        for key in keys:
            value = row.get(key)
            if isinstance(value, str):
                normalized = value.strip()
                if normalized:
                    return normalized
        return ""

    @staticmethod
    def _split_list(value: str) -> list[str]:
        if not value:
            return []
        return [part.strip() for part in value.split(",") if part.strip()]

    def _extract_software_modules(self, row: dict[str, Any]) -> list[str]:
        modules_value = row.get("software_modules") or row.get("software") or row.get("modules")
        if isinstance(modules_value, list):
            return [str(module).strip() for module in modules_value if str(module).strip()]
        if isinstance(modules_value, str):
            return self._split_list(modules_value)
        return []

    def _deterministic_id(self, prefix: str, source: str, index: int) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", source.lower()).strip("_")
        if not slug:
            slug = "item"
        return f"{prefix}_{slug}_{index}"

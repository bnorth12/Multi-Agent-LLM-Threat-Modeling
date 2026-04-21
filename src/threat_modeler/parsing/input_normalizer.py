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
        normalized_rows = self._normalized_rows(payload.tables)

        subsystems = self._subsystems_from_tables(normalized_rows, system_name)
        if not subsystems:
            subsystems = [
                Subsystem(
                    id="subsystem_core",
                    name="Core Subsystem",
                    description="Default subsystem created by parser normalization.",
                    parent_system=system_name,
                )
            ]

        components = self._components_from_tables(normalized_rows, default_subsystem_id=subsystems[0].id)
        if not components:
            components = [
                Component(
                    id="component_primary",
                    name="Primary Component",
                    parent_subsystem=subsystems[0].id,
                    hardware="unknown",
                    software_modules=[],
                    description="Default component created by parser normalization.",
                )
            ]

        data_flows = self._flows_from_text(text_lines)
        data_flows.extend(self._flows_from_tables(normalized_rows))
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
            metadata=GraphMetadata(model_level="system"),
            system=SystemContext(
                name=system_name,
                description=system_description,
                mission_criticality="undetermined",
                safety_criticality="undetermined",
            ),
            subsystems=subsystems,
            components=components,
            data_flows=data_flows,
        )

    def _subsystems_from_tables(self, tables: list[dict[str, Any]], system_name: str) -> list[Subsystem]:
        subsystems: list[Subsystem] = []
        seen_ids: set[str] = set()

        for index, row in enumerate(tables, start=1):
            row_schema = self._row_schema(row)
            if row_schema and row_schema not in {"subsystem", "subsystems"}:
                continue

            subsystem_name = self._first_str(row, ["subsystem", "subsystem_name", "name"])
            if not subsystem_name:
                continue

            subsystem_id = self._first_str(row, ["subsystem_id", "id"]) or self._deterministic_id("subsystem", subsystem_name, index)
            if subsystem_id in seen_ids:
                continue

            seen_ids.add(subsystem_id)
            subsystems.append(
                Subsystem(
                    id=subsystem_id,
                    name=subsystem_name,
                    description=self._first_str(row, ["description", "notes"]) or "Parsed from table input.",
                    parent_system=self._first_str(row, ["parent_system", "system"]) or system_name,
                )
            )

        return subsystems

    def _components_from_tables(self, tables: list[dict[str, Any]], *, default_subsystem_id: str) -> list[Component]:
        components: list[Component] = []
        seen_ids: set[str] = set()
        for index, row in enumerate(tables, start=1):
            row_schema = self._row_schema(row)
            if row_schema and row_schema not in {"component", "components"}:
                continue

            name = self._first_str(row, ["component", "component_name", "name"])
            if not name:
                continue

            component_id = self._first_str(row, ["component_id", "id"]) or self._deterministic_id("component", name, index)
            if component_id in seen_ids:
                continue

            seen_ids.add(component_id)
            parent_subsystem = self._first_str(row, ["parent_subsystem", "subsystem_id"]) or default_subsystem_id
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
        pattern = re.compile(r"^(?P<from>[^-]+)->(?P<to>[^:\[]+)(?::(?P<protocol>[^\[]+))?(?:\[(?P<data_items>[^\]]+)\])?$")
        for index, line in enumerate(text_lines, start=1):
            lower_line = line.lower()
            if lower_line.startswith("flow:"):
                fields = self._parse_structured_fields(line.split(":", maxsplit=1)[1])
                from_node = fields.get("from") or fields.get("source")
                to_node = fields.get("to") or fields.get("target")
                if from_node and to_node:
                    flow_id = fields.get("id") or self._deterministic_id("df", f"{from_node}-{to_node}", index)
                    trust_boundary_name = fields.get("trust_boundary") or fields.get("boundary") or ""
                    flows.append(
                        DataFlow(
                            id=flow_id,
                            from_node=from_node,
                            to_node=to_node,
                            protocol=fields.get("protocol", "unknown"),
                            data_items=self._split_list(fields.get("data_items") or fields.get("data") or ""),
                            trust_boundary_crossing=bool(trust_boundary_name),
                            trust_boundary_name=trust_boundary_name,
                        )
                    )
                continue

            compact = line.replace(" ", "")
            match = pattern.match(compact)
            if match:
                from_node = match.group("from")
                to_node = match.group("to")
                protocol = match.group("protocol") or "unknown"
                flow_id = self._deterministic_id("df", f"{from_node}-{to_node}", index)
                items = self._split_list(match.group("data_items") or "") or ["parsed_text"]
                flows.append(
                    DataFlow(
                        id=flow_id,
                        from_node=from_node,
                        to_node=to_node,
                        protocol=protocol,
                        data_items=items,
                    )
                )
        return flows

    def _flows_from_tables(self, tables: list[dict[str, Any]]) -> list[DataFlow]:
        flows: list[DataFlow] = []
        seen_ids: set[str] = set()
        for index, row in enumerate(tables, start=1):
            row_schema = self._row_schema(row)
            if row_schema and row_schema not in {"flow", "flows", "data_flow", "data_flows"}:
                continue

            from_node = self._first_str(row, ["from_node", "source", "from"])
            to_node = self._first_str(row, ["to_node", "target", "to"])
            if not from_node or not to_node:
                continue

            flow_id = self._first_str(row, ["flow_id", "id"]) or self._deterministic_id("df", f"{from_node}-{to_node}", index)
            if flow_id in seen_ids:
                continue

            seen_ids.add(flow_id)
            protocol = self._first_str(row, ["protocol", "transport"]) or "unknown"
            data_items = self._extract_data_items(row)
            trust_boundary_name = self._first_str(row, ["trust_boundary_name", "trust_boundary", "boundary"])

            flows.append(
                DataFlow(
                    id=flow_id,
                    from_node=from_node,
                    to_node=to_node,
                    protocol=protocol,
                    data_items=data_items,
                    trust_boundary_crossing=bool(trust_boundary_name),
                    trust_boundary_name=trust_boundary_name,
                )
            )
        return flows

    def _normalized_rows(self, tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for table in tables:
            nested_rows = table.get("rows")
            if isinstance(nested_rows, list):
                schema_name = self._first_str(table, ["schema", "kind", "type", "table"])
                for nested_row in nested_rows:
                    if not isinstance(nested_row, dict):
                        continue
                    enriched_row = dict(nested_row)
                    if schema_name and "__schema" not in enriched_row:
                        enriched_row["__schema"] = schema_name
                    rows.append(enriched_row)
                continue

            rows.append(table)
        return rows

    def _row_schema(self, row: dict[str, Any]) -> str:
        return self._first_str(row, ["__schema", "schema", "kind", "type"]).lower()

    def _extract_data_items(self, row: dict[str, Any]) -> list[str]:
        direct_list = row.get("data_items") or row.get("data") or row.get("payload")
        if isinstance(direct_list, list):
            return [str(item).strip() for item in direct_list if str(item).strip()]
        return self._split_list(self._first_str(row, ["data_items", "data", "payload"]))

    def _parse_structured_fields(self, text: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for part in text.split(";"):
            if "=" not in part:
                continue
            key, value = part.split("=", maxsplit=1)
            normalized_key = key.strip().lower()
            normalized_value = value.strip()
            if normalized_key and normalized_value:
                fields[normalized_key] = normalized_value
        return fields

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

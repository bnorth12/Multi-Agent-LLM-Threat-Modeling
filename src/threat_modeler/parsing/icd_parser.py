"""ICD spreadsheet ingestion: parses CSV (and optionally xlsx) ICD files.

CSV format uses a flat entity-per-row layout with columns:
  entity_type, id, name, description, parent, hardware,
  software_modules, from_node, to_node, interface_type, protocol,
  data_items, trust_boundary_crossing, trust_boundary_name

entity_type values: subsystem | component | function | interface
"""

import csv
import os
import re
from dataclasses import dataclass, field
from typing import Any

from threat_modeler.models.canonical import Component, Function, Interface, Subsystem


@dataclass
class IcdParseResult:
    """Normalised entities extracted from one ICD source file."""

    source_file: str
    version: str
    subsystems: list[Subsystem] = field(default_factory=list)
    components: list[Component] = field(default_factory=list)
    functions: list[Function] = field(default_factory=list)
    interfaces: list[Interface] = field(default_factory=list)

    # Backward compatibility
    @property
    def data_flows(self) -> list[Interface]:
        return self.interfaces


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VERSION_RE = re.compile(r"_v(\d+(?:\.\d+)?)(?:\.\w+)?$", re.IGNORECASE)


def _extract_version(path: str) -> str:
    """Derive a version string from the filename, e.g. icd_alpha_v1.csv -> '1'."""
    stem = os.path.splitext(os.path.basename(path))[0]
    m = _VERSION_RE.search(stem)
    return m.group(1) if m else "unknown"


def _to_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes")


def _parse_rows(rows: list[dict[str, Any]], source_file: str, version: str) -> IcdParseResult:
    result = IcdParseResult(source_file=source_file, version=version)
    for row in rows:
        etype = row.get("entity_type", "").strip().lower()
        if etype == "subsystem":
            result.subsystems.append(
                Subsystem(
                    id=row.get("id", "").strip(),
                    name=row.get("name", "").strip(),
                    description=row.get("description", "").strip(),
                    parent_system=row.get("parent", "").strip(),
                )
            )
        elif etype == "component":
            software_raw = row.get("software_modules", "").strip()
            result.components.append(
                Component(
                    id=row.get("id", "").strip(),
                    name=row.get("name", "").strip(),
                    parent_subsystem=row.get("parent", "").strip(),
                    hardware=row.get("hardware", "").strip(),
                    software_modules=[m.strip() for m in software_raw.split("|") if m.strip()],
                    description=row.get("description", "").strip(),
                )
            )
        elif etype == "function":
            result.functions.append(
                Function(
                    id=row.get("id", "").strip(),
                    name=row.get("name", "").strip(),
                    parent_component=row.get("parent", "").strip(),
                    description=row.get("description", "").strip(),
                )
            )
        elif etype == "interface":
            items_raw = row.get("data_items", "").strip()
            result.interfaces.append(
                Interface(
                    id=row.get("id", "").strip(),
                    name=row.get("name", "").strip(),
                    description=row.get("description", "").strip(),
                    from_node=row.get("from_node", "").strip(),
                    to_node=row.get("to_node", "").strip(),
                    interface_type=row.get("interface_type", "unknown").strip(),
                    protocol=row.get("protocol", "unknown").strip(),
                    data_items=[i.strip() for i in items_raw.split("|") if i.strip()],
                    trust_boundary_crossing=_to_bool(row.get("trust_boundary_crossing", "false")),
                    trust_boundary_name=row.get("trust_boundary_name", "").strip(),
                )
            )
        elif etype == "data_flow":
            # Backward compatibility: treat data_flow as interface
            items_raw = row.get("data_items", "").strip()
            result.interfaces.append(
                Interface(
                    id=row.get("id", "").strip(),
                    name=row.get("name", "").strip(),
                    description="Legacy data flow",
                    from_node=row.get("from_node", "").strip(),
                    to_node=row.get("to_node", "").strip(),
                    interface_type="unknown",
                    protocol=row.get("protocol", "unknown").strip(),
                    data_items=[i.strip() for i in items_raw.split("|") if i.strip()],
                    trust_boundary_crossing=_to_bool(row.get("trust_boundary_crossing", "false")),
                    trust_boundary_name=row.get("trust_boundary_name", "").strip(),
                )
            )
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_csv(path: str) -> IcdParseResult:
    """Parse a CSV-format ICD file and return an IcdParseResult."""
    version = _extract_version(path)
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return _parse_rows(rows, source_file=path, version=version)


def parse_xlsx(path: str) -> IcdParseResult:
    """Parse an xlsx-format ICD file.  Requires openpyxl."""
    try:
        import openpyxl  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "openpyxl is required to parse xlsx files.  "
            "Install it with: pip install openpyxl"
        ) from exc

    version = _extract_version(path)
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    headers: list[str] = []
    rows: list[dict[str, Any]] = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            headers = [str(c).strip() if c is not None else "" for c in row]
        else:
            rows.append({headers[j]: (str(v).strip() if v is not None else "") for j, v in enumerate(row)})
    wb.close()
    return _parse_rows(rows, source_file=path, version=version)


def parse(path: str) -> IcdParseResult:
    """Dispatch to the appropriate parser based on file extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return parse_csv(path)
    if ext in (".xlsx", ".xlsm"):
        return parse_xlsx(path)
    raise ValueError(f"Unsupported ICD file extension: {ext!r}. Supported: .csv, .xlsx")

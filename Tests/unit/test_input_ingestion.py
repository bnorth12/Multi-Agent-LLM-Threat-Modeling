"""Unit tests for S05-02: ICD and narrative document ingestion."""

import os
import pathlib

import pytest

from threat_modeler.parsing.icd_parser import parse_csv, IcdParseResult
from threat_modeler.parsing.narrative_parser import parse_markdown, NarrativeParseResult

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "inputs"
ICD_DIR = FIXTURES / "icd"
DESC_DIR = FIXTURES / "descriptions"


# ---------------------------------------------------------------------------
# ICD CSV fixtures
# ---------------------------------------------------------------------------

class TestIcdCsvAlpha:
    """icd_alpha_v1.csv — Alpha UAV System."""

    def setup_method(self):
        self.result: IcdParseResult = parse_csv(str(ICD_DIR / "icd_alpha_v1.csv"))

    def test_returns_icd_parse_result(self):
        assert isinstance(self.result, IcdParseResult)

    def test_provenance_source_file(self):
        assert self.result.source_file.endswith("icd_alpha_v1.csv")

    def test_provenance_version(self):
        assert self.result.version == "1"

    def test_subsystems_count(self):
        assert len(self.result.subsystems) == 2

    def test_subsystem_ids(self):
        ids = {s.id for s in self.result.subsystems}
        assert "SS-NAV-01" in ids
        assert "SS-CMD-01" in ids

    def test_subsystem_parent_system_populated(self):
        for s in self.result.subsystems:
            assert s.parent_system != ""

    def test_components_count(self):
        assert len(self.result.components) == 3

    def test_component_parent_subsystem_populated(self):
        for c in self.result.components:
            assert c.parent_subsystem != ""

    def test_data_flows_count(self):
        assert len(self.result.data_flows) == 3

    def test_trust_boundary_crossing_detected(self):
        crossing_flows = [df for df in self.result.data_flows if df.trust_boundary_crossing]
        assert len(crossing_flows) == 1
        assert crossing_flows[0].id == "DF-003"

    def test_trust_boundary_name_populated(self):
        df = next(df for df in self.result.data_flows if df.id == "DF-003")
        assert df.trust_boundary_name == "External Radio Link"

    def test_data_items_parsed_as_list(self):
        df = next(df for df in self.result.data_flows if df.id == "DF-001")
        assert "position_fix" in df.data_items
        assert "timestamp" in df.data_items

    def test_software_modules_parsed_as_list(self):
        cmd = next(c for c in self.result.components if c.id == "C-CMD-01")
        assert "cmd.processor" in cmd.software_modules
        assert "cmd.validator" in cmd.software_modules


class TestIcdCsvBravo:
    """icd_bravo_v2.csv — Bravo Ground Station."""

    def setup_method(self):
        self.result: IcdParseResult = parse_csv(str(ICD_DIR / "icd_bravo_v2.csv"))

    def test_provenance_version(self):
        assert self.result.version == "2"

    def test_subsystems_count(self):
        assert len(self.result.subsystems) == 2

    def test_components_count(self):
        assert len(self.result.components) == 3

    def test_data_flows_count(self):
        assert len(self.result.data_flows) == 3

    def test_trust_boundary_crossing_detected(self):
        crossing = [df for df in self.result.data_flows if df.trust_boundary_crossing]
        assert len(crossing) == 1
        assert crossing[0].id == "DF-103"


class TestIcdCsvAvionics:
    """icd_avionics_v1.csv — Avionics Data Network."""

    def setup_method(self):
        self.result: IcdParseResult = parse_csv(str(ICD_DIR / "icd_avionics_v1.csv"))

    def test_provenance_version(self):
        assert self.result.version == "1"

    def test_expected_entity_counts(self):
        assert len(self.result.subsystems) == 4
        assert len(self.result.components) == 7
        assert len(self.result.data_flows) == 8

    def test_expected_protocols_present(self):
        protocols = {df.protocol for df in self.result.data_flows}
        assert "ARINC-429" in protocols
        assert "MIL-STD-1553" in protocols
        assert "ARINC-664" in protocols
        assert "ARINC-818" in protocols
        assert "Discrete" in protocols
        assert "Analog" in protocols

    def test_trust_boundary_flows_present(self):
        boundary_ids = {df.id for df in self.result.data_flows if df.trust_boundary_crossing}
        assert "DF-203" in boundary_ids
        assert "DF-204" in boundary_ids
        assert "DF-205" in boundary_ids


# ---------------------------------------------------------------------------
# Narrative Markdown fixtures
# ---------------------------------------------------------------------------

class TestNarrativeAlpha:
    """description_alpha.md — Alpha UAV System."""

    def setup_method(self):
        self.result: NarrativeParseResult = parse_markdown(str(DESC_DIR / "description_alpha.md"))

    def test_returns_narrative_parse_result(self):
        assert isinstance(self.result, NarrativeParseResult)

    def test_provenance_source_file(self):
        assert self.result.source_file.endswith("description_alpha.md")

    def test_system_name_extracted_from_h1(self):
        assert self.result.system_name == "Alpha UAV System"

    def test_description_is_non_empty(self):
        assert len(self.result.description) > 20

    def test_raw_text_contains_trust_boundary_section(self):
        assert "Trust Boundaries" in self.result.raw_text

    def test_description_does_not_start_with_heading(self):
        assert not self.result.description.startswith("#")


class TestNarrativeBravo:
    """description_bravo.md — Bravo Ground Station."""

    def setup_method(self):
        self.result: NarrativeParseResult = parse_markdown(str(DESC_DIR / "description_bravo.md"))

    def test_system_name_extracted_from_h1(self):
        assert self.result.system_name == "Bravo Ground Station"

    def test_description_is_non_empty(self):
        assert len(self.result.description) > 20

    def test_raw_text_contains_storage_section(self):
        assert "Storage Subsystem" in self.result.raw_text


class TestNarrativeAvionics:
    """description_avionics.md — Avionics Data Network."""

    def setup_method(self):
        self.result: NarrativeParseResult = parse_markdown(str(DESC_DIR / "description_avionics.md"))

    def test_system_name_extracted_from_h1(self):
        assert self.result.system_name == "Avionics Data Network"

    def test_raw_text_contains_interface_standards(self):
        assert "ARINC-429" in self.result.raw_text
        assert "MIL-STD-1553" in self.result.raw_text
        assert "ARINC-818" in self.result.raw_text


class TestIcdCsvThreatModeler:
    """icd_threat_modeler_v1.csv — Multi-Agent Threat Modeler Tool."""

    def setup_method(self):
        self.result: IcdParseResult = parse_csv(str(ICD_DIR / "icd_threat_modeler_v1.csv"))

    def test_provenance_version(self):
        assert self.result.version == "1"

    def test_expected_subsystem_count(self):
        assert len(self.result.subsystems) == 6

    def test_subsystem_ids_present(self):
        ids = {s.id for s in self.result.subsystems}
        assert "SS-INPUT-01" in ids
        assert "SS-ORCHESTRATION-01" in ids
        assert "SS-LLM-01" in ids
        assert "SS-HITL-01" in ids
        assert "SS-EXPORT-01" in ids
        assert "SS-UI-01" in ids

    def test_expected_component_count(self):
        # Threat modeler ICD is large; validate >= expected threshold
        assert len(self.result.components) >= 15

    def test_expected_data_flow_count(self):
        assert len(self.result.data_flows) == 27

    def test_llm_api_boundary_flows_present(self):
        boundary_flows = [df for df in self.result.data_flows if "API" in df.trust_boundary_name]
        boundary_ids = {df.id for df in boundary_flows}
        assert "DF-MODEL-009" in boundary_ids
        assert "DF-MODEL-010" in boundary_ids

    def test_user_trust_boundary_flows_present(self):
        user_boundary = [df for df in self.result.data_flows if df.trust_boundary_name == "User Trust Boundary"]
        assert len(user_boundary) >= 5

    def test_protocol_variety(self):
        protocols = {df.protocol for df in self.result.data_flows}
        assert "HTTP/Multipart" in protocols
        assert "HTTPS" in protocols
        assert "gRPC" in protocols
        assert "protobuf" in protocols
        assert "in-process" in protocols

    def test_hitl_gate_components_present(self):
        ids = {c.id for c in self.result.components}
        assert "C-HITL-01" in ids
        assert "C-HITL-02" in ids


class TestNarrativeThreatModeler:
    """description_threat_modeler.md — Multi-Agent Threat Modeler Tool."""

    def setup_method(self):
        self.result: NarrativeParseResult = parse_markdown(str(DESC_DIR / "description_threat_modeler.md"))

    def test_system_name_extracted_from_h1(self):
        assert self.result.system_name == "Multi-Agent Threat Modeler Tool"

    def test_description_is_comprehensive(self):
        assert len(self.result.description) > 100

    def test_raw_text_contains_subsystems(self):
        assert "Input Management Subsystem" in self.result.raw_text
        assert "Agent Orchestration Subsystem" in self.result.raw_text
        assert "LLM Runtime Subsystem" in self.result.raw_text
        assert "Human-in-the-Loop Subsystem" in self.result.raw_text
        assert "Export Subsystem" in self.result.raw_text
        assert "User Interface Subsystem" in self.result.raw_text

    def test_raw_text_contains_hitl_gates(self):
        assert "Gate 0" in self.result.raw_text
        assert "Gate 7" in self.result.raw_text
        assert "pause" in self.result.raw_text.lower()

    def test_raw_text_contains_export_formats(self):
        assert "STIX" in self.result.raw_text
        assert "Mermaid" in self.result.raw_text
        assert "JSON" in self.result.raw_text

    def test_raw_text_contains_trust_boundaries(self):
        assert "User Trust Boundary" in self.result.raw_text
        assert "External LLM API Boundary" in self.result.raw_text


# ---------------------------------------------------------------------------
# Dispatch (parse() entry-point)
# ---------------------------------------------------------------------------

def test_parse_icd_dispatches_csv():
    from threat_modeler.parsing.icd_parser import parse
    result = parse(str(ICD_DIR / "icd_alpha_v1.csv"))
    assert isinstance(result, IcdParseResult)


def test_parse_narrative_dispatches_md():
    from threat_modeler.parsing.narrative_parser import parse
    result = parse(str(DESC_DIR / "description_alpha.md"))
    assert isinstance(result, NarrativeParseResult)


def test_parse_icd_unsupported_extension():
    from threat_modeler.parsing.icd_parser import parse
    with pytest.raises(ValueError, match="Unsupported ICD file extension"):
        parse("some_file.pdf")


def test_parse_narrative_unsupported_extension():
    from threat_modeler.parsing.narrative_parser import parse
    with pytest.raises(ValueError, match="Unsupported narrative file extension"):
        parse("some_file.pdf")

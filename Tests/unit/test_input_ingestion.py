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


class TestIcdCsvUasWeaponSystem:
    """icd_uas_weapon_system_v1.csv — UAS Weapon System."""

    def setup_method(self):
        self.result: IcdParseResult = parse_csv(str(ICD_DIR / "icd_uas_weapon_system_v1.csv"))

    def test_provenance_version(self):
        assert self.result.version == "1"

    def test_expected_subsystem_count(self):
        assert len(self.result.subsystems) == 4

    def test_subsystem_ids_present(self):
        ids = {s.id for s in self.result.subsystems}
        assert "SS-ALPHA-01" in ids
        assert "SS-BRAVO-01" in ids
        assert "SS-CHARLIE-01" in ids
        assert "SS-DELTA-01" in ids

    def test_expected_component_count(self):
        assert len(self.result.components) >= 12

    def test_expected_data_flow_count(self):
        assert len(self.result.data_flows) == 10

    def test_satellite_link_boundary_flows_present(self):
        boundary_flows = [df for df in self.result.data_flows if df.trust_boundary_name == "Satellite Link Boundary"]
        boundary_ids = {df.id for df in boundary_flows}
        assert "DF-WS-001" in boundary_ids
        assert "DF-WS-002" in boundary_ids

    def test_ground_boundary_flows_present(self):
        boundary_names = {df.trust_boundary_name for df in self.result.data_flows}
        assert "Ops Network Boundary" in boundary_names
        assert "Maintenance Bus Boundary" in boundary_names
        assert "Maintenance LAN Boundary" in boundary_names
        assert "Key Management Boundary" in boundary_names

    def test_protocol_variety(self):
        protocols = {df.protocol for df in self.result.data_flows}
        assert "Encrypted RF (AES-256-GCM)" in protocols
        assert "HTTPS TLS 1.3" in protocols
        assert "MIL-STD-1553" in protocols
        assert "RS-422" in protocols
        assert "Ethernet (LAN)" in protocols

    def test_lower_level_components_present(self):
        ids = {c.id for c in self.result.components}
        assert "C-ALPHA-01" in ids
        assert "C-BRAVO-03" in ids
        assert "C-CHARLIE-02" in ids
        assert "C-DELTA-02" in ids


class TestNarrativeUasWeaponSystem:
    """description_uas_weapon_system.md — UAS Weapon System."""

    def setup_method(self):
        self.result: NarrativeParseResult = parse_markdown(str(DESC_DIR / "description_uas_weapon_system.md"))

    def test_system_name_extracted_from_h1(self):
        assert self.result.system_name == "UAS Weapon System"

    def test_description_is_comprehensive(self):
        assert len(self.result.description) > 100

    def test_raw_text_contains_segments(self):
        assert "Segment Alpha" in self.result.raw_text
        assert "Segment Bravo" in self.result.raw_text
        assert "Segment Charlie" in self.result.raw_text
        assert "Segment Delta" in self.result.raw_text

    def test_raw_text_contains_lower_level_components(self):
        assert "Flight Control Computer" in self.result.raw_text
        assert "Mission Processing Server" in self.result.raw_text
        assert "Satcom Modem" in self.result.raw_text
        assert "Maintenance Test Set" in self.result.raw_text

    def test_raw_text_contains_trust_boundaries(self):
        assert "Satellite Link Boundary" in self.result.raw_text
        assert "Ops Network Boundary" in self.result.raw_text
        assert "Maintenance Bus Boundary" in self.result.raw_text
        assert "Maintenance LAN Boundary" in self.result.raw_text
        assert "Key Management Boundary" in self.result.raw_text


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

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
        assert len(self.result.data_flows) == 5

    def test_trust_boundary_crossing_detected(self):
        crossing_flows = [iface for iface in self.result.interfaces if iface.trust_boundary_crossing]
        assert len(crossing_flows) == 1
        assert crossing_flows[0].id == "IF-003"

    def test_trust_boundary_name_populated(self):
        iface = next(i for i in self.result.interfaces if i.id == "IF-003")
        assert iface.trust_boundary_name == "External Radio Link"

    def test_data_items_parsed_as_list(self):
        iface = next(i for i in self.result.interfaces if i.id == "IF-001")
        assert "position_fix" in iface.data_items
        assert "timestamp" in iface.data_items

    def test_software_modules_parsed_as_list(self):
        cmd = next(c for c in self.result.components if c.id == "C-CMD-01")
        assert "cmd.processor" in cmd.software_modules
        assert "cmd.validator" in cmd.software_modules

    def test_functions_count(self):
        assert len(self.result.functions) == 5

    def test_function_parent_component_populated(self):
        for func in self.result.functions:
            assert func.parent_component != ""

    def test_interface_count(self):
        assert len(self.result.interfaces) == 5

    def test_interface_type_populated(self):
        for iface in self.result.interfaces:
            assert iface.interface_type != "unknown"


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
        assert len(self.result.data_flows) == 5

    def test_functions_count(self):
        assert len(self.result.functions) == 5

    def test_interface_count(self):
        assert len(self.result.interfaces) == 5

    def test_trust_boundary_crossing_detected(self):
        crossing = [i for i in self.result.interfaces if i.trust_boundary_crossing]
        assert len(crossing) == 1
        assert crossing[0].id == "IF-103"


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

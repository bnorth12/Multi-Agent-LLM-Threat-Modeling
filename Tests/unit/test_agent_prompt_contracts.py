from __future__ import annotations

import json
import re

from threat_modeler.agents.agent_09_report_writer import _REQUIRED_SECTIONS
from threat_modeler.backend import prompt_store as backend_prompt_store
from threat_modeler.ui import prompt_store as ui_prompt_store


_CANONICAL_GRAPH_AGENTS = ("agent_01", "agent_02", "agent_03", "agent_04", "agent_05", "agent_07")
_STRIDE_KEYS = {
    "S",
    "S_justification",
    "T",
    "T_justification",
    "R",
    "R_justification",
    "I",
    "I_justification",
    "D",
    "D_justification",
    "E",
    "E_justification",
}


def _load_backend_expected_output_json(agent_id: str) -> dict:
    text = backend_prompt_store._DEFAULT_PROMPTS[agent_id]["expected_output"]
    parsed = json.loads(text)
    assert isinstance(parsed, dict)
    return parsed


def test_canonical_graph_agents_use_full_canonical_shape_examples() -> None:
    required_top_level = {"metadata", "system", "subsystems", "components", "functions", "interfaces"}

    for agent_id in _CANONICAL_GRAPH_AGENTS:
        payload = _load_backend_expected_output_json(agent_id)
        assert required_top_level.issubset(payload.keys()), f"{agent_id} expected_output is not a full canonical graph"
        assert isinstance(payload["interfaces"], list)
        assert payload["interfaces"], f"{agent_id} expected_output should include at least one interface example"

        interface = payload["interfaces"][0]
        assert isinstance(interface.get("stride"), dict), f"{agent_id} interface missing stride section"
        assert _STRIDE_KEYS.issubset(interface["stride"].keys()), f"{agent_id} stride section is incomplete"
        assert "threats" in interface and isinstance(interface["threats"], list)


def test_stix_packager_example_has_stix_bundle_contract() -> None:
    payload = _load_backend_expected_output_json("agent_06")

    assert payload.get("type") == "bundle"
    assert payload.get("spec_version") == "2.1"
    assert isinstance(payload.get("objects"), list) and payload["objects"]

    first_object = payload["objects"][0]
    assert "type" in first_object and "id" in first_object


def test_diagram_generator_example_uses_parser_contract() -> None:
    expected_output = backend_prompt_store._DEFAULT_PROMPTS["agent_08"]["expected_output"]

    assert "MERMAID_LEVEL0" in expected_output
    assert "```mermaid" in expected_output
    sections = re.findall(r"MERMAID_LEVEL(\d+)\s*```mermaid", expected_output)
    assert sections, "Diagram expected_output must include section markers with mermaid code fences"


def test_report_writer_example_includes_required_sections() -> None:
    expected_output = backend_prompt_store._DEFAULT_PROMPTS["agent_09"]["expected_output"]
    lowered = expected_output.lower()

    for section in _REQUIRED_SECTIONS:
        assert section.lower() in lowered, f"Missing required report section in expected_output: {section}"


def test_ui_and_backend_default_expected_outputs_stay_in_sync() -> None:
    for agent_id in backend_prompt_store.AGENT_IDS:
        backend_value = backend_prompt_store._DEFAULT_PROMPTS[agent_id]["expected_output"]
        ui_value = ui_prompt_store._DEFAULT_PROMPTS[agent_id]["expected_output"]
        assert backend_value == ui_value, f"UI and backend defaults diverged for {agent_id}"

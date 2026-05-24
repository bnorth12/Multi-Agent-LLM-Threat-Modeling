from __future__ import annotations

import json
from pathlib import Path

from threat_modeler.backend import prompt_store as backend_prompt_store
from threat_modeler.ui import prompt_store as ui_prompt_store


REQUIRED_STRUCTURED_SECTIONS = (
    "Purpose:",
    "Inputs:",
    "Outputs:",
    "System Prompt:",
    "Rules:",
)

STRUCTURED_BASELINE_AGENTS = (
    *backend_prompt_store.AGENT_IDS,
)

PROMPT_PARITY_BASELINE_AGENTS = backend_prompt_store.AGENT_IDS

CANONICAL_SHAPE_AGENTS = (
    "agent_01",
    "agent_02",
    "agent_03",
    "agent_04",
)

MIN_STRUCTURED_PROMPT_LENGTH = 400
REQUIRED_CANONICAL_KEYS = (
    "metadata",
    "system",
    "subsystems",
    "components",
    "functions",
    "interfaces",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_baseline_doc() -> str:
    baseline_path = _repo_root() / "Requirements" / "14_Prompt_Requirements_Baseline.md"
    return baseline_path.read_text(encoding="utf-8")


def test_prompt_baseline_document_contains_core_requirement_ids() -> None:
    baseline_doc = _load_baseline_doc()
    for requirement_id in ("PRM-001", "PRM-002", "PRM-003", "PRM-004", "PRM-005"):
        assert requirement_id in baseline_doc


def test_each_default_prompt_record_has_split_prompt_and_expected_output() -> None:
    for agent_id, record in backend_prompt_store._DEFAULT_PROMPTS.items():
        assert set(record.keys()) == {"prompt", "expected_output"}
        assert isinstance(record["prompt"], str) and record["prompt"].strip()
        assert isinstance(record["expected_output"], str) and record["expected_output"].strip()
        assert "```json" not in record["expected_output"]


def test_backend_and_ui_default_prompts_are_identical() -> None:
    backend = backend_prompt_store._DEFAULT_PROMPTS
    ui = ui_prompt_store._DEFAULT_PROMPTS

    assert backend.keys() == ui.keys()
    for agent_id in PROMPT_PARITY_BASELINE_AGENTS:
        assert backend[agent_id]["prompt"] == ui[agent_id]["prompt"]
        assert backend[agent_id]["expected_output"] == ui[agent_id]["expected_output"]


def test_structured_baseline_agents_have_required_sections_and_verbosity() -> None:
    for agent_id in STRUCTURED_BASELINE_AGENTS:
        prompt = backend_prompt_store._DEFAULT_PROMPTS[agent_id]["prompt"]
        for section in REQUIRED_STRUCTURED_SECTIONS:
            assert section in prompt, f"{agent_id} missing section: {section}"
        assert len(prompt) >= MIN_STRUCTURED_PROMPT_LENGTH


def test_canonical_shape_agents_expected_output_preserves_required_keys() -> None:
    for agent_id in CANONICAL_SHAPE_AGENTS:
        expected_output = backend_prompt_store._DEFAULT_PROMPTS[agent_id]["expected_output"]
        payload = json.loads(expected_output)

        for key in REQUIRED_CANONICAL_KEYS:
            assert key in payload, f"{agent_id} missing key: {key}"

        interfaces = payload.get("interfaces")
        assert isinstance(interfaces, list)
        assert interfaces, f"{agent_id} expected_output must include interface examples"

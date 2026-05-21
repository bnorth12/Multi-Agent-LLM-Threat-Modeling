"""SCR-010/011 — Per-agent prompt store with version history.

Manages a session-scoped dictionary of agent prompts and records an append-only
version history for each agent.  No file I/O is performed; all state lives in
st.session_state so it survives Streamlit reruns within a session but is reset
on page refresh.

Public API
----------
get_prompt(agent_id)            -> str   current system prompt text
set_prompt(agent_id, text, actor) -> None  save & record version
get_history(agent_id)           -> list[VersionEntry]
revert_to(agent_id, version_index, actor) -> None  restore a prior version
get_temperature(agent_id)       -> float
set_temperature(agent_id, value) -> None

All functions raise KeyError if agent_id is not in AGENT_IDS.
"""

from __future__ import annotations

import datetime
from typing import NamedTuple

import streamlit as st

# ---------------------------------------------------------------------------
# Agent catalogue — the nine pipeline agents
# ---------------------------------------------------------------------------
AGENT_IDS: tuple[str, ...] = (
    "agent_01",
    "agent_02",
    "agent_03",
    "agent_04",
    "agent_05",
    "agent_06",
    "agent_07",
    "agent_08",
    "agent_09",
)

AGENT_LABELS: dict[str, str] = {
    "agent_01": "01 — Input Normalizer",
    "agent_02": "02 — Hierarchical Context Builder",
    "agent_03": "03 — Trust Boundary Validator",
    "agent_04": "04 — STRIDE Scorer",
    "agent_05": "05 — Concrete Threat Generator",
    "agent_06": "06 — STIX Packager",
    "agent_07": "07 — Mitigation Generator",
    "agent_08": "08 — Diagram Generator",
    "agent_09": "09 — Human Report Writer",
}


# Default system prompts and expected outputs (expand as needed)
_DEFAULT_PROMPTS: dict[str, dict] = {
    "agent_01": {
        "prompt": (
            "You are an aerospace systems engineering parser that converts unstructured and "
            "semi-structured descriptions into strict canonical JSON. "
            "Use fully qualified node paths where possible. "
            "Infer missing IDs deterministically. "
            "Never invent data flows not present in source material. "
            "Output JSON only."
        ),
        "expected_output": '{\n  "system": {\n    "name": "UAS system",\n    "components": [\n      {"id": "mission_computer", "name": "Mission Computer"}\n    ]\n  }\n}'
    },
    "agent_02": {
        "prompt": (
            "You are a hierarchical systems analyst. Given a canonical graph, construct a "
            "multi-level context model that captures subsystem relationships, trust zones, "
            "and operational boundaries. Output canonical JSON only."
        ),
        "expected_output": '{\n  "subsystems": [\n    {"id": "uas", "name": "UAS", "parent_system": "uas_system"}\n  ]\n}'
    },
    "agent_03": {
        "prompt": (
            "You are a trust boundary auditor. Validate every edge in the canonical graph "
            "for correct trust_boundary_crossing flags and boundary names. "
            "Report violations and corrected values."
        ),
        "expected_output": '{\n  "violations": [],\n  "corrections": []\n}'
    },
    "agent_04": {
        "prompt": (
            "You are a STRIDE threat analyst. Score each data flow against all six STRIDE "
            "categories. Assign a severity (Critical/High/Medium/Low/Informational) and "
            "confidence score. Output JSON only."
        ),
        "expected_output": '{\n  "stride_scores": [\n    {"flow_id": "f1", "S": 2, "T": 1, "R": 0, "I": 0, "D": 0, "E": 0}\n  ]\n}'
    },
    "agent_05": {
        "prompt": (
            "You are a concrete threat generator. Using the STRIDE scores and canonical "
            "context, produce specific, actionable threat statements that reference real "
            "component IDs and flow IDs. Output JSON only."
        ),
        "expected_output": '{\n  "threats": [\n    {"id": "t1", "description": "Spoofing attack on datalink."}\n  ]\n}'
    },
    "agent_06": {
        "prompt": (
            "You are a STIX 2.1 packager. Convert the threat list into a valid STIX 2.1 "
            "bundle with attack-pattern, threat-actor, and relationship objects. "
            "Output JSON only."
        ),
        "expected_output": '{\n  "type": "bundle",\n  "objects": [\n    {"type": "attack-pattern", "id": "attack-pattern--1234"}\n  ]\n}'
    },
    "agent_07": {
        "prompt": (
            "You are a mitigation engineer. For each threat, propose one or more MITRE "
            "ATT&CK-aligned mitigations with implementation guidance and effort estimates. "
            "Output JSON only."
        ),
        "expected_output": '{\n  "mitigations": [\n    {"id": "m1", "description": "Encrypt datalink communications."}\n  ]\n}'
    },
    "agent_08": {
        "prompt": (
            "You are a diagram generator. Produce a Mermaid flowchart that shows the system "
            "architecture, trust boundaries, and top threats. Output Mermaid markdown only."
        ),
        "expected_output": '```mermaid\ngraph TD\n  A[UAS] -->|Datalink| B[Ground Station]\n```'
    },
    "agent_09": {
        "prompt": (
            "You are a technical report writer. Produce a comprehensive threat model report "
            "in Markdown format suitable for security review boards. Include executive summary, "
            "methodology, findings, mitigation, recommendations, and diagrams."
        ),
        "expected_output": (
            "# Threat Model Report\n"
            "\n"
            "## Executive Summary\n"
            "This report provides a comprehensive threat model for the UAS system, summarizing key risks and recommendations.\n"
            "\n"
            "## Table of Contents\n"
            "1. Executive Summary\n"
            "2. Methodology\n"
            "3. System Overview\n"
            "4. Threat Analysis\n"
            "5. Findings\n"
            "6. Mitigation\n"
            "7. Recommendations\n"
            "8. Mermaid Diagrams\n"
            "9. Appendix\n"
            "\n"
            "## Methodology\n"
            "- Approach: STRIDE, STIX 2.1, MITRE ATT&CK\n"
            "- Data sources: Canonical system model, context graph\n"
            "\n"
            "## System Overview\n"
            "- System Name: UAS\n"
            "- Major Components: Mission Computer, Datalink, Ground Station\n"
            "- Diagram: See Mermaid diagram section\n"
            "\n"
            "## Threat Analysis\n"
            "| Threat ID | Description | Severity |\n"
            "|-----------|-------------|----------|\n"
            "| T-001     | Spoofing attack on datalink | High |\n"
            "| T-002     | Data tampering in ground station | Medium |\n"
            "\n"
            "## Findings\n"
            "- The datalink is vulnerable to spoofing due to lack of encryption.\n"
            "- Ground station authentication is insufficient.\n"
            "\n"
            "## Mitigation\n"
            "- Encrypt datalink communications to prevent spoofing.\n"
            "- Implement multi-factor authentication for ground station access.\n"
            "\n"
            "## Recommendations\n"
            "- Implement end-to-end encryption on datalink.\n"
            "- Strengthen ground station authentication.\n"
            "\n"
            "## Mermaid Diagrams\n"
            "```mermaid\ngraph TD\n  A[UAS] -->|Datalink| B[Ground Station]\n```\n"
            "- Architecture, trust boundaries, and threat flows are visualized above.\n"
            "\n"
            "## Appendix\n"
            "- Full STRIDE scoring table\n"
            "- STIX 2.1 bundle\n"
            "- Additional diagrams and references\n"
        )
    },
}

_DEFAULT_TEMPERATURES: dict[str, float] = {agent: 0.2 for agent in AGENT_IDS}

# ---------------------------------------------------------------------------
# Version entry
# ---------------------------------------------------------------------------

class VersionEntry(NamedTuple):
    version: int        # 1-based sequence number
    text: str           # prompt text at this version
    actor: str          # role or user identifier
    timestamp: str      # ISO-8601 UTC string



# ---------------------------------------------------------------------------
# Session state keys
# ---------------------------------------------------------------------------
_KEY_PROMPTS = "prompt_store_prompts"
_KEY_EXPECTED_OUTPUTS = "prompt_store_expected_outputs"
_KEY_HISTORIES = "prompt_store_histories"
_KEY_TEMPERATURES = "prompt_store_temperatures"



def _ensure_initialised() -> None:
    """Lazily populate prompt store keys into st.session_state."""
    if _KEY_PROMPTS not in st.session_state:
        st.session_state[_KEY_PROMPTS] = {k: v["prompt"] for k, v in _DEFAULT_PROMPTS.items()}
    if _KEY_EXPECTED_OUTPUTS not in st.session_state:
        st.session_state[_KEY_EXPECTED_OUTPUTS] = {k: v["expected_output"] for k, v in _DEFAULT_PROMPTS.items()}
    if _KEY_HISTORIES not in st.session_state:
        # Seed each agent with version 1 = default prompt (actor = "system")
        st.session_state[_KEY_HISTORIES] = {
            agent_id: [
                VersionEntry(
                    version=1,
                    text=_DEFAULT_PROMPTS[agent_id]["prompt"],
                    actor="system",
                    timestamp=_utc_now(),
                )
            ]
            for agent_id in AGENT_IDS
        }
    if _KEY_TEMPERATURES not in st.session_state:
        st.session_state[_KEY_TEMPERATURES] = dict(_DEFAULT_TEMPERATURES)


def _utc_now() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_agent(agent_id: str) -> None:
    if agent_id not in AGENT_IDS:
        raise KeyError(f"Unknown agent_id '{agent_id}'. Must be one of {AGENT_IDS}.")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_prompt(agent_id: str) -> str:
    """Return the current system prompt for agent_id from backend store."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    prompt = backend_prompt_store.get_prompt(agent_id)
    _ensure_initialised()
    st.session_state[_KEY_PROMPTS][agent_id] = prompt
    return prompt

def get_expected_output(agent_id: str) -> str:
    """Return the expected output example for agent_id from backend store."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    expected_output = backend_prompt_store.get_expected_output(agent_id)
    _ensure_initialised()
    st.session_state[_KEY_EXPECTED_OUTPUTS][agent_id] = expected_output
    return expected_output

def set_prompt(agent_id: str, text: str, actor: str = "user") -> None:
    """Save a new prompt for agent_id in backend store and mirror to session."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    backend_prompt_store.set_prompt(agent_id, text, actor=actor)

    _ensure_initialised()
    st.session_state[_KEY_PROMPTS][agent_id] = text
    st.session_state[_KEY_HISTORIES][agent_id] = list(backend_prompt_store.get_history(agent_id))

def set_expected_output(agent_id: str, example: str) -> None:
    """Save a new expected output example for agent_id in backend store and mirror to session."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    backend_prompt_store.set_expected_output(agent_id, example)
    _ensure_initialised()
    st.session_state[_KEY_EXPECTED_OUTPUTS][agent_id] = example


def get_history(agent_id: str) -> list[VersionEntry]:
    """Return the full version history for agent_id from backend store."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    history = backend_prompt_store.get_history(agent_id)
    _ensure_initialised()
    st.session_state[_KEY_HISTORIES][agent_id] = list(history)
    return list(history)


def revert_to(agent_id: str, version_index: int, actor: str = "user") -> None:
    """Restore a prior version by its 0-based list index in backend store."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    backend_prompt_store.revert_to(agent_id, version_index, actor=actor)
    _ensure_initialised()
    st.session_state[_KEY_PROMPTS][agent_id] = backend_prompt_store.get_prompt(agent_id)
    st.session_state[_KEY_HISTORIES][agent_id] = list(backend_prompt_store.get_history(agent_id))


def get_temperature(agent_id: str) -> float:
    """Return the current temperature setting for agent_id from backend store."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    temperature = backend_prompt_store.get_temperature(agent_id)
    _ensure_initialised()
    st.session_state[_KEY_TEMPERATURES][agent_id] = temperature
    return temperature


def set_temperature(agent_id: str, value: float) -> None:
    """Persist a temperature value (0.0–2.0) for agent_id in backend store."""
    _validate_agent(agent_id)
    if not (0.0 <= value <= 2.0):
        raise ValueError(f"Temperature must be in [0.0, 2.0]; got {value}.")
    from threat_modeler.backend import prompt_store as backend_prompt_store

    backend_prompt_store.set_temperature(agent_id, value)
    _ensure_initialised()
    st.session_state[_KEY_TEMPERATURES][agent_id] = value


def reset_to_default(agent_id: str, actor: str = "user") -> None:
    """Reset agent_id prompt and temperature to backend defaults."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    backend_prompt_store.reset_to_default(agent_id, actor=actor)
    _ensure_initialised()
    st.session_state[_KEY_PROMPTS][agent_id] = backend_prompt_store.get_prompt(agent_id)
    st.session_state[_KEY_EXPECTED_OUTPUTS][agent_id] = backend_prompt_store.get_expected_output(agent_id)
    st.session_state[_KEY_TEMPERATURES][agent_id] = backend_prompt_store.get_temperature(agent_id)
    st.session_state[_KEY_HISTORIES][agent_id] = list(backend_prompt_store.get_history(agent_id))


def is_modified(agent_id: str) -> bool:
    """Return True if backend current prompt differs from default."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    return backend_prompt_store.is_modified(agent_id)


def get_default_prompt(agent_id: str) -> str:
    """Return the default system prompt for agent_id from backend store."""
    _validate_agent(agent_id)
    from threat_modeler.backend import prompt_store as backend_prompt_store

    return backend_prompt_store.get_default_prompt(agent_id)

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

# Default system prompts (trimmed single-line form; user can expand in the editor)
_DEFAULT_PROMPTS: dict[str, str] = {
    "agent_01": (
        "You are an aerospace systems engineering parser that converts unstructured and "
        "semi-structured descriptions into strict canonical JSON. "
        "Use fully qualified node paths where possible. "
        "Infer missing IDs deterministically. "
        "Never invent data flows not present in source material. "
        "Output JSON only."
    ),
    "agent_02": (
        "You are a hierarchical systems analyst. Given a canonical graph, construct a "
        "multi-level context model that captures subsystem relationships, trust zones, "
        "and operational boundaries. Output canonical JSON only."
    ),
    "agent_03": (
        "You are a trust boundary auditor. Validate every edge in the canonical graph "
        "for correct trust_boundary_crossing flags and boundary names. "
        "Report violations and corrected values."
    ),
    "agent_04": (
        "You are a STRIDE threat analyst. Score each data flow against all six STRIDE "
        "categories. Assign a severity (Critical/High/Medium/Low/Informational) and "
        "confidence score. Output JSON only."
    ),
    "agent_05": (
        "You are a concrete threat generator. Using the STRIDE scores and canonical "
        "context, produce specific, actionable threat statements that reference real "
        "component IDs and flow IDs. Output JSON only."
    ),
    "agent_06": (
        "You are a STIX 2.1 packager. Convert the threat list into a valid STIX 2.1 "
        "bundle with attack-pattern, threat-actor, and relationship objects. "
        "Output JSON only."
    ),
    "agent_07": (
        "You are a mitigation engineer. For each threat, propose one or more MITRE "
        "ATT&CK-aligned mitigations with implementation guidance and effort estimates. "
        "Output JSON only."
    ),
    "agent_08": (
        "You are a diagram generator. Produce a Mermaid flowchart that shows the system "
        "architecture, trust boundaries, and top threats. Output Mermaid markdown only."
    ),
    "agent_09": (
        "You are a technical report writer. Produce a comprehensive threat model report "
        "in Markdown format suitable for security review boards. Include executive summary, "
        "methodology, findings, and recommendations."
    ),
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
_KEY_HISTORIES = "prompt_store_histories"
_KEY_TEMPERATURES = "prompt_store_temperatures"


def _ensure_initialised() -> None:
    """Lazily populate prompt store keys into st.session_state."""
    if _KEY_PROMPTS not in st.session_state:
        st.session_state[_KEY_PROMPTS] = dict(_DEFAULT_PROMPTS)
    if _KEY_HISTORIES not in st.session_state:
        # Seed each agent with version 1 = default prompt (actor = "system")
        st.session_state[_KEY_HISTORIES] = {
            agent_id: [
                VersionEntry(
                    version=1,
                    text=_DEFAULT_PROMPTS[agent_id],
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
    """Return the current system prompt for agent_id."""
    _validate_agent(agent_id)
    _ensure_initialised()
    return st.session_state[_KEY_PROMPTS][agent_id]


def set_prompt(agent_id: str, text: str, actor: str = "user") -> None:
    """Save a new prompt for agent_id and record a version history entry."""
    _validate_agent(agent_id)
    _ensure_initialised()
    st.session_state[_KEY_PROMPTS][agent_id] = text
    history: list[VersionEntry] = st.session_state[_KEY_HISTORIES][agent_id]
    next_version = history[-1].version + 1 if history else 1
    history.append(
        VersionEntry(
            version=next_version,
            text=text,
            actor=actor,
            timestamp=_utc_now(),
        )
    )


def get_history(agent_id: str) -> list[VersionEntry]:
    """Return the full version history for agent_id, oldest first."""
    _validate_agent(agent_id)
    _ensure_initialised()
    return list(st.session_state[_KEY_HISTORIES][agent_id])


def revert_to(agent_id: str, version_index: int, actor: str = "user") -> None:
    """Restore a prior version by its 0-based list index and create a new version entry."""
    _validate_agent(agent_id)
    _ensure_initialised()
    history = st.session_state[_KEY_HISTORIES][agent_id]
    if version_index < 0 or version_index >= len(history):
        raise IndexError(
            f"version_index {version_index} out of range for agent '{agent_id}' "
            f"(history length {len(history)})."
        )
    prior_text = history[version_index].text
    set_prompt(agent_id, prior_text, actor=f"{actor} (revert to v{history[version_index].version})")


def get_temperature(agent_id: str) -> float:
    """Return the current temperature setting for agent_id."""
    _validate_agent(agent_id)
    _ensure_initialised()
    return st.session_state[_KEY_TEMPERATURES][agent_id]


def set_temperature(agent_id: str, value: float) -> None:
    """Persist a temperature value (0.0–2.0) for agent_id."""
    _validate_agent(agent_id)
    if not (0.0 <= value <= 2.0):
        raise ValueError(f"Temperature must be in [0.0, 2.0]; got {value}.")
    _ensure_initialised()
    st.session_state[_KEY_TEMPERATURES][agent_id] = value


def reset_to_default(agent_id: str, actor: str = "user") -> None:
    """Reset agent_id to its default prompt and record the change."""
    _validate_agent(agent_id)
    _ensure_initialised()
    set_prompt(agent_id, _DEFAULT_PROMPTS[agent_id], actor=f"{actor} (reset to default)")
    st.session_state[_KEY_TEMPERATURES][agent_id] = _DEFAULT_TEMPERATURES[agent_id]


def is_modified(agent_id: str) -> bool:
    """Return True if the current prompt differs from the default."""
    _validate_agent(agent_id)
    _ensure_initialised()
    return st.session_state[_KEY_PROMPTS][agent_id] != _DEFAULT_PROMPTS[agent_id]


def get_default_prompt(agent_id: str) -> str:
    """Return the default (built-in) system prompt for agent_id."""
    _validate_agent(agent_id)
    return _DEFAULT_PROMPTS[agent_id]

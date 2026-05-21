"""File-backed per-agent prompt store.

Pure Python — no Streamlit dependency.  Stores agent system prompts,
version histories, and temperature settings in a JSON file so they persist
across process restarts and are available to any execution context (CLI, web
server, or test runner) without a Streamlit session.

Public API (mirrors ``ui/prompt_store.py``)
-------------------------------------------
get_prompt(agent_id)              -> str
set_prompt(agent_id, text, actor) -> None
get_history(agent_id)             -> list[VersionEntry]
revert_to(agent_id, idx, actor)   -> None
get_temperature(agent_id)         -> float
set_temperature(agent_id, value)  -> None
reset_to_default(agent_id, actor) -> None
is_modified(agent_id)             -> bool
get_default_prompt(agent_id)      -> str

All functions raise ``KeyError`` if *agent_id* is not in ``AGENT_IDS``.
``set_temperature`` raises ``ValueError`` for values outside [0.0, 2.0].

Thread safety
-------------
A module-level ``threading.Lock`` protects all mutations to the global
default store.  A ``PromptStore`` instance can also be used directly when
tests need isolated state (pass ``store_path=None`` for in-memory-only).
"""

from __future__ import annotations

import datetime
import json
import os
import threading
from pathlib import Path
from typing import NamedTuple, Optional

# ---------------------------------------------------------------------------
# Agent catalogue
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

_DEFAULT_PROMPTS: dict[str, str] = {
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

# Default file location for the global store instance.
_DEFAULT_STORE_PATH = Path(
    os.environ.get(
        "THREAT_MODELER_PROMPT_STORE_PATH",
        str(Path.home() / ".multi_agent_threat_modeler_prompts.json"),
    )
)


# ---------------------------------------------------------------------------
# Version entry
# ---------------------------------------------------------------------------

class VersionEntry(NamedTuple):
    version: int     # 1-based sequence number
    text: str        # prompt text at this version
    actor: str       # role or user identifier
    timestamp: str   # ISO-8601 UTC string


# ---------------------------------------------------------------------------
# PromptStore class
# ---------------------------------------------------------------------------

class PromptStore:
    """Thread-safe, optionally file-backed prompt store.

    Args:
        store_path: Path to the JSON backing file.  Pass ``None`` to use an
                    in-memory-only store (useful for isolated unit tests).
    """

    def __init__(self, store_path: Optional[Path] = _DEFAULT_STORE_PATH) -> None:
        self._lock = threading.Lock()
        self._store_path = store_path
        self._prompts: dict[str, str] = {k: v["prompt"] for k, v in _DEFAULT_PROMPTS.items()}
        self._expected_outputs: dict[str, str] = {k: v["expected_output"] for k, v in _DEFAULT_PROMPTS.items()}
        self._histories: dict[str, list[VersionEntry]] = {
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
        self._temperatures: dict[str, float] = dict(_DEFAULT_TEMPERATURES)

        if store_path is not None:
            self._load_from_disk()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_from_disk(self) -> None:
        if self._store_path is None or not self._store_path.exists():
            return
        try:
            payload = json.loads(self._store_path.read_text(encoding="utf-8"))
        except Exception:
            return
        if not isinstance(payload, dict):
            return

        with self._lock:
            prompts = payload.get("prompts", {})
            if isinstance(prompts, dict):
                for aid in AGENT_IDS:
                    if aid in prompts and isinstance(prompts[aid], str):
                        self._prompts[aid] = prompts[aid]

            expected_outputs = payload.get("expected_outputs", {})
            if isinstance(expected_outputs, dict):
                for aid in AGENT_IDS:
                    if aid in expected_outputs and isinstance(expected_outputs[aid], str):
                        self._expected_outputs[aid] = expected_outputs[aid]

            histories = payload.get("histories", {})
            if isinstance(histories, dict):
                for aid in AGENT_IDS:
                    raw = histories.get(aid)
                    if isinstance(raw, list):
                        entries: list[VersionEntry] = []
                        for item in raw:
                            if isinstance(item, dict):
                                try:
                                    entries.append(
                                        VersionEntry(
                                            version=int(item["version"]),
                                            text=str(item["text"]),
                                            actor=str(item["actor"]),
                                            timestamp=str(item["timestamp"]),
                                        )
                                    )
                                except (KeyError, ValueError):
                                    pass
                        if entries:
                            self._histories[aid] = entries

            temperatures = payload.get("temperatures", {})
            if isinstance(temperatures, dict):
                for aid in AGENT_IDS:
                    val = temperatures.get(aid)
                    if isinstance(val, (int, float)) and 0.0 <= float(val) <= 2.0:
                        self._temperatures[aid] = float(val)

    def _save_to_disk(self) -> None:
        if self._store_path is None:
            return
        payload = {
            "prompts": dict(self._prompts),
            "expected_outputs": dict(self._expected_outputs),
            "histories": {
                aid: [
                    {
                        "version": entry.version,
                        "text": entry.text,
                        "actor": entry.actor,
                        "timestamp": entry.timestamp,
                    }
                    for entry in entries
                ]
                for aid, entries in self._histories.items()
            },
            "temperatures": dict(self._temperatures),
        }
        try:
            self._store_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_agent(self, agent_id: str) -> None:
        if agent_id not in AGENT_IDS:
            raise KeyError(f"Unknown agent_id '{agent_id}'. Must be one of {AGENT_IDS}.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_prompt(self, agent_id: str) -> str:
        self._validate_agent(agent_id)
        with self._lock:
            return self._prompts[agent_id]

    def get_expected_output(self, agent_id: str) -> str:
        self._validate_agent(agent_id)
        with self._lock:
            return self._expected_outputs[agent_id]

    def set_expected_output(self, agent_id: str, example: str) -> None:
        self._validate_agent(agent_id)
        with self._lock:
            self._expected_outputs[agent_id] = example
            self._save_to_disk()

    def set_prompt(self, agent_id: str, text: str, actor: str = "user") -> None:
        self._validate_agent(agent_id)
        with self._lock:
            self._prompts[agent_id] = text
            history = self._histories[agent_id]
            next_version = history[-1].version + 1 if history else 1
            history.append(
                VersionEntry(
                    version=next_version,
                    text=text,
                    actor=actor,
                    timestamp=_utc_now(),
                )
            )
            self._save_to_disk()

    def get_history(self, agent_id: str) -> list[VersionEntry]:
        self._validate_agent(agent_id)
        with self._lock:
            return list(self._histories[agent_id])

    def revert_to(self, agent_id: str, version_index: int, actor: str = "user") -> None:
        self._validate_agent(agent_id)
        with self._lock:
            history = self._histories[agent_id]
            if version_index < 0 or version_index >= len(history):
                raise IndexError(
                    f"version_index {version_index} out of range for agent '{agent_id}' "
                    f"(history length {len(history)})."
                )
            prior = history[version_index]
        self.set_prompt(agent_id, prior.text, actor=f"{actor} (revert to v{prior.version})")

    def get_temperature(self, agent_id: str) -> float:
        self._validate_agent(agent_id)
        with self._lock:
            return self._temperatures[agent_id]

    def set_temperature(self, agent_id: str, value: float) -> None:
        self._validate_agent(agent_id)
        if not (0.0 <= value <= 2.0):
            raise ValueError(f"Temperature must be in [0.0, 2.0]; got {value}.")
        with self._lock:
            self._temperatures[agent_id] = value
            self._save_to_disk()

    def reset_to_default(self, agent_id: str, actor: str = "user") -> None:
        self._validate_agent(agent_id)
        self.set_prompt(agent_id, _DEFAULT_PROMPTS[agent_id]["prompt"], actor=f"{actor} (reset to default)")
        with self._lock:
            self._temperatures[agent_id] = _DEFAULT_TEMPERATURES[agent_id]
            self._save_to_disk()

    def is_modified(self, agent_id: str) -> bool:
        self._validate_agent(agent_id)
        with self._lock:
            return self._prompts[agent_id] != _DEFAULT_PROMPTS[agent_id]["prompt"]

    def get_default_prompt(self, agent_id: str) -> str:
        self._validate_agent(agent_id)
        return _DEFAULT_PROMPTS[agent_id]["prompt"]


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Global default store instance
# ---------------------------------------------------------------------------

_default_store = PromptStore(store_path=_DEFAULT_STORE_PATH)


# ---------------------------------------------------------------------------
# Module-level public API (delegates to global store)
# ---------------------------------------------------------------------------

def get_prompt(agent_id: str) -> str:
    """Return the current system prompt for *agent_id* from the global store."""
    return _default_store.get_prompt(agent_id)


def set_prompt(agent_id: str, text: str, actor: str = "user") -> None:
    """Save a new prompt for *agent_id* and record a version history entry."""
    _default_store.set_prompt(agent_id, text, actor)


def get_expected_output(agent_id: str) -> str:
    """Return the current expected output for *agent_id* from the global store."""
    return _default_store.get_expected_output(agent_id)

def set_expected_output(agent_id: str, example: str) -> None:
    """Save a new expected output example for *agent_id*."""
    _default_store.set_expected_output(agent_id, example)


def get_history(agent_id: str) -> list[VersionEntry]:
    """Return full version history for *agent_id*, oldest first."""
    return _default_store.get_history(agent_id)


def revert_to(agent_id: str, version_index: int, actor: str = "user") -> None:
    """Restore a prior prompt version by 0-based history index."""
    _default_store.revert_to(agent_id, version_index, actor)


def get_temperature(agent_id: str) -> float:
    """Return configured model temperature for *agent_id*."""
    return _default_store.get_temperature(agent_id)


def set_temperature(agent_id: str, value: float) -> None:
    """Set model temperature for *agent_id* in [0.0, 2.0]."""
    _default_store.set_temperature(agent_id, value)


def reset_to_default(agent_id: str, actor: str = "user") -> None:
    """Reset prompt and temperature for *agent_id* to defaults."""
    _default_store.reset_to_default(agent_id, actor)


def is_modified(agent_id: str) -> bool:
    """Return True when current prompt differs from default for *agent_id*."""
    return _default_store.is_modified(agent_id)


def get_default_prompt(agent_id: str) -> str:
    """Return default prompt text for *agent_id*."""
    return _default_store.get_default_prompt(agent_id)


def get_store_path() -> str:
    """Return the absolute path of the active prompt store file."""
    return str(_DEFAULT_STORE_PATH)

"""UI-facing prompt store API.

This module preserves the historical UI import path while delegating storage and
versioning operations to the backend prompt store, which is the canonical
prompt source for all agents.
"""

from __future__ import annotations

from threat_modeler.backend import prompt_store as backend_prompt_store

AGENT_IDS = backend_prompt_store.AGENT_IDS
AGENT_LABELS = backend_prompt_store.AGENT_LABELS
VersionEntry = backend_prompt_store.VersionEntry
_DEFAULT_PROMPTS = backend_prompt_store._DEFAULT_PROMPTS


def get_prompt(agent_id: str) -> str:
    return backend_prompt_store.get_prompt(agent_id)


def set_prompt(agent_id: str, text: str, actor: str = "analyst") -> None:
    backend_prompt_store.set_prompt(agent_id, text, actor)


def get_history(agent_id: str) -> list[VersionEntry]:
    return backend_prompt_store.get_history(agent_id)


def revert_to(agent_id: str, version_index: int, actor: str = "analyst") -> None:
    backend_prompt_store.revert_to(agent_id, version_index, actor)


def get_temperature(agent_id: str) -> float:
    return backend_prompt_store.get_temperature(agent_id)


def set_temperature(agent_id: str, value: float) -> None:
    backend_prompt_store.set_temperature(agent_id, value)


def reset_to_default(agent_id: str, actor: str = "analyst") -> None:
    backend_prompt_store.reset_to_default(agent_id, actor)


def is_modified(agent_id: str) -> bool:
    return backend_prompt_store.is_modified(agent_id)


def get_default_prompt(agent_id: str) -> str:
    return backend_prompt_store.get_default_prompt(agent_id)

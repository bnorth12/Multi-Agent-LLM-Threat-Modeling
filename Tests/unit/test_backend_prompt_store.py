"""Unit tests for backend.prompt_store — no Streamlit dependency.

Uses an in-memory (``store_path=None``) ``PromptStore`` instance for
complete isolation between tests.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from threat_modeler.backend.prompt_store import (
    AGENT_IDS,
    AGENT_LABELS,
    PromptStore,
    VersionEntry,
    get_default_prompt,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _store() -> PromptStore:
    """Return a fresh in-memory PromptStore for each test."""
    return PromptStore(store_path=None)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_nine_agent_ids(self):
        assert len(AGENT_IDS) == 9

    def test_agent_ids_sequential(self):
        for i, aid in enumerate(AGENT_IDS, start=1):
            assert aid == f"agent_0{i}", f"Expected agent_0{i}, got {aid}"

    def test_labels_cover_all_agents(self):
        for agent_id in AGENT_IDS:
            assert agent_id in AGENT_LABELS
            assert len(AGENT_LABELS[agent_id]) > 5

    def test_default_prompts_non_empty(self):
        for agent_id in AGENT_IDS:
            assert len(get_default_prompt(agent_id)) > 20


# ---------------------------------------------------------------------------
# PromptStore.get_prompt / set_prompt
# ---------------------------------------------------------------------------

class TestGetSetPrompt:
    def test_initial_prompt_equals_default(self):
        ps = _store()
        for agent_id in AGENT_IDS:
            assert ps.get_prompt(agent_id) == get_default_prompt(agent_id)

    def test_set_prompt_updates_current(self):
        ps = _store()
        ps.set_prompt("agent_01", "New text", actor="Author")
        assert ps.get_prompt("agent_01") == "New text"

    def test_set_prompt_does_not_affect_other_agents(self):
        ps = _store()
        original_02 = ps.get_prompt("agent_02")
        ps.set_prompt("agent_01", "Changed", actor="Author")
        assert ps.get_prompt("agent_02") == original_02

    def test_unknown_agent_raises_key_error(self):
        ps = _store()
        with pytest.raises(KeyError):
            ps.get_prompt("agent_99")

    def test_set_unknown_agent_raises_key_error(self):
        ps = _store()
        with pytest.raises(KeyError):
            ps.set_prompt("agent_99", "text", actor="Author")


# ---------------------------------------------------------------------------
# Version history
# ---------------------------------------------------------------------------

class TestVersionHistory:
    def test_initial_history_has_one_entry(self):
        ps = _store()
        history = ps.get_history("agent_01")
        assert len(history) == 1

    def test_initial_entry_is_version_1(self):
        ps = _store()
        entry = ps.get_history("agent_01")[0]
        assert entry.version == 1

    def test_initial_entry_actor_is_system(self):
        ps = _store()
        entry = ps.get_history("agent_01")[0]
        assert entry.actor == "system"

    def test_set_prompt_appends_history(self):
        ps = _store()
        ps.set_prompt("agent_01", "v2 text", actor="Author")
        history = ps.get_history("agent_01")
        assert len(history) == 2
        assert history[-1].text == "v2 text"
        assert history[-1].actor == "Author"
        assert history[-1].version == 2

    def test_version_numbers_increment_monotonically(self):
        ps = _store()
        ps.set_prompt("agent_02", "A", actor="Author")
        ps.set_prompt("agent_02", "B", actor="Author")
        versions = [e.version for e in ps.get_history("agent_02")]
        assert versions == list(range(1, len(versions) + 1))

    def test_get_history_returns_copy(self):
        ps = _store()
        h1 = ps.get_history("agent_01")
        h2 = ps.get_history("agent_01")
        assert h1 is not h2

    def test_history_entries_are_version_entries(self):
        ps = _store()
        for entry in ps.get_history("agent_01"):
            assert isinstance(entry, VersionEntry)


# ---------------------------------------------------------------------------
# revert_to
# ---------------------------------------------------------------------------

class TestRevertTo:
    def test_revert_restores_text(self):
        ps = _store()
        original = ps.get_prompt("agent_03")
        ps.set_prompt("agent_03", "Changed text", actor="Author")
        ps.revert_to("agent_03", 0, actor="Author")
        assert ps.get_prompt("agent_03") == original

    def test_revert_creates_new_history_entry(self):
        ps = _store()
        ps.set_prompt("agent_03", "Changed", actor="Author")
        before = len(ps.get_history("agent_03"))
        ps.revert_to("agent_03", 0, actor="Author")
        assert len(ps.get_history("agent_03")) == before + 1

    def test_revert_out_of_range_raises_index_error(self):
        ps = _store()
        with pytest.raises(IndexError):
            ps.revert_to("agent_03", 999, actor="Author")

    def test_revert_negative_index_raises_index_error(self):
        ps = _store()
        with pytest.raises(IndexError):
            ps.revert_to("agent_03", -1, actor="Author")


# ---------------------------------------------------------------------------
# Temperature
# ---------------------------------------------------------------------------

class TestTemperature:
    def test_default_temperature_is_0_2(self):
        ps = _store()
        for agent_id in AGENT_IDS:
            assert abs(ps.get_temperature(agent_id) - 0.2) < 0.001

    def test_set_temperature_persists(self):
        ps = _store()
        ps.set_temperature("agent_01", 0.8)
        assert abs(ps.get_temperature("agent_01") - 0.8) < 0.001

    def test_temperature_boundary_0_accepted(self):
        ps = _store()
        ps.set_temperature("agent_01", 0.0)
        assert ps.get_temperature("agent_01") == 0.0

    def test_temperature_boundary_2_accepted(self):
        ps = _store()
        ps.set_temperature("agent_01", 2.0)
        assert ps.get_temperature("agent_01") == 2.0

    def test_temperature_out_of_range_raises_value_error(self):
        ps = _store()
        with pytest.raises(ValueError):
            ps.set_temperature("agent_01", 2.5)

    def test_temperature_negative_raises_value_error(self):
        ps = _store()
        with pytest.raises(ValueError):
            ps.set_temperature("agent_01", -0.1)

    def test_temperature_unknown_agent_raises_key_error(self):
        ps = _store()
        with pytest.raises(KeyError):
            ps.get_temperature("agent_99")


# ---------------------------------------------------------------------------
# is_modified / reset_to_default
# ---------------------------------------------------------------------------

class TestModifiedAndReset:
    def test_not_modified_initially(self):
        ps = _store()
        for agent_id in AGENT_IDS:
            assert ps.is_modified(agent_id) is False

    def test_modified_after_set(self):
        ps = _store()
        ps.set_prompt("agent_04", "Something different", actor="Author")
        assert ps.is_modified("agent_04") is True

    def test_not_modified_after_reset(self):
        ps = _store()
        ps.set_prompt("agent_04", "Something different", actor="Author")
        ps.reset_to_default("agent_04", actor="Author")
        assert ps.is_modified("agent_04") is False

    def test_reset_restores_default_temperature(self):
        ps = _store()
        ps.set_temperature("agent_05", 1.5)
        ps.reset_to_default("agent_05", actor="Author")
        assert abs(ps.get_temperature("agent_05") - 0.2) < 0.001


# ---------------------------------------------------------------------------
# JSON file persistence
# ---------------------------------------------------------------------------

class TestJsonPersistence:
    def test_changes_survive_reload(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            ps1 = PromptStore(store_path=path)
            ps1.set_prompt("agent_01", "Persisted prompt", actor="Author")
            ps1.set_temperature("agent_01", 1.0)

            ps2 = PromptStore(store_path=path)
            assert ps2.get_prompt("agent_01") == "Persisted prompt"
            assert abs(ps2.get_temperature("agent_01") - 1.0) < 0.001
        finally:
            path.unlink(missing_ok=True)

    def test_history_survives_reload(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            ps1 = PromptStore(store_path=path)
            ps1.set_prompt("agent_02", "v2", actor="Author")

            ps2 = PromptStore(store_path=path)
            history = ps2.get_history("agent_02")
            assert len(history) == 2
            assert history[-1].text == "v2"
        finally:
            path.unlink(missing_ok=True)

    def test_corrupt_file_handled_gracefully(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("NOT VALID JSON {{{{")
            path = Path(f.name)

        try:
            ps = PromptStore(store_path=path)
            # Should fall back to defaults without raising.
            assert ps.get_prompt("agent_01") == get_default_prompt("agent_01")
        finally:
            path.unlink(missing_ok=True)

    def test_missing_file_handled_gracefully(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)
        path.unlink()  # Remove so the store sees a genuinely missing file.
        # Store should initialise with defaults without raising.
        ps = PromptStore(store_path=path)
        assert ps.get_prompt("agent_01") == get_default_prompt("agent_01")
        # Clean up any file the store may have written on set_prompt.
        path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------

class TestThreadSafety:
    def test_concurrent_set_prompt_does_not_corrupt_history(self):
        import threading

        ps = _store()
        errors: list[Exception] = []

        def _writer(agent_id: str, count: int) -> None:
            for i in range(count):
                try:
                    ps.set_prompt(agent_id, f"text-{i}", actor="thread")
                except Exception as exc:
                    errors.append(exc)

        threads = [threading.Thread(target=_writer, args=("agent_01", 50)) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Concurrent writes produced errors: {errors}"
        history = ps.get_history("agent_01")
        # Version numbers must be strictly sequential.
        versions = [e.version for e in history]
        assert versions == list(range(1, len(versions) + 1))


# ---------------------------------------------------------------------------
# No Streamlit dependency
# ---------------------------------------------------------------------------

class TestNoStreamlitDependency:
    def test_prompt_store_has_no_st_attribute(self):
        import threat_modeler.backend.prompt_store as ps_mod
        assert not hasattr(ps_mod, "st"), "backend.prompt_store must not import streamlit as 'st'"

    def test_prompt_store_importable_without_streamlit_in_path(self):
        import sys
        original = sys.modules.pop("streamlit", None)
        try:
            import importlib
            import threat_modeler.backend.prompt_store as ps_mod
            importlib.reload(ps_mod)
            # Should not raise even if streamlit is not installed / present.
        except ImportError as exc:
            if "streamlit" in str(exc).lower():
                pytest.fail(f"prompt_store imported streamlit unexpectedly: {exc}")
        finally:
            if original is not None:
                sys.modules["streamlit"] = original

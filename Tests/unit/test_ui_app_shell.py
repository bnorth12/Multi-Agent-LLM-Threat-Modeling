"""Unit tests for S06-07: Streamlit Application Shell.

Strategy: Streamlit screen functions call st.* which requires a running
Streamlit server. Tests patch the entire streamlit module so logic and
module structure can be verified without a running server.
"""

from __future__ import annotations

import sys
import types
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call
import pytest


# ---------------------------------------------------------------------------
# Helpers — build a minimal streamlit stub that records calls
# ---------------------------------------------------------------------------

def _make_st_stub() -> MagicMock:
    """Return a MagicMock that accepts any st.* call silently."""
    stub = MagicMock()
    # st.session_state must behave like a dict
    stub.session_state = {}
    # Forms require a context manager
    stub.form.return_value.__enter__ = MagicMock(return_value=None)
    stub.form.return_value.__exit__ = MagicMock(return_value=False)
    return stub


# ---------------------------------------------------------------------------
# Session initialisation
# ---------------------------------------------------------------------------

class TestSessionInit:
    def test_all_defaults_set_on_empty_state(self):
        st_stub = _make_st_stub()
        with patch.dict(sys.modules, {"streamlit": st_stub}):
            from threat_modeler.ui.session import init_session_state
            init_session_state()

        state = st_stub.session_state
        assert "role" in state
        assert "run_id" in state
        assert "pipeline_state" in state
        assert "gate_states" in state
        assert "settings_override" in state
        assert "theme" in state

    def test_defaults_not_overwritten_if_key_already_set(self):
        st_stub = _make_st_stub()
        st_stub.session_state["role"] = "Reviewer"
        with patch.dict(sys.modules, {"streamlit": st_stub}):
            from threat_modeler.ui.session import init_session_state
            init_session_state()

        assert st_stub.session_state["role"] == "Reviewer"

    def test_role_default_is_empty_string(self):
        st_stub = _make_st_stub()
        with patch.dict(sys.modules, {"streamlit": st_stub}):
            from threat_modeler.ui.session import init_session_state
            init_session_state()

        assert st_stub.session_state["role"] == ""

    def test_gate_states_default_is_dict(self):
        st_stub = _make_st_stub()
        with patch.dict(sys.modules, {"streamlit": st_stub}):
            from threat_modeler.ui.session import init_session_state
            init_session_state()

        assert isinstance(st_stub.session_state["gate_states"], dict)

    def test_theme_default_is_default(self):
        st_stub = _make_st_stub()
        with patch.dict(sys.modules, {"streamlit": st_stub}):
            from threat_modeler.ui.session import init_session_state
            init_session_state()

        assert st_stub.session_state["theme"] == "Default"


# ---------------------------------------------------------------------------
# Module structure
# ---------------------------------------------------------------------------

class TestModuleStructure:
    def test_ui_package_importable(self):
        import threat_modeler.ui

    def test_session_module_importable(self):
        import threat_modeler.ui.session

    def test_pages_package_importable(self):
        import threat_modeler.ui.screens

    def test_home_page_has_render(self):
        from threat_modeler.ui.screens import home
        assert callable(getattr(home, "render", None))

    def test_role_select_page_has_render(self):
        from threat_modeler.ui.screens import role_select
        assert callable(getattr(role_select, "render", None))

    def test_config_page_has_render(self):
        from threat_modeler.ui.screens import config
        assert callable(getattr(config, "render", None))

    def test_app_module_exists_and_has_set_page_config(self):
        """app.py runs Streamlit at module level — verify structure via AST."""
        import ast
        from pathlib import Path
        app_path = Path("src/threat_modeler/ui/app.py")
        assert app_path.exists(), "app.py not found"
        tree = ast.parse(app_path.read_text(encoding="utf-8"))
        calls = [
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(getattr(node, "func", None), ast.Attribute)
        ]
        assert "set_page_config" in calls, "app.py must call st.set_page_config"
        assert "radio" in calls, "app.py must include navigation radio"


# ---------------------------------------------------------------------------
# Config page — validation logic
# ---------------------------------------------------------------------------

class TestConfigPageDefaults:
    def test_build_default_settings_returns_runtime_settings(self):
        from threat_modeler.config import RuntimeSettings, build_default_settings
        s = build_default_settings()
        assert isinstance(s, RuntimeSettings)

    def test_default_provider_is_fixture(self):
        """Verify default provider is 'fixture' (offline mode)."""
        from threat_modeler.config import build_default_settings
        s = build_default_settings()
        assert s.model.provider == "fixture"
        assert s.model.offline_only is True

    def test_default_all_nine_stages_enabled(self):
        from threat_modeler.config import build_default_settings
        s = build_default_settings()
        assert len(s.pipeline.enabled_stage_ids) == 9

    def test_settings_override_stored_in_session_state(self):
        """Verify RuntimeSettings can be constructed and stored (logic layer only)."""
        from threat_modeler.config import ModelSelection, PipelineSettings, RuntimeSettings
        settings = RuntimeSettings(
            model=ModelSelection(provider="xai", model_name="grok-3-mini", offline_only=False),
            pipeline=PipelineSettings(
                enabled_stage_ids=("agent_01", "agent_02"),
                stop_on_validation_error=True,
                require_hitl_gates=False,
            ),
        )
        fake_state: dict = {}
        fake_state["settings_override"] = settings
        assert isinstance(fake_state["settings_override"], RuntimeSettings)
        assert fake_state["settings_override"].model.provider == "xai"

    def test_provider_matrix_has_required_providers(self):
        """Verify PROVIDER_MATRIX includes all required providers."""
        from threat_modeler.config import PROVIDER_MATRIX
        required_providers = ["fixture", "openai", "anthropic", "xai", "azure", "ollama", "custom"]
        for prov in required_providers:
            assert prov in PROVIDER_MATRIX, f"Provider '{prov}' missing from PROVIDER_MATRIX"

    def test_provider_matrix_entries_complete(self):
        """Verify each provider has required metadata."""
        from threat_modeler.config import PROVIDER_MATRIX
        for prov_key, metadata in PROVIDER_MATRIX.items():
            assert "label" in metadata, f"{prov_key} missing 'label'"
            assert "description" in metadata, f"{prov_key} missing 'description'"
            assert "requires_url" in metadata, f"{prov_key} missing 'requires_url'"
            assert "requires_api_key" in metadata, f"{prov_key} missing 'requires_api_key'"
            assert "default_model" in metadata, f"{prov_key} missing 'default_model'"


# ---------------------------------------------------------------------------
# Role constants
# ---------------------------------------------------------------------------

class TestRoleConstants:
    def test_three_roles_defined(self):
        from threat_modeler.ui.screens.role_select import _ROLES
        assert len(_ROLES) == 3

    def test_all_expected_roles_present(self):
        from threat_modeler.ui.screens.role_select import _ROLES
        assert "Author" in _ROLES
        assert "Reviewer" in _ROLES
        assert "Approver" in _ROLES

    def test_each_role_has_description(self):
        from threat_modeler.ui.screens.role_select import _ROLES, _ROLE_DESCRIPTIONS
        for role in _ROLES:
            assert role in _ROLE_DESCRIPTIONS
            assert len(_ROLE_DESCRIPTIONS[role]) > 10


# ---------------------------------------------------------------------------
# Home page — stage label completeness
# ---------------------------------------------------------------------------

class TestHomeStageCoverage:
    def test_all_nine_stages_have_labels(self):
        from threat_modeler.ui.screens.home import _STAGE_LABELS
        for i in range(1, 10):
            stage_id = f"agent_0{i}"
            assert stage_id in _STAGE_LABELS, f"{stage_id} missing from _STAGE_LABELS"

    def test_status_icons_cover_expected_statuses(self):
        from threat_modeler.ui.screens.home import _STATUS_ICON
        for status in ("pending", "running", "complete", "halted", "awaiting"):
            assert status in _STATUS_ICON


# ---------------------------------------------------------------------------
# Theme module
# ---------------------------------------------------------------------------

class TestTheme:
    def test_theme_module_importable(self):
        import threat_modeler.ui.theme  # noqa: F401

    def test_apply_theme_function_exists(self):
        from threat_modeler.ui.theme import apply_theme
        assert callable(apply_theme)

    def test_dark_css_contains_background(self):
        from threat_modeler.ui.theme import _DARK_CSS
        assert "0e1117" in _DARK_CSS

    def test_dark_css_targets_sidebar(self):
        from threat_modeler.ui.theme import _DARK_CSS
        assert "stSidebar" in _DARK_CSS

    def test_default_css_is_empty(self):
        from threat_modeler.ui.theme import _DEFAULT_CSS
        assert _DEFAULT_CSS == ""

    def test_apply_theme_dark_injects_css(self):
        """apply_theme with theme='Dark' must call st.markdown with a style block."""
        calls = []
        import types
        st_stub = _make_st_stub()
        st_stub.markdown = lambda content, **kw: calls.append(content)
        st_stub.session_state = {"theme": "Dark"}
        import threat_modeler.ui.theme as theme_mod
        with patch.object(theme_mod, "st", st_stub):
            theme_mod.apply_theme()
        assert any("<style>" in c for c in calls), "Dark mode must inject a <style> block"

    def test_apply_theme_default_injects_nothing(self):
        """apply_theme with theme='Default' must not call st.markdown."""
        calls = []
        st_stub = _make_st_stub()
        st_stub.markdown = lambda content, **kw: calls.append(content)
        st_stub.session_state = {"theme": "Default"}
        import threat_modeler.ui.theme as theme_mod
        with patch.object(theme_mod, "st", st_stub):
            theme_mod.apply_theme()
        assert calls == [], "Default theme must not inject any CSS"


# ---------------------------------------------------------------------------
# Input Entry Form — module structure and logic
# ---------------------------------------------------------------------------

class TestInputEntryModuleStructure:
    def test_input_entry_module_importable(self):
        import threat_modeler.ui.screens.input_entry  # noqa: F401

    def test_render_function_exists(self):
        from threat_modeler.ui.screens.input_entry import render
        assert callable(render)

    def test_accepted_extensions_defined(self):
        from threat_modeler.ui.screens.input_entry import _ACCEPTED_EXTENSIONS
        for ext in ("csv", "xlsx", "md", "txt", "yaml", "yml"):
            assert ext in _ACCEPTED_EXTENSIONS

    def test_max_files_is_positive(self):
        from threat_modeler.ui.screens.input_entry import _MAX_FILES
        assert _MAX_FILES > 0


class TestInputEntryParseUploadedFiles:
    """Tests for _parse_uploaded_files without Streamlit running."""

    def _make_uploaded_file(self, name: str, content: bytes) -> MagicMock:
        uf = MagicMock()
        uf.name = name
        uf.size = len(content)
        uf.read.return_value = content
        return uf

    def test_markdown_file_produces_raw_text(self):
        from threat_modeler.ui.screens.input_entry import _parse_uploaded_files
        uf = self._make_uploaded_file("arch.md", b"# MySystem\n\nCore architecture.")
        raw, tables = _parse_uploaded_files([uf])
        assert "MySystem" in raw
        assert tables == []

    def test_txt_file_produces_raw_text(self):
        from threat_modeler.ui.screens.input_entry import _parse_uploaded_files
        uf = self._make_uploaded_file("notes.txt", b"Plain text description.")
        raw, tables = _parse_uploaded_files([uf])
        assert "Plain text description." in raw
        assert tables == []

    def test_csv_file_produces_tables(self):
        from threat_modeler.ui.screens.input_entry import _parse_uploaded_files
        csv_bytes = b"entity_type,id,name\nsubsystem,SS-01,Flight Control\n"
        uf = self._make_uploaded_file("icd.csv", csv_bytes)
        raw, tables = _parse_uploaded_files([uf])
        assert len(tables) == 1
        assert tables[0]["entity_type"] == "subsystem"
        assert raw == ""

    def test_multiple_files_merged(self):
        from threat_modeler.ui.screens.input_entry import _parse_uploaded_files
        md_uf = self._make_uploaded_file("arch.md", b"# System A")
        csv_bytes = b"entity_type,id,name\ncomponent,C-01,Sensor\n"
        csv_uf = self._make_uploaded_file("icd.csv", csv_bytes)
        raw, tables = _parse_uploaded_files([md_uf, csv_uf])
        assert "System A" in raw
        assert len(tables) == 1

    def test_yaml_treated_as_text(self):
        from threat_modeler.ui.screens.input_entry import _parse_uploaded_files
        uf = self._make_uploaded_file("config.yaml", b"system: MySystem\n")
        raw, tables = _parse_uploaded_files([uf])
        assert "MySystem" in raw
        assert tables == []

    def test_empty_list_returns_empty(self):
        from threat_modeler.ui.screens.input_entry import _parse_uploaded_files
        raw, tables = _parse_uploaded_files([])
        assert raw == ""
        assert tables == []


class TestInputEntrySessionKeys:
    """input_entry session keys are registered in session defaults."""

    def _run_init(self, st_stub):
        import threat_modeler.ui.session as session_mod
        with patch.object(session_mod, "st", st_stub):
            session_mod.init_session_state()

    def test_input_system_name_default_in_session(self):
        st_stub = _make_st_stub()
        self._run_init(st_stub)
        assert "input_system_name" in st_stub.session_state

    def test_input_system_description_default_in_session(self):
        st_stub = _make_st_stub()
        self._run_init(st_stub)
        assert "input_system_description" in st_stub.session_state

    def test_input_raw_text_paste_default_in_session(self):
        st_stub = _make_st_stub()
        self._run_init(st_stub)
        assert "input_raw_text_paste" in st_stub.session_state


class TestAppNavIncludesInputEntry:
    def test_input_entry_in_pages_registry(self):
        import ast
        from pathlib import Path
        tree = ast.parse(Path("src/threat_modeler/ui/app.py").read_text(encoding="utf-8"))
        # Look for "Input Entry" string constant in the AST
        strings = [
            node.s if isinstance(node, ast.Constant) and isinstance(node.s, str) else None
            for node in ast.walk(tree)
        ]
        assert "Input Entry" in strings, "app.py _PAGES dict must include 'Input Entry'"


# ---------------------------------------------------------------------------
# S07-03 — Connection validator unit tests
# ---------------------------------------------------------------------------

class TestConnectionValidatorFixtureMode:
    """Fixture and offline-only modes always validate without network I/O."""

    def test_fixture_provider_auto_passes(self):
        from threat_modeler.ui.connection_validator import validate_connection
        from threat_modeler.config import ModelSelection
        model = ModelSelection(provider="fixture", model_name="fixture", offline_only=True)
        result = validate_connection(model)
        assert result.ok is True
        assert "offline" in result.message.lower() or "fixture" in result.message.lower()

    def test_offline_only_flag_auto_passes(self):
        """offline_only=True should bypass network regardless of provider."""
        from threat_modeler.ui.connection_validator import validate_connection
        from threat_modeler.config import ModelSelection
        model = ModelSelection(provider="openai", model_name="gpt-4o", offline_only=True)
        result = validate_connection(model)
        assert result.ok is True

    def test_unknown_provider_fails_gracefully(self):
        from threat_modeler.ui.connection_validator import validate_connection
        from threat_modeler.config import ModelSelection
        model = ModelSelection(provider="nonexistent", model_name="x", offline_only=False)
        result = validate_connection(model)
        assert result.ok is False
        assert "nonexistent" in result.message or "Unknown" in result.message


class TestConnectionValidatorApiKeyCheck:
    """Providers that require_api_key fail fast when no key is supplied."""

    def test_openai_fails_without_api_key(self):
        from threat_modeler.ui.connection_validator import validate_connection
        from threat_modeler.config import ModelSelection
        model = ModelSelection(provider="openai", model_name="gpt-4o", offline_only=False)
        result = validate_connection(model, api_key="")
        assert result.ok is False
        assert "API key" in result.message

    def test_anthropic_fails_without_api_key(self):
        from threat_modeler.ui.connection_validator import validate_connection
        from threat_modeler.config import ModelSelection
        model = ModelSelection(provider="anthropic", model_name="claude-3-5-sonnet", offline_only=False)
        result = validate_connection(model, api_key="")
        assert result.ok is False

    def test_api_key_hint_mentions_env_var(self):
        from threat_modeler.ui.connection_validator import validate_connection
        from threat_modeler.config import ModelSelection
        model = ModelSelection(provider="openai", model_name="gpt-4o", offline_only=False)
        result = validate_connection(model, api_key="")
        assert "OPENAI_API_KEY" in result.detail


class TestConnectionValidatorUrlCheck:
    """Providers that require_url fail fast when URL is blank."""

    def test_ollama_fails_without_url(self):
        from threat_modeler.ui.connection_validator import validate_connection
        from threat_modeler.config import ModelSelection
        model = ModelSelection(provider="ollama", model_name="llama3", offline_only=False, connection_url="")
        result = validate_connection(model, api_key="")
        assert result.ok is False
        assert "URL" in result.message or "url" in result.message.lower()

    def test_custom_fails_without_url(self):
        from threat_modeler.ui.connection_validator import validate_connection
        from threat_modeler.config import ModelSelection
        model = ModelSelection(provider="custom", model_name="my-model", offline_only=False, connection_url="")
        result = validate_connection(model, api_key="")
        assert result.ok is False


class TestConnectionValidatorResult:
    """ValidationResult named-tuple contract."""

    def test_result_has_ok_message_detail(self):
        from threat_modeler.ui.connection_validator import ValidationResult
        r = ValidationResult(ok=True, message="OK")
        assert r.ok is True
        assert r.message == "OK"
        assert r.detail == ""  # default

    def test_failed_result_carries_detail(self):
        from threat_modeler.ui.connection_validator import ValidationResult
        r = ValidationResult(ok=False, message="Failed", detail="some detail")
        assert r.ok is False
        assert r.detail == "some detail"


class TestSessionOfflineOverrideKey:
    """offline_override_active key exists in session defaults."""

    def test_offline_override_active_in_defaults(self):
        st_stub = _make_st_stub()
        import threat_modeler.ui.session as session_mod
        with patch.object(session_mod, "st", st_stub):
            session_mod.init_session_state()
        assert "offline_override_active" in st_stub.session_state
        assert st_stub.session_state["offline_override_active"] is False


# ---------------------------------------------------------------------------
# S07-04 — Prompt store unit tests
# ---------------------------------------------------------------------------

class TestPromptStoreConstants:
    """AGENT_IDS and AGENT_LABELS cover all nine agents."""

    def test_nine_agent_ids(self):
        from threat_modeler.ui.prompt_store import AGENT_IDS
        assert len(AGENT_IDS) == 9

    def test_agent_ids_sequential(self):
        from threat_modeler.ui.prompt_store import AGENT_IDS
        for i, aid in enumerate(AGENT_IDS, start=1):
            assert aid == f"agent_0{i}", f"Expected agent_0{i}, got {aid}"

    def test_labels_cover_all_agents(self):
        from threat_modeler.ui.prompt_store import AGENT_IDS, AGENT_LABELS
        for agent_id in AGENT_IDS:
            assert agent_id in AGENT_LABELS, f"{agent_id} missing from AGENT_LABELS"
            assert len(AGENT_LABELS[agent_id]) > 5

    def test_default_prompts_non_empty(self):
        from threat_modeler.ui.prompt_store import AGENT_IDS, get_default_prompt
        for agent_id in AGENT_IDS:
            assert len(get_default_prompt(agent_id)) > 20, f"{agent_id} default prompt too short"


class TestPromptStoreGetSet:
    """get_prompt / set_prompt / get_history round-trip."""

    def _make_st(self):
        return _make_st_stub()

    def test_get_prompt_returns_default_initially(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = self._make_st()
        with patch.object(ps, "st", st_stub):
            default = ps.get_default_prompt("agent_01")
            current = ps.get_prompt("agent_01")
        assert current == default

    def test_set_prompt_updates_current(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = self._make_st()
        with patch.object(ps, "st", st_stub):
            ps.set_prompt("agent_01", "New prompt text", actor="Author")
            assert ps.get_prompt("agent_01") == "New prompt text"

    def test_set_prompt_appends_history(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = self._make_st()
        with patch.object(ps, "st", st_stub):
            ps.set_prompt("agent_01", "Version 2 text", actor="Author")
            history = ps.get_history("agent_01")
        # Seed v1 (default) + v2 (just saved)
        assert len(history) == 2
        assert history[-1].text == "Version 2 text"
        assert history[-1].actor == "Author"
        assert history[-1].version == 2

    def test_history_version_numbers_increment(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = self._make_st()
        with patch.object(ps, "st", st_stub):
            ps.set_prompt("agent_02", "A", actor="Author")
            ps.set_prompt("agent_02", "B", actor="Author")
            history = ps.get_history("agent_02")
        versions = [e.version for e in history]
        assert versions == list(range(1, len(versions) + 1))

    def test_unknown_agent_raises_key_error(self):
        import pytest
        import threat_modeler.ui.prompt_store as ps
        st_stub = self._make_st()
        with patch.object(ps, "st", st_stub):
            with pytest.raises(KeyError):
                ps.get_prompt("agent_99")


class TestPromptStoreRevert:
    """revert_to restores a prior version and records a new entry."""

    def test_revert_restores_text(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            original = ps.get_prompt("agent_03")
            ps.set_prompt("agent_03", "Changed text", actor="Author")
            ps.revert_to("agent_03", 0, actor="Author")  # index 0 = initial default
            assert ps.get_prompt("agent_03") == original

    def test_revert_creates_new_history_entry(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            ps.set_prompt("agent_03", "Changed", actor="Author")
            before_len = len(ps.get_history("agent_03"))
            ps.revert_to("agent_03", 0, actor="Author")
            after_len = len(ps.get_history("agent_03"))
        assert after_len == before_len + 1

    def test_revert_out_of_range_raises(self):
        import pytest
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            with pytest.raises(IndexError):
                ps.revert_to("agent_03", 999, actor="Author")


class TestPromptStoreTemperature:
    """get_temperature / set_temperature round-trip and validation."""

    def test_default_temperature_is_0_2(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            assert ps.get_temperature("agent_01") == 0.2

    def test_set_temperature_persists(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            ps.set_temperature("agent_01", 0.8)
            assert abs(ps.get_temperature("agent_01") - 0.8) < 0.001

    def test_temperature_out_of_range_raises(self):
        import pytest
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            with pytest.raises(ValueError):
                ps.set_temperature("agent_01", 2.5)

    def test_temperature_boundary_values_accepted(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            ps.set_temperature("agent_01", 0.0)
            assert ps.get_temperature("agent_01") == 0.0
            ps.set_temperature("agent_01", 2.0)
            assert ps.get_temperature("agent_01") == 2.0


class TestPromptStoreIsModified:
    """is_modified returns False for default prompt, True after edit."""

    def test_not_modified_initially(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            assert ps.is_modified("agent_04") is False

    def test_modified_after_set(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            ps.set_prompt("agent_04", "Something different", actor="Author")
            assert ps.is_modified("agent_04") is True

    def test_not_modified_after_reset(self):
        import threat_modeler.ui.prompt_store as ps
        st_stub = _make_st_stub()
        with patch.object(ps, "st", st_stub):
            ps.set_prompt("agent_04", "Something different", actor="Author")
            ps.reset_to_default("agent_04", actor="Author")
            assert ps.is_modified("agent_04") is False


class TestPromptEditorModuleStructure:
    """prompt_editor.py exports a render() function."""

    def test_module_importable(self):
        import threat_modeler.ui.screens.prompt_editor  # noqa: F401

    def test_render_function_exists(self):
        from threat_modeler.ui.screens.prompt_editor import render
        assert callable(render)


class TestAppNavIncludesPromptEditor:
    """app.py _PAGES registry includes 'Prompt Editor'."""

    def test_prompt_editor_in_pages(self):
        import ast
        from pathlib import Path
        tree = ast.parse(Path("src/threat_modeler/ui/app.py").read_text(encoding="utf-8"))
        strings = [
            node.s if isinstance(node, ast.Constant) and isinstance(node.s, str) else None
            for node in ast.walk(tree)
        ]
        assert "Prompt Editor" in strings, "app.py _PAGES must include 'Prompt Editor'"


class TestStageResultsModuleStructure:
    def test_module_importable(self):
        import threat_modeler.ui.screens.stage_results  # noqa: F401

    def test_render_function_exists(self):
        from threat_modeler.ui.screens.stage_results import render
        assert callable(render)


class TestStageResultsHelpers:
    def test_stage_rows_marks_completed_stages(self):
        from threat_modeler.ui.screens.stage_results import _stage_rows

        class _State:
            messages = [
                {"stage_id": "agent_01", "text": "done"},
                {"stage_id": "agent_02", "text": "done"},
            ]

        rows = _stage_rows(_State())
        by_id = {r["Stage ID"]: r["Status"] for r in rows}
        assert by_id["agent_01"] == "Complete"
        assert by_id["agent_02"] == "Complete"
        assert by_id["agent_03"] == "Pending"

    def test_message_rows_flattens_messages(self):
        from threat_modeler.ui.screens.stage_results import _message_rows

        class _State:
            messages = [
                {"stage_id": "agent_01", "text": "first"},
                {"stage_id": "agent_02", "text": "second"},
            ]

        rows = _message_rows(_State())
        assert len(rows) == 2
        assert rows[0]["Stage ID"] == "agent_01"
        assert rows[0]["Message"] == "first"


class TestThreatReviewModuleStructure:
    def test_module_importable(self):
        import threat_modeler.ui.screens.threat_review  # noqa: F401

    def test_render_function_exists(self):
        from threat_modeler.ui.screens.threat_review import render
        assert callable(render)


class TestThreatReviewHelpers:
    def test_extract_threat_rows_empty_without_graph(self):
        from threat_modeler.ui.screens.threat_review import _extract_threat_rows

        class _State:
            canonical_graph = None

        rows = _extract_threat_rows(_State())
        assert rows == []

    def test_extract_threat_rows_from_interface_threats(self):
        from threat_modeler.models.canonical import (
            CanonicalThreatModelGraph,
            Interface,
            Mitigation,
            Threat,
        )
        from threat_modeler.ui.screens.threat_review import _extract_threat_rows

        t = Threat(
            name="Spoofed command",
            description="Attacker injects command",
            likelihood=4,
            impact=5,
            mitigations_technical=[
                Mitigation(control_id="M-1", title="Auth", description="Enable auth")
            ],
            mitigations_administrative=[
                Mitigation(control_id="M-2", title="Policy", description="Operator policy")
            ],
        )
        interface = Interface(
            id="if_cmd",
            name="Command Link",
            description="Ground to flight controller",
            from_node="ground",
            to_node="flight",
            threats=[t],
        )
        graph = CanonicalThreatModelGraph(interfaces=[interface])

        class _State:
            canonical_graph = graph

        rows = _extract_threat_rows(_State())
        assert len(rows) == 1
        row = rows[0]
        assert row["Threat"] == "Spoofed command"
        assert row["Risk Score"] == "20"
        assert row["Tech Mitigations"] == "1"
        assert row["Admin Mitigations"] == "1"


class TestAppNavIncludesS0705Pages:
    def test_stage_results_and_threat_review_in_pages(self):
        import ast
        from pathlib import Path

        tree = ast.parse(Path("src/threat_modeler/ui/app.py").read_text(encoding="utf-8"))
        strings = [
            node.s if isinstance(node, ast.Constant) and isinstance(node.s, str) else None
            for node in ast.walk(tree)
        ]
        assert "Stage Results" in strings
        assert "Threat Review" in strings

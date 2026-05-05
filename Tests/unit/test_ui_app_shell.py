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

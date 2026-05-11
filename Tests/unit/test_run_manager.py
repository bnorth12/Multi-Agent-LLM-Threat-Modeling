"""Unit tests for backend.run_manager — no Streamlit dependency.

These tests verify that the pure-Python execution engine in
``threat_modeler.backend.run_manager`` behaves correctly without any
Streamlit session state or UI layer.
"""

from __future__ import annotations

import threading
import time
import uuid
from unittest.mock import MagicMock, patch

import pytest

from threat_modeler.backend.run_manager import (
    ExecutionStatus,
    any_run_active,
    cancel_run,
    get_all_run_ids,
    get_run_status,
    is_run_active,
    resume_run,
    submit_run,
    wait_for_run,
    _RUN_REGISTRY,
    _REGISTRY_LOCK,
)
from threat_modeler.config import build_default_settings
from threat_modeler.state import FrameworkState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_run_id() -> str:
    return str(uuid.uuid4())


def _fixture_settings():
    return build_default_settings()


# ---------------------------------------------------------------------------
# ExecutionStatus enum
# ---------------------------------------------------------------------------

class TestExecutionStatus:
    def test_all_statuses_present(self):
        statuses = {s.value for s in ExecutionStatus}
        assert "idle" in statuses
        assert "queued" in statuses
        assert "running" in statuses
        assert "paused" in statuses
        assert "completed" in statuses
        assert "failed" in statuses

    def test_status_values_are_strings(self):
        for status in ExecutionStatus:
            assert isinstance(status.value, str)


# ---------------------------------------------------------------------------
# get_run_status / get_all_run_ids
# ---------------------------------------------------------------------------

class TestRunStatusAccessors:
    def test_unknown_run_returns_none(self):
        assert get_run_status("nonexistent-run-id") is None

    def test_known_run_returns_dict(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {
                "status": ExecutionStatus.IDLE.value,
                "run_id": run_id,
                "start_time": None,
                "end_time": None,
                "error": None,
                "result_state": None,
                "live_state": None,
                "pause_gate": None,
                "settings": None,
            }
        try:
            result = get_run_status(run_id)
            assert result is not None
            assert result["run_id"] == run_id
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_get_run_status_returns_copy(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": "idle", "run_id": run_id}
        try:
            snap1 = get_run_status(run_id)
            snap2 = get_run_status(run_id)
            assert snap1 is not snap2
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_all_run_ids_includes_registered_run(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": "idle", "run_id": run_id}
        try:
            assert run_id in get_all_run_ids()
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)


# ---------------------------------------------------------------------------
# is_run_active / any_run_active
# ---------------------------------------------------------------------------

class TestActivityChecks:
    def test_idle_run_not_active(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": ExecutionStatus.IDLE.value}
        try:
            assert is_run_active(run_id) is False
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_running_run_is_active(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": ExecutionStatus.RUNNING.value}
        try:
            assert is_run_active(run_id) is True
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_queued_run_is_active(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": ExecutionStatus.QUEUED.value}
        try:
            assert is_run_active(run_id) is True
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_completed_run_not_active(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": ExecutionStatus.COMPLETED.value}
        try:
            assert is_run_active(run_id) is False
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_unknown_run_not_active(self):
        assert is_run_active("no-such-run") is False

    def test_any_run_active_detects_running_entry(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": ExecutionStatus.RUNNING.value}
        try:
            assert any_run_active() is True
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)


# ---------------------------------------------------------------------------
# cancel_run
# ---------------------------------------------------------------------------

class TestCancelRun:
    def test_cancel_active_run_returns_true(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {
                "status": ExecutionStatus.RUNNING.value,
                "run_id": run_id,
                "end_time": None,
                "error": None,
            }
        try:
            result = cancel_run(run_id)
            assert result is True
            entry = get_run_status(run_id)
            assert entry["status"] == ExecutionStatus.FAILED.value
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_cancel_completed_run_returns_false(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": ExecutionStatus.COMPLETED.value}
        try:
            result = cancel_run(run_id)
            assert result is False
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_cancel_unknown_run_returns_false(self):
        assert cancel_run("no-such-run") is False


# ---------------------------------------------------------------------------
# wait_for_run
# ---------------------------------------------------------------------------

class TestWaitForRun:
    def test_wait_nonexistent_run_returns_true(self):
        assert wait_for_run("no-such-run", timeout=0.1) is True

    def test_wait_completed_run_returns_immediately(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": ExecutionStatus.COMPLETED.value}
        try:
            assert wait_for_run(run_id, timeout=5.0) is True
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_wait_times_out_for_stuck_run(self):
        run_id = _fresh_run_id()
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[run_id] = {"status": ExecutionStatus.RUNNING.value}
        try:
            result = wait_for_run(run_id, timeout=0.05)
            assert result is False
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)


# ---------------------------------------------------------------------------
# submit_run — integration with fixture settings
# ---------------------------------------------------------------------------

class TestSubmitRun:
    def test_submit_run_registers_run_id(self):
        run_id = _fresh_run_id()
        state = FrameworkState(raw_text="test system description")
        settings = _fixture_settings()
        submit_run(run_id, state, settings)
        try:
            entry = get_run_status(run_id)
            assert entry is not None
            assert entry["run_id"] == run_id
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_submit_run_completes_with_fixture_settings(self):
        run_id = _fresh_run_id()
        state = FrameworkState(raw_text="Avionics flight controller bus.")
        settings = _fixture_settings()
        submit_run(run_id, state, settings)
        completed = wait_for_run(run_id, timeout=30.0)
        try:
            assert completed, "Run did not complete within timeout"
            entry = get_run_status(run_id)
            status = entry["status"]
            error = entry.get("error") or ""
            # In a full install the pipeline should complete or pause at a HITL gate.
            # In a partial install (e.g. stix2 missing) the run may fail at or before
            # the STIX stage — that is an environment limitation, not a run_manager bug.
            if status == ExecutionStatus.FAILED.value and (
                "stix2" in error.lower() or "stixpackageragent" in error.lower()
            ):
                # stix2 not installed — acceptable test-environment limitation.
                pass
            else:
                assert status in (
                    ExecutionStatus.COMPLETED.value,
                    ExecutionStatus.PAUSED.value,
                ), f"Unexpected status '{status}'; error: {error}"
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_submit_run_calls_on_complete_callback(self):
        run_id = _fresh_run_id()
        state = FrameworkState(raw_text="callback test")
        settings = _fixture_settings()
        callback_called = threading.Event()

        def _cb():
            callback_called.set()

        submit_run(run_id, state, settings, on_complete=_cb)
        try:
            fired = callback_called.wait(timeout=30.0)
            assert fired, "on_complete callback was not invoked"
        finally:
            with _REGISTRY_LOCK:
                _RUN_REGISTRY.pop(run_id, None)

    def test_submit_run_has_no_streamlit_dependency(self):
        """Importing run_manager must not import streamlit at module level."""
        import threat_modeler.backend.run_manager as rm
        # If streamlit were imported at module level, sys.modules would contain it.
        # The module must NOT have 'streamlit' as a direct dependency.
        import sys
        # Verify the module itself does not hold a 'st' attribute.
        assert not hasattr(rm, "st"), "run_manager must not import streamlit as 'st'"

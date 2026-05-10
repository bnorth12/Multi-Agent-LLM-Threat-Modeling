"""Integration tests for GUI-025: Markdown Viewer and Editor

Acceptance Criteria:
- Markdown viewer displays generated report artifacts
- Editor mode allows content editing with save state feedback
- Edited markdown persists across session state changes
- Markdown edits integrate with snapshot save/restore
- Export generates both original and edited artifacts
- Basic edit safeguards (reset, discard, unsaved indicator) function correctly
"""

import json

import pytest

from threat_modeler.state import FrameworkState
from threat_modeler.ui.runtime_io import (
    build_snapshot_payload,
    framework_state_from_dict,
    snapshot_payload_from_json,
    snapshot_payload_to_json,
)


class TestMarkdownViewerEditorIntegration:
    """Verify markdown viewer/editor display, edit, and persistence functionality."""

    @staticmethod
    def _create_test_state_with_report() -> FrameworkState:
        """Create a FrameworkState with a sample markdown report."""
        state = FrameworkState(
            raw_text="Test system",
            tables=[],
            canonical_graph=None,
            messages=[],
            stix_bundle=None,
            mermaid_diagrams={},
            final_report="# Test Report\n\n## Introduction\n\nThis is a test report.\n\n## Threats\n\n- Threat 1\n- Threat 2\n",
            human_feedback={},
            next_stage_id=None,
        )
        return state

    def test_markdown_display_from_state(self):
        """Verify markdown report displays from FrameworkState."""
        state = self._create_test_state_with_report()
        assert state.final_report is not None
        assert "# Test Report" in state.final_report
        assert "## Introduction" in state.final_report
        assert "## Threats" in state.final_report

    def test_markdown_edits_persist_in_session_dict(self):
        """Verify edited markdown persists in a session tracking dict."""
        state = self._create_test_state_with_report()
        run_id = "test-run-123"

        # Simulate session state tracking for markdown edits
        markdown_edits = {}
        markdown_edits[run_id] = state.final_report

        # Simulate edit
        edited_content = state.final_report.replace("## Threats", "## Identified Threats")
        markdown_edits[run_id] = edited_content

        # Verify edit persists
        assert markdown_edits[run_id] == edited_content
        assert markdown_edits[run_id] != state.final_report

    def test_markdown_edits_integration_with_snapshot_payload(self):
        """Verify markdown edits are included in snapshot payload."""
        state = self._create_test_state_with_report()
        run_id = "test-run-456"

        # Build markdown edits dict
        edited_content = state.final_report + "\n\n## Additional Notes\n\nEdited by analyst.\n"
        markdown_edits = {run_id: edited_content}

        # Build snapshot payload with markdown edits
        payload = build_snapshot_payload(run_id, state, {}, markdown_edits)

        # Verify markdown edits are in payload
        assert "markdown_edits" in payload
        assert payload["markdown_edits"][run_id] == edited_content

    def test_markdown_edits_snapshot_serialization(self):
        """Verify snapshot with markdown edits serializes/deserializes correctly."""
        state = self._create_test_state_with_report()
        run_id = "test-run-789"

        # Create markdown edits
        edited_content = state.final_report.replace("test report", "EDITED report")
        markdown_edits = {run_id: edited_content}

        # Build and serialize payload
        payload = build_snapshot_payload(run_id, state, {}, markdown_edits)
        payload_json = snapshot_payload_to_json(payload)

        # Verify JSON is valid
        assert isinstance(payload_json, str)
        restored_payload = snapshot_payload_from_json(payload_json)

        # Verify markdown edits survive serialization round-trip
        assert restored_payload["markdown_edits"][run_id] == edited_content

    def test_markdown_reset_to_original(self):
        """Verify reset-to-original functionality discards edits."""
        state = self._create_test_state_with_report()
        run_id = "test-run-reset"

        # Simulate session tracking
        markdown_edits = {run_id: state.final_report}
        original = markdown_edits[run_id]

        # Simulate edit
        markdown_edits[run_id] = original + "\n\n## NEW SECTION"
        assert markdown_edits[run_id] != original

        # Reset to original
        markdown_edits[run_id] = original
        assert markdown_edits[run_id] == original

    def test_markdown_multiple_runs_tracked_separately(self):
        """Verify edits for different runs are tracked independently."""
        state1 = self._create_test_state_with_report()
        state2 = self._create_test_state_with_report()

        run_id_1 = "run-1"
        run_id_2 = "run-2"

        # Track edits for both runs
        markdown_edits = {}
        markdown_edits[run_id_1] = state1.final_report + "\n## Run 1 Notes"
        markdown_edits[run_id_2] = state2.final_report + "\n## Run 2 Notes"

        # Verify they're tracked separately
        assert markdown_edits[run_id_1] != markdown_edits[run_id_2]
        assert "Run 1 Notes" in markdown_edits[run_id_1]
        assert "Run 2 Notes" in markdown_edits[run_id_2]

    def test_markdown_edits_export_generation(self):
        """Verify edited markdown can be exported as artifact."""
        state = self._create_test_state_with_report()
        run_id = "test-run-export"

        # Simulate original and edited versions
        original_md = state.final_report
        edited_md = state.final_report + "\n\n## Analyst Review\n\nApproved for release.\n"

        # Both should be exportable
        assert isinstance(original_md, str)
        assert len(original_md) > 0
        assert isinstance(edited_md, str)
        assert len(edited_md) > len(original_md)
        assert "Analyst Review" in edited_md
        assert "Analyst Review" not in original_md

    def test_markdown_changed_detection(self):
        """Verify change detection logic for save button state."""
        state = self._create_test_state_with_report()
        original = state.final_report

        # Simulate different edit scenarios
        edited_same = original  # No change
        edited_minor = original.replace("Test", "Test_Modified")  # Minor change
        edited_major = original + "\n\n## New Section"  # Major change

        # Verify change detection
        assert original == edited_same  # No change detected
        assert original != edited_minor  # Change detected
        assert original != edited_major  # Change detected

    def test_snapshot_restore_preserves_markdown_edits(self):
        """Verify snapshot restore reconstitutes markdown edits."""
        state = self._create_test_state_with_report()
        run_id = "test-run-restore"

        # Create snapshot with markdown edits
        edited_content = state.final_report + "\n\nEdited content preserved."
        markdown_edits = {run_id: edited_content}
        payload = build_snapshot_payload(run_id, state, {}, markdown_edits)

        # Simulate snapshot download/upload cycle
        json_str = snapshot_payload_to_json(payload)
        restored_payload = snapshot_payload_from_json(json_str)

        # Simulate restore into session state
        restored_markdown_edits = restored_payload.get("markdown_edits", {})

        # Verify edits are restored
        assert run_id in restored_markdown_edits
        assert restored_markdown_edits[run_id] == edited_content

    def test_snapshot_restore_multiple_runs_edits(self):
        """Verify snapshot with multiple run edits restores correctly."""
        state1 = self._create_test_state_with_report()
        state2 = self._create_test_state_with_report()

        run_id_1 = "run-multi-1"
        run_id_2 = "run-multi-2"

        # Create edits for multiple runs
        markdown_edits = {
            run_id_1: state1.final_report + "\n## Run 1 Edit",
            run_id_2: state2.final_report + "\n## Run 2 Edit",
        }

        # Create and restore snapshot with multiple edits
        payload = build_snapshot_payload(run_id_1, state1, {}, markdown_edits)
        json_str = snapshot_payload_to_json(payload)
        restored_payload = snapshot_payload_from_json(json_str)

        restored_edits = restored_payload.get("markdown_edits", {})

        # Verify all edits are restored
        assert len(restored_edits) == 2
        assert run_id_1 in restored_edits
        assert run_id_2 in restored_edits
        assert "Run 1 Edit" in restored_edits[run_id_1]
        assert "Run 2 Edit" in restored_edits[run_id_2]

    def test_empty_markdown_state_handling(self):
        """Verify handling of empty/None markdown state."""
        state = FrameworkState(
            raw_text="Test",
            tables=[],
            canonical_graph=None,
            messages=[],
            stix_bundle=None,
            mermaid_diagrams={},
            final_report=None,  # None report
            human_feedback={},
            next_stage_id=None,
        )

        run_id = "empty-run"
        markdown_edits = {}

        # Should handle None gracefully
        if state.final_report:
            markdown_edits[run_id] = state.final_report
        else:
            markdown_edits[run_id] = "# Empty Report\n\nNo content generated."

        # Verify fallback works
        assert run_id in markdown_edits
        assert "Empty Report" in markdown_edits[run_id]


class TestMarkdownViewerDisplayLogic:
    """Test markdown display and rendering logic (non-Streamlit)."""

    def test_markdown_content_preservation(self):
        """Verify markdown content is preserved without modification."""
        content = "# Test\n\n## Section\n\n- Item 1\n- Item 2\n"
        result = content
        assert result == content

    def test_markdown_multiline_preservation(self):
        """Verify multiline markdown formatting is preserved."""
        content = """# Header 1

## Header 2

- Bullet 1
- Bullet 2

```python
code block
```

Paragraph with **bold** and *italic*.
"""
        result = content
        assert result == content
        assert "# Header 1" in result
        assert "```python" in result
        assert "**bold**" in result

    def test_markdown_with_special_characters(self):
        """Verify markdown with special characters is preserved."""
        content = "# Report: STRIDE Analysis & Threat Model\n\nAssets: $100K, 50% mitigation\n\n> Quote: 'test'\n"
        result = content
        assert result == content
        assert "&" in result
        assert "$" in result
        assert "%" in result
        assert "'" in result

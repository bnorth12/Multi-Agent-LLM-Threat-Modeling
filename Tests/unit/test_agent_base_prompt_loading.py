"""Unit tests for S11-018: Agent base prompt loading with proper exception handling and logging."""

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

import pytest

from threat_modeler.agents.base import BaseAgent
from threat_modeler.state import FrameworkState


class TestAgentBasePromptLoading(unittest.TestCase):
    """Test suite for agent prompt loading with exception handling and logging."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = BaseAgent(
            display_name="Test Agent",
            stage_id="test_stage_01",
            _prompt_filename="test_prompt.txt",
            _fixture_filename="test_fixture.json",
        )

    def test_load_system_prompt_from_backend_success(self):
        """Test successful prompt load from backend store."""
        with patch("threat_modeler.backend.prompt_store.get_prompt") as mock_get:
            mock_get.return_value = "Backend test prompt"
            result = self.agent._load_system_prompt()
            assert result == "Backend test prompt"
            mock_get.assert_called_once_with("test_stage_01")

    def test_load_system_prompt_import_error_falls_back(self):
        """Test that ImportError falls back to file-based prompt."""
        with patch("threat_modeler.backend.prompt_store.get_prompt") as mock_get, \
             patch.object(self.agent, "_load_system_prompt_from_file") as mock_file:
            mock_get.side_effect = ImportError("Backend module not found")
            mock_file.return_value = "File-based prompt"
            result = self.agent._load_system_prompt()
            assert result == "File-based prompt"
            mock_file.assert_called_once()

    def test_load_system_prompt_key_error_falls_back(self):
        """Test that KeyError falls back to file-based prompt."""
        with patch("threat_modeler.backend.prompt_store.get_prompt") as mock_get, \
             patch.object(self.agent, "_load_system_prompt_from_file") as mock_file:
            mock_get.side_effect = KeyError("Prompt not found")
            mock_file.return_value = "File-based prompt"
            result = self.agent._load_system_prompt()
            assert result == "File-based prompt"
            mock_file.assert_called_once()

    def test_load_system_prompt_unexpected_error_falls_back(self):
        """Test that unexpected exceptions fall back to file-based prompt."""
        with patch("threat_modeler.backend.prompt_store.get_prompt") as mock_get, \
             patch.object(self.agent, "_load_system_prompt_from_file") as mock_file:
            mock_get.side_effect = RuntimeError("Unexpected backend error")
            mock_file.return_value = "File-based prompt"
            result = self.agent._load_system_prompt()
            assert result == "File-based prompt"
            mock_file.assert_called_once()

    def test_load_expected_output_from_backend_success(self):
        """Test successful expected output load from backend store."""
        with patch("threat_modeler.backend.prompt_store.get_expected_output") as mock_get:
            mock_get.return_value = "Expected JSON structure"
            result = self.agent._load_expected_output()
            assert result == "Expected JSON structure"
            mock_get.assert_called_once_with("test_stage_01")

    def test_load_expected_output_import_error_returns_empty(self):
        """Test that ImportError returns empty string for expected output."""
        with patch("threat_modeler.backend.prompt_store.get_expected_output") as mock_get:
            mock_get.side_effect = ImportError("Backend module not found")
            result = self.agent._load_expected_output()
            assert result == ""

    def test_load_expected_output_key_error_returns_empty(self):
        """Test that KeyError returns empty string for expected output."""
        with patch("threat_modeler.backend.prompt_store.get_expected_output") as mock_get:
            mock_get.side_effect = KeyError("Expected output not found")
            result = self.agent._load_expected_output()
            assert result == ""

    def test_load_expected_output_unexpected_error_returns_empty(self):
        """Test that unexpected exceptions return empty string for expected output."""
        with patch("threat_modeler.backend.prompt_store.get_expected_output") as mock_get:
            mock_get.side_effect = RuntimeError("Unexpected backend error")
            result = self.agent._load_expected_output()
            assert result == ""

    def test_compose_system_prompt_with_expected_output(self):
        """Test compose_system_prompt includes expected output example."""
        system_prompt = "You are a test agent."
        expected_output = '{"result": "example"}'
        result = self.agent._compose_system_prompt(system_prompt, expected_output)
        assert "Expected output example" in result
        assert expected_output in result
        assert "--- EXPECTED_OUTPUT_EXAMPLE_START ---" in result
        assert "--- EXPECTED_OUTPUT_EXAMPLE_END ---" in result

    def test_compose_system_prompt_without_expected_output(self):
        """Test compose_system_prompt returns plain prompt when no expected output."""
        system_prompt = "You are a test agent."
        expected_output = ""
        result = self.agent._compose_system_prompt(system_prompt, expected_output)
        assert result == system_prompt

    def test_compose_system_prompt_with_whitespace_only_expected_output(self):
        """Test compose_system_prompt treats whitespace-only as empty expected output."""
        system_prompt = "You are a test agent."
        expected_output = "   \n\t  "
        result = self.agent._compose_system_prompt(system_prompt, expected_output)
        assert result == system_prompt


if __name__ == "__main__":
    unittest.main()

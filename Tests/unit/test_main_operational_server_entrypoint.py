"""Tests for operational CLI entry point."""

from __future__ import annotations

from unittest.mock import patch


def test_main_uses_operational_server_defaults():
    from threat_modeler import __main__

    with patch("threat_modeler.__main__.start_server") as start_mock, patch(
        "sys.argv", ["threat_modeler"]
    ):
        __main__.main()

    start_mock.assert_called_once_with(host="127.0.0.1", port=8600)


def test_main_uses_custom_host_and_port():
    from threat_modeler import __main__

    with patch("threat_modeler.__main__.start_server") as start_mock, patch(
        "sys.argv", ["threat_modeler", "--host", "0.0.0.0", "--port", "9001"]
    ):
        __main__.main()

    start_mock.assert_called_once_with(host="0.0.0.0", port=9001)

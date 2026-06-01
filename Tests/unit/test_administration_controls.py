from pathlib import Path

from scripts.verify_administration_controls import evaluate_controls


def test_administration_controls_are_present() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    missing = evaluate_controls(repo_root)
    assert missing == {}

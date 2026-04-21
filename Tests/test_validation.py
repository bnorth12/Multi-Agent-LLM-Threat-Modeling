from pathlib import Path
import sys


def _add_src_to_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def test_placeholder_graph_passes_schema_validation() -> None:
    _add_src_to_path()

    from threat_modeler.models import build_placeholder_graph
    from threat_modeler.validation import CanonicalGraphValidator

    validator = CanonicalGraphValidator()
    result = validator.validate_graph(build_placeholder_graph())

    assert result.is_valid is True
    assert result.issues == []


def test_missing_required_field_fails_schema_validation() -> None:
    _add_src_to_path()

    from threat_modeler.models import build_placeholder_graph
    from threat_modeler.validation import CanonicalGraphValidator

    graph_payload = build_placeholder_graph().to_dict()
    del graph_payload["system"]["name"]

    validator = CanonicalGraphValidator()
    result = validator.validate_graph(graph_payload)

    assert result.is_valid is False
    assert result.issues[0].code == "SCHEMA_REQUIRED"
    assert result.issues[0].location == "system"


def test_additional_metadata_field_fails_schema_validation() -> None:
    _add_src_to_path()

    from threat_modeler.models import build_placeholder_graph
    from threat_modeler.validation import CanonicalGraphValidator

    graph_payload = build_placeholder_graph().to_dict()
    graph_payload["metadata"]["status"] = "extra"

    validator = CanonicalGraphValidator()
    result = validator.validate_graph(graph_payload)

    assert result.is_valid is False
    assert result.issues[0].code == "SCHEMA_ADDITIONALPROPERTIES"
    assert result.issues[0].location == "metadata"
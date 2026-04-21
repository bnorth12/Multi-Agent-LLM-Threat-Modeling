import json
from pathlib import Path
import sys


def _ensure_src_on_path() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    return repo_root


def _load_validator(repo_root: Path):
    from jsonschema import Draft202012Validator

    schema_path = repo_root / "docs" / "schemas" / "canonical_graph.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def test_parser_output_from_text_is_schema_aligned() -> None:
    repo_root = _ensure_src_on_path()

    from threat_modeler.parsing import ParserInput, ParserInterface

    validator = _load_validator(repo_root)
    parser = ParserInterface()

    graph = parser.normalize(
        ParserInput(
            raw_text="Command Processor\nFlow: from=client; to=gateway; protocol=https; data_items=token,request",
            tables=[],
        )
    )

    issues = list(validator.iter_errors(graph.to_dict()))
    assert issues == []


def test_parser_output_from_structured_tables_is_schema_aligned() -> None:
    repo_root = _ensure_src_on_path()

    from threat_modeler.parsing import ParserInput, ParserInterface

    validator = _load_validator(repo_root)
    parser = ParserInterface()

    graph = parser.normalize(
        ParserInput(
            raw_text="Avionics Node",
            tables=[
                {
                    "schema": "subsystems",
                    "rows": [
                        {
                            "subsystem": "Control Plane",
                            "subsystem_id": "subsystem_control_plane",
                            "description": "Control and policy processing",
                        }
                    ],
                },
                {
                    "schema": "components",
                    "rows": [
                        {
                            "component": "Policy Engine",
                            "component_id": "component_policy_engine",
                            "parent_subsystem": "subsystem_control_plane",
                            "hardware": "vm",
                            "software_modules": ["policy", "rules"],
                            "description": "Policy evaluation",
                        }
                    ],
                },
                {
                    "schema": "flows",
                    "rows": [
                        {
                            "from_node": "component_policy_engine",
                            "to_node": "component_command_dispatch",
                            "protocol": "grpc",
                            "data_items": ["policy_decision"],
                            "trust_boundary_name": "control_network",
                        }
                    ],
                },
            ],
        )
    )

    issues = list(validator.iter_errors(graph.to_dict()))
    assert issues == []

from pathlib import Path
import sys


def _ensure_src_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def test_parser_normalize_raw_text_only_builds_typed_graph() -> None:
    _ensure_src_on_path()

    from threat_modeler.parsing import ParserInput, ParserInterface

    parser = ParserInterface()
    graph = parser.normalize(
        ParserInput(
            raw_text="Vehicle Gateway\nHandles command routing\nECU_A -> ECU_B:CAN",
            tables=[],
        )
    )

    assert graph.system.name == "Vehicle Gateway"
    assert graph.metadata.model_level == "system"
    assert len(graph.components) >= 1
    assert len(graph.data_flows) >= 1
    assert graph.data_flows[0].id.startswith("df_")


def test_parser_normalize_table_rows_maps_component_and_flow() -> None:
    _ensure_src_on_path()

    from threat_modeler.parsing import ParserInput, ParserInterface

    parser = ParserInterface()
    graph = parser.normalize(
        ParserInput(
            raw_text="Control Plane",
            tables=[
                {
                    "component": "Gateway Service",
                    "parent_subsystem": "subsystem_core",
                    "hardware": "vm",
                    "software_modules": "router,auth",
                    "description": "Ingress handler",
                },
                {
                    "from_node": "gateway_service",
                    "to_node": "policy_engine",
                    "protocol": "https",
                    "data_items": "jwt,request",
                },
            ],
        )
    )

    component_names = [component.name for component in graph.components]
    assert "Gateway Service" in component_names

    table_flow = next(flow for flow in graph.data_flows if flow.from_node == "gateway_service")
    assert table_flow.to_node == "policy_engine"
    assert table_flow.protocol == "https"
    assert table_flow.data_items == ["jwt", "request"]


def test_agent01_populates_graph_from_state_input() -> None:
    _ensure_src_on_path()

    from threat_modeler.agents.agent_01_input_normalizer import Agent01InputNormalizer
    from threat_modeler.state import FrameworkState

    agent = Agent01InputNormalizer()
    state = FrameworkState(raw_text="Safety Controller\nHandles decisions", tables=[])

    agent.run(state)

    assert state.canonical_graph is not None
    assert state.canonical_graph.system.name == "Safety Controller"


def test_parser_extracts_subsystems_from_structured_table_schema() -> None:
    _ensure_src_on_path()

    from threat_modeler.parsing import ParserInput, ParserInterface

    parser = ParserInterface()
    graph = parser.normalize(
        ParserInput(
            raw_text="Mission Platform",
            tables=[
                {
                    "schema": "subsystems",
                    "rows": [
                        {
                            "subsystem": "Guidance",
                            "subsystem_id": "subsystem_guidance",
                            "description": "Trajectory and control decisions",
                        }
                    ],
                }
            ],
        )
    )

    assert len(graph.subsystems) == 1
    assert graph.subsystems[0].id == "subsystem_guidance"
    assert graph.subsystems[0].name == "Guidance"


def test_parser_extracts_richer_flows_from_structured_text_and_table() -> None:
    _ensure_src_on_path()

    from threat_modeler.parsing import ParserInput, ParserInterface

    parser = ParserInterface()
    graph = parser.normalize(
        ParserInput(
            raw_text=(
                "Flight Computer\n"
                "Flow: from=gateway_api; to=policy_engine; protocol=https; data_items=jwt,request; trust_boundary=dmz"
            ),
            tables=[
                {
                    "schema": "flows",
                    "rows": [
                        {
                            "from_node": "policy_engine",
                            "to_node": "command_bus",
                            "protocol": "can",
                            "data_items": ["command"],
                            "trust_boundary_name": "internal_control",
                        }
                    ],
                }
            ],
        )
    )

    text_flow = next(flow for flow in graph.data_flows if flow.from_node == "gateway_api")
    assert text_flow.to_node == "policy_engine"
    assert text_flow.protocol == "https"
    assert text_flow.data_items == ["jwt", "request"]
    assert text_flow.trust_boundary_crossing is True
    assert text_flow.trust_boundary_name == "dmz"

    table_flow = next(flow for flow in graph.data_flows if flow.from_node == "policy_engine")
    assert table_flow.to_node == "command_bus"
    assert table_flow.protocol == "can"
    assert table_flow.data_items == ["command"]
    assert table_flow.trust_boundary_crossing is True
    assert table_flow.trust_boundary_name == "internal_control"

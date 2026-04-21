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
    assert graph.metadata.status == "parsed"
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

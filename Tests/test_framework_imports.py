from pathlib import Path
import sys


def test_framework_package_imports() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from threat_modeler import FrameworkOrchestrator, build_default_settings

    orchestrator = FrameworkOrchestrator(build_default_settings())
    assert orchestrator.planned_stage_ids() == [
        "agent_01",
        "agent_02",
        "agent_03",
        "agent_04",
        "agent_05",
        "agent_06",
        "agent_07",
        "agent_08",
        "agent_09",
    ]


def test_langgraph_compatible_execution_plan() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from threat_modeler import FrameworkOrchestrator, build_default_settings

    settings = build_default_settings()
    orchestrator = FrameworkOrchestrator(settings)
    plan = orchestrator.build_langgraph_execution_plan()

    assert plan.start_node_id == "agent_01"
    assert plan.end_node_id == "agent_09"
    assert len(plan.nodes) == 9
    assert len(plan.edges) == 8


def test_langgraph_compatible_run_populates_typed_graph() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from threat_modeler import FrameworkOrchestrator, build_default_settings

    settings = build_default_settings()
    settings = settings.__class__(
        model=settings.model,
        pipeline=settings.pipeline.__class__(
            execution_mode="langgraph-compatible",
            enabled_stage_ids=settings.pipeline.enabled_stage_ids,
            stop_on_validation_error=settings.pipeline.stop_on_validation_error,
            require_hitl_gates=settings.pipeline.require_hitl_gates,
        ),
    )

    orchestrator = FrameworkOrchestrator(settings)
    state = orchestrator.run_planned_stages()

    assert state.canonical_graph is not None
    assert state.canonical_graph.system.name == "Threat Modeler Placeholder System"
    assert state.messages[0]["stage_id"] == "agent_01"

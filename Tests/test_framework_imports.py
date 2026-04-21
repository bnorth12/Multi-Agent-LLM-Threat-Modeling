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

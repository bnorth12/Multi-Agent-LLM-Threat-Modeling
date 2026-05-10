"""Generate and export full threat model artifacts for documentation."""
import json
from pathlib import Path
from threat_modeler.agents.agent_01_input_normalizer import InputNormalizerAgent
from threat_modeler.agents.agent_02_context_builder import ContextBuilderAgent
from threat_modeler.agents.agent_03_trust_boundary_validator import TrustBoundaryValidatorAgent
from threat_modeler.agents.agent_04_stride_scorer import StrideScorer
from threat_modeler.agents.agent_05_threat_generator import ThreatGeneratorAgent
from threat_modeler.agents.agent_06_stix_packager import StixPackagerAgent
from threat_modeler.agents.agent_07_mitigation_generator import MitigationGeneratorAgent
from threat_modeler.agents.agent_08_diagram_generator import DiagramGeneratorAgent
from threat_modeler.agents.agent_09_report_writer import ReportWriterAgent
from threat_modeler.config import ModelSelection, PipelineSettings, RuntimeSettings
from threat_modeler.llm.base import FixtureAdapter
from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.state import FrameworkState
from threat_modeler.exports import export_json, export_stix, export_mermaid, export_report

_FIXTURES = Path(__file__).resolve().parent / "Tests" / "fixtures" / "agents"

def _avionics_agents():
    return {
        "agent_01": InputNormalizerAgent(adapter=FixtureAdapter(_FIXTURES / "agent_01_avionics_output.json")),
        "agent_02": ContextBuilderAgent(adapter=FixtureAdapter(_FIXTURES / "agent_02_avionics_output.json")),
        "agent_03": TrustBoundaryValidatorAgent(adapter=FixtureAdapter(_FIXTURES / "agent_03_avionics_output.json")),
        "agent_04": StrideScorer(adapter=FixtureAdapter(_FIXTURES / "agent_04_avionics_output.json")),
        "agent_05": ThreatGeneratorAgent(adapter=FixtureAdapter(_FIXTURES / "agent_05_avionics_output.json")),
        "agent_06": StixPackagerAgent(adapter=FixtureAdapter(_FIXTURES / "agent_06_avionics_output.json")),
        "agent_07": MitigationGeneratorAgent(adapter=FixtureAdapter(_FIXTURES / "agent_07_avionics_output.json")),
        "agent_08": DiagramGeneratorAgent(adapter=FixtureAdapter(_FIXTURES / "agent_08_avionics_output.txt")),
        "agent_09": ReportWriterAgent(adapter=FixtureAdapter(_FIXTURES / "agent_09_avionics_output.md")),
    }

settings = RuntimeSettings(
    model=ModelSelection(provider="fixture", model_name="fixture-placeholder", offline_only=True),
    pipeline=PipelineSettings(execution_mode="langgraph-compatible", require_hitl_gates=False)
)

orchestrator = FrameworkOrchestrator(settings=settings, run_id="live-doc-artifacts")
orchestrator.agents = _avionics_agents()
state = FrameworkState(raw_text="Avionics Data Network threat model")
result = orchestrator.run_planned_stages(state)

# Export artifacts
json_export = export_json(result.canonical_graph)
stix_bundle = export_stix(result.canonical_graph)
stix_export = stix_bundle.serialize(pretty=True)
mermaid_export = export_mermaid(result.canonical_graph)
report_export = export_report(result)

# Save to files
export_dir = Path("./exports_for_manual")
export_dir.mkdir(exist_ok=True)

(export_dir / "canonical_graph.json").write_text(json_export)
(export_dir / "threat_model.stix2").write_text(stix_export)
(export_dir / "diagrams.md").write_text(mermaid_export)
(export_dir / "report.md").write_text(report_export)

print(f"✅ Exports generated to {export_dir}:")
print(f"  - canonical_graph.json: {len(json_export)} bytes")
print(f"  - threat_model.stix2: {len(stix_export)} bytes")
print(f"  - diagrams.md: {len(mermaid_export)} bytes")
print(f"  - report.md: {len(report_export)} bytes")

# Validation
print("\n✅ Artifact Validation:")
graph_data = json.loads(json_export)
print(f"  - System: {graph_data.get('system', {}).get('name')}")
print(f"  - Subsystems: {len(graph_data.get('subsystems', []))}")
print(f"  - Components: {len(graph_data.get('components', []))}")
print(f"  - Interfaces: {len(graph_data.get('interfaces', []))}")
print(f"  - Threats: {sum(len(i.get('threats', [])) for i in graph_data.get('interfaces', []))}")

stix_data = json.loads(stix_export)
print(f"  - STIX Bundle: {stix_data.get('type')} with {len(stix_data.get('objects', []))} objects")

print(f"  - Mermaid diagrams: {mermaid_export.count('graph')}")
print(f"  - Report sections: {report_export.count('##')}")

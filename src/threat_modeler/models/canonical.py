"""
Stub CanonicalThreatModelGraph for orchestrator and state compatibility.
"""
class CanonicalThreatModelGraph:
    def to_dict(self):
        return {}
"""Typed canonical graph models for the framework skeleton."""

from dataclasses import asdict, dataclass, field


@dataclass
class GraphMetadata:
    generation_timestamp: str = "placeholder"
    model_level: str = "system"


@dataclass
class SystemContext:
    name: str = "Threat Modeler Placeholder System"
    description: str = "Initial framework skeleton canonical graph."
    mission_criticality: str = "undetermined"
    safety_criticality: str = "undetermined"


@dataclass
class Subsystem:
    id: str
    name: str
    description: str
    parent_system: str


@dataclass
class Component:
    id: str
    name: str
    parent_subsystem: str
    hardware: str
    software_modules: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class StrideAssessment:
    S: int = 0
    S_justification: str = "Not scored yet."
    T: int = 0
    T_justification: str = "Not scored yet."
    R: int = 0
    R_justification: str = "Not scored yet."
    I: int = 0
    I_justification: str = "Not scored yet."
    D: int = 0
    D_justification: str = "Not scored yet."
    E: int = 0
    E_justification: str = "Not scored yet."


@dataclass
class Mitigation:
    control_id: str
    title: str
    description: str
    residual_risk_after_control: int = 3


@dataclass
class Threat:
    name: str
    description: str
    mitre_attack_technique: list[str] = field(default_factory=list)
    capec_id: str = ""
    cwe_id: str = ""
    likelihood: int = 1
    impact: int = 1
    mitigations_technical: list[Mitigation] = field(default_factory=list)
    mitigations_administrative: list[Mitigation] = field(default_factory=list)


@dataclass
class DataFlow:
    id: str
    from_node: str
    to_node: str
    protocol: str = "unknown"
    data_items: list[str] = field(default_factory=list)
    trust_boundary_crossing: bool = False
    trust_boundary_name: str = ""
    stride: StrideAssessment = field(default_factory=StrideAssessment)
    threats: list[Threat] = field(default_factory=list)


@dataclass
class CanonicalThreatModelGraph:
    metadata: GraphMetadata = field(default_factory=GraphMetadata)
    system: SystemContext = field(default_factory=SystemContext)
    subsystems: list[Subsystem] = field(default_factory=list)
    components: list[Component] = field(default_factory=list)
    data_flows: list[DataFlow] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def build_placeholder_graph() -> CanonicalThreatModelGraph:
    return CanonicalThreatModelGraph(
        subsystems=[
            Subsystem(
                id="subsystem_core",
                name="Core Threat Modeling Pipeline",
                description="Placeholder subsystem for the staged runtime.",
                parent_system="Threat Modeler Placeholder System",
            )
        ],
        components=[
            Component(
                id="component_orchestrator",
                name="Framework Orchestrator",
                parent_subsystem="subsystem_core",
                hardware="host",
                software_modules=["threat_modeler.orchestrator"],
                description="Coordinates the staged execution skeleton.",
            )
        ],
        data_flows=[
            DataFlow(
                id="df_placeholder_input",
                from_node="user.input",
                to_node="framework.orchestrator",
                protocol="internal",
                data_items=["raw_text", "tables"],
            )
        ],
    )

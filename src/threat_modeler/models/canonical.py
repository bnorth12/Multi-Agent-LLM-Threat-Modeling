"""Typed canonical graph models for the framework skeleton."""

from dataclasses import asdict, dataclass, field


@dataclass
class GraphMetadata:
    generation_timestamp: str = "1970-01-01T00:00:00Z"
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

    @classmethod
    def from_dict(cls, payload: dict) -> "CanonicalThreatModelGraph":
        metadata_payload = payload.get("metadata", {})
        system_payload = payload.get("system", {})

        subsystems = [Subsystem(**item) for item in payload.get("subsystems", [])]
        components = [Component(**item) for item in payload.get("components", [])]

        data_flows: list[DataFlow] = []
        for item in payload.get("data_flows", []):
            stride_payload = item.get("stride", {})
            threats_payload = item.get("threats", [])

            threats: list[Threat] = []
            for threat_payload in threats_payload:
                technical = [Mitigation(**entry) for entry in threat_payload.get("mitigations_technical", [])]
                administrative = [Mitigation(**entry) for entry in threat_payload.get("mitigations_administrative", [])]
                threats.append(
                    Threat(
                        name=threat_payload.get("name", ""),
                        description=threat_payload.get("description", ""),
                        mitre_attack_technique=threat_payload.get("mitre_attack_technique", []),
                        capec_id=threat_payload.get("capec_id", ""),
                        cwe_id=threat_payload.get("cwe_id", ""),
                        likelihood=threat_payload.get("likelihood", 1),
                        impact=threat_payload.get("impact", 1),
                        mitigations_technical=technical,
                        mitigations_administrative=administrative,
                    )
                )

            data_flows.append(
                DataFlow(
                    id=item.get("id", ""),
                    from_node=item.get("from_node", ""),
                    to_node=item.get("to_node", ""),
                    protocol=item.get("protocol", "unknown"),
                    data_items=item.get("data_items", []),
                    trust_boundary_crossing=item.get("trust_boundary_crossing", False),
                    trust_boundary_name=item.get("trust_boundary_name", ""),
                    stride=StrideAssessment(**stride_payload),
                    threats=threats,
                )
            )

        return cls(
            metadata=GraphMetadata(**metadata_payload),
            system=SystemContext(**system_payload),
            subsystems=subsystems,
            components=components,
            data_flows=data_flows,
        )


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

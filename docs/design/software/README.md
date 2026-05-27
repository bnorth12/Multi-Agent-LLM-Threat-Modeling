# Software Design Documents

This folder holds software-level design specifications for application subsystems, services, component contracts, and implementation-constraining design authorities.

These documents are the bridge between architecture intent and code implementation. They should explain the controlling behavior in plain language first and then preserve identifiers for traceability.

Current contents:

| Document | Software authority |
|---|---|
| `Agent_Subsystem_Design_Specification.md` | Stage-by-stage agent responsibilities, mutation boundaries, and output expectations. |
| `Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md` | Canonical-state lifecycle, validation gates, and safe-enrichment rules. |
| `Export_And_Evidence_Packaging_Design_Specification.md` | Export assembly, degraded-output handling, and evidence packaging. |
| `Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md` | Prompt version storage, run-state persistence, checkpointing, and restore behavior. |
| `Runtime_And_Orchestration_Design_Specification.md` | Runtime control-plane sequencing, HITL pause/resume, and closeout behavior. |
| `Model_Configuration_Design_Specification.md` | Provider selection, connection configuration, secure storage, and validation flow. |

Planned additions include:

- HMI behavior detail specifications only where architecture-level GUI authority needs narrower software rules.

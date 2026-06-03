# Parking Lot 2026-99: Skills Layer & Avionics Specialization

**Date**: 2026-06-01
**Status**: Parking Lot Backlog
**Sprint Length**: 2 weeks
**Target End**: 2026-06-15
**Sprint Lead**: [To be assigned]

---

## Executive Summary

Parking Lot 2026-99 preserves a modular "skills" layer concept for the LangGraph agent framework, enabling:

- Domain specialization (threat, governance, reporting, data, workflow, integration, UI/UX)
- Avionics/IOT-specific skills (drawing from secure aerospace design, mixed-criticality, and mitigation architecture)
- Extensibility for future domain-specific skills

This sprint will also explore skills inspired by Lockheed Martin's "Fundamentals of Secure Aerospace Design" and best practices from avionics, IOT, and data center security.

---

## Story Map

The story map is the execution source of truth for the sprint. Strategic objectives summarize intent; stories define the delivery slices and the checklist items below execute them.

| Story ID | Epic | Story Detail | Exit Evidence |
|----------|------|--------------|---------------|
| S13-01 | Skills Foundation | Define the base skill protocol, registry, metadata, and backend adapter boundary. | Skill interface, registry, adapter boundary tests |
| S13-02 | Core Utility Skills | Implement utility-focused skills that can be extracted first with low risk. | Data normalization, reporting helpers, governance helpers |
| S13-03 | Risk Analysis Skills | Split impact, probability, scoping, and risk register logic into explicit skills. | Risk skill tests and HITL review path |
| S13-04 | Avionics Specialization | Implement avionics and domain-boundary skills for mixed-criticality analysis. | Avionics and boundary enforcement tests |
| S13-05 | Mitigation Skills | Add pattern recognition, gap analysis, and mitigation recommendation skills. | Mitigation skill tests and evidence |
| S13-06 | Migration and Compatibility | Migrate hardcoded logic behind adapters without breaking the existing stage contracts. | Compatibility shims, regression tests |
| S13-07 | Governance Rollout | Govern rollout, ownership, and approval gates for skill activation. | Checklist completion, sign-off, and handoff |

---

## Strategic Objectives

1. **Skills Layer Architecture**: Design and implement a modular skills interface and registry for LangGraph agents.
1. **Core Skills Implementation**: Add initial skills for threat intelligence, governance, reporting, data processing, workflow, integration, and UI/UX.
1. **Risk Analysis & Management Skills**: Implement modular skills for:
   - Risk scoping/aggregation (combining impact and probability)
   - Impact analysis (loss modeling, consequence estimation)
   - Probability/likelihood estimation (with HITL support for subjective/uncertain cases)
   - Risk register management and prioritization
   - Integration with threat, mitigation, and governance skills
1. **Avionics/IOT Specialization**: Develop avionics-inspired skills, including:
   - Mixed-criticality data flow analysis
   - Safety/security domain boundary enforcement
   - Ethernet/data center protocol mapping
   - Mitigation architecture skills (e.g., defense-in-depth, partitioning, redundancy)
1. **Mitigation Architecture Skills**: Implement skills for:
   - Mitigation pattern recognition
   - Architecture gap analysis
   - Automated mitigation recommendation
1. **Extensibility & Documentation**: Provide clear interfaces and documentation for adding new skills, including a section for future skills inspired by secure aerospace design literature and loss-based systems engineering.

---

## 0. Scope & Deferrals

### Candidate Scope for Parking Lot 2026-99

- Skills interface and registry design
- Implementation of at least 6 core skills (see above)
- At least 2 avionics/IOT-specific skills
- At least 2 mitigation architecture skills
- Documentation and usage examples
- Backend integration of the skills layer into the LangGraph/orchestrator stack after the GUI/backend split is complete

### Out-of-Scope (Remain Parked Until Explicit Activation)

- Full plugin ecosystem or user-defined skills
- Deep integration with external aerospace/IOT data sources
- Performance optimization of skills engine
- Direct Streamlit/UI integration of the skills framework until after the backend split is complete

---

## 1. Current State Baseline

- LangGraph agents implemented, but skills are implicit or hardcoded
- No modular skills registry or interface
- No avionics/IOT-specific logic encapsulated as skills
- Mitigation logic present but not modularized

---

## 2. Key Deliverables

- `src/skills/` module with base Skill class/protocol
- Skills registry and agent integration
- Core skills: threat intelligence, governance, reporting, data processing, workflow, integration, UI/UX
- **Risk analysis & management skills:**
  - RiskScopingSkill (aggregates impact and probability)
  - ImpactAnalysisSkill (loss/consequence modeling)
  - ProbabilityEstimationSkill (likelihood, with HITL)
  - RiskRegisterSkill (risk tracking/prioritization)
- Avionics/IOT skills: mixed-criticality analysis, domain boundary enforcement
- Mitigation architecture skills: pattern recognition, gap analysis, recommendation
- Planning doc section: "Future Skills from Secure Aerospace Design and Loss-Based Systems Engineering"
- Traceability matrix mapping requirements to skills and tests

---

## 3. Phase-Ordered Sprint Execution

### Phase 1: Skills Layer Design (Days 1-3)

- [ ] **Story S13-01**: Define Skill interface/protocol
- [ ] **Story S13-01**: Implement skills registry
- [ ] **Story S13-06**: Integrate with LangGraph agents

### Phase 2: Core Skills Implementation (Days 4-7)

- [ ] **Story S13-02**: Implement and test core skills
- [ ] **Story S13-02**: Document usage and interfaces

### Phase 3: Avionics/IOT & Mitigation Skills (Days 8-11)

- [ ] **Story S13-04**: Implement avionics/IOT skills
- [ ] **Story S13-05**: Implement mitigation architecture skills
- [ ] **Story S13-04 / S13-05**: Add tests and usage examples

### Phase 4: Documentation & Extensibility (Days 12-13)

- [ ] **Story S13-07**: Write developer guide for adding new skills
- [ ] **Story S13-07**: Add section for future skills (secure aerospace design)

### Phase 5: Sprint Review & Closure (Day 14)

- [ ] **Story S13-07**: Review deliverables
- [ ] **Story S13-07**: Update traceability matrix
- [ ] **Story S13-07**: Sprint closure summary

---

## 4. Traceability Matrix (Initial)

| Req ID | Description | Issue | Status | Skill | Test File | Evidence |
|--------|-------------|-------|--------|-------|-----------|----------|
| S13-001 | Skills interface and registry | D-S13-001 | To Start | Skill base, registry | test_skills_registry.py | src/skills/ |
| S13-002 | Threat intelligence skill | D-S13-002 | To Start | ThreatIntelSkill | test_threat_intel_skill.py | src/skills/threat_intel.py |
| S13-003 | Governance skill | D-S13-003 | To Start | GovernanceSkill | test_governance_skill.py | src/skills/governance.py |
| S13-004 | Reporting skill | D-S13-004 | To Start | ReportWriterSkill | test_report_writer_skill.py | src/skills/report_writer.py |
| S13-005 | Data processing skill | D-S13-005 | To Start | DataNormalizationSkill | test_data_normalization_skill.py | src/skills/data_normalization.py |
| S13-006 | Workflow/orchestration skill | D-S13-006 | To Start | TaskRoutingSkill | test_task_routing_skill.py | src/skills/task_routing.py |
| S13-007 | Risk scoping/aggregation skill | D-S13-007 | To Start | RiskScopingSkill | test_risk_scoping_skill.py | src/skills/risk_scoping.py |
| S13-008 | Impact analysis skill | D-S13-008 | To Start | ImpactAnalysisSkill | test_impact_analysis_skill.py | src/skills/impact_analysis.py |
| S13-009 | Probability/likelihood estimation skill | D-S13-009 | To Start | ProbabilityEstimationSkill | test_probability_estimation_skill.py | src/skills/probability_estimation.py |
| S13-010 | Risk register management skill | D-S13-010 | To Start | RiskRegisterSkill | test_risk_register_skill.py | src/skills/risk_register.py |
| S13-011 | Avionics mixed-criticality skill | D-S13-011 | To Start | MixedCriticalitySkill | test_mixed_criticality_skill.py | src/skills/avionics_mixed_criticality.py |
| S13-012 | Domain boundary enforcement skill | D-S13-012 | To Start | DomainBoundarySkill | test_domain_boundary_skill.py | src/skills/domain_boundary.py |
| S13-013 | Mitigation pattern recognition skill | D-S13-013 | To Start | MitigationPatternSkill | test_mitigation_pattern_skill.py | src/skills/mitigation_pattern.py |
| S13-014 | Mitigation recommendation skill | D-S13-014 | To Start | MitigationRecommendationSkill | test_mitigation_recommendation_skill.py | src/skills/mitigation_recommendation.py |
| S13-015 | Stable skill invocation boundary | D-S13-015 | To Start | Skill adapter/facade boundary | test_skill_invocation_boundary.py | src/skills/ and orchestrator integration |
| S13-016 | State field read/write contract | D-S13-016 | To Start | Skill state contract | test_skill_state_contract.py | framework state integration rules |
| S13-017 | Migration path from hardcoded logic | D-S13-017 | To Start | Migration plan | test_skill_migration_compatibility.py | compatibility shims and regression coverage |
| S13-018 | LangGraph integration of skills | D-S13-018 | To Start | LangGraph skill integration | test_langgraph_skill_integration.py | orchestrator / stage handoff points |
| S13-019 | Canonical artifact merge contract | D-S13-019 | To Start | Output merge contract | test_skill_output_merge.py | canonical graph, mitigation, and report artifacts |
| S13-020 | Skill execution instrumentation | D-S13-020 | To Start | Skill run tracing | test_skill_execution_tracing.py | run metadata and audit evidence |

---

## 6. Technical Requirements for Skills Integration (Draft)

The following technical requirements are to be addressed in this sprint for the skills layer and its integration. These will be refined and moved to the application requirements as the architecture matures.

### 6.1 Skills Framework Requirements

- **REQ-SKILL-001**: The system SHALL provide a base Skill interface or protocol that all skills must implement, supporting initialization, execution, and metadata.
- **REQ-SKILL-002**: The system SHALL provide a skills registry for dynamic discovery, registration, and lookup of available skills.
- **REQ-SKILL-003**: The skills framework SHALL support dependency injection for skills that require access to shared resources (e.g., data stores, config, agent context).
- **REQ-SKILL-004**: The framework SHALL allow skills to declare input/output schemas for validation and integration.
- **REQ-SKILL-005**: The system SHALL provide error handling and logging for skill execution and integration failures.

### 6.2 Skill Definition Requirements

- **REQ-SKILL-101**: Each skill SHALL have a unique identifier, name, and description.
- **REQ-SKILL-102**: Each skill SHALL define its required inputs, outputs, and any preconditions or postconditions.
- **REQ-SKILL-103**: Skills SHOULD be stateless by default, but MAY support stateful operation if required.
- **REQ-SKILL-104**: Skills SHALL provide metadata for documentation and traceability (e.g., version, author, tags).

### 6.3 Skills Integration Requirements

- **REQ-SKILL-201**: The agent framework SHALL support dynamic loading and unloading of skills at runtime.
- **REQ-SKILL-202**: The agent framework SHALL allow skills to be composed into workflows or pipelines.
- **REQ-SKILL-203**: The integration layer SHALL provide mechanisms for skills to communicate or share context when necessary.
- **REQ-SKILL-204**: The system SHALL provide test harnesses and fixtures for validating skill integration and behavior.
- **REQ-SKILL-205**: The agent architecture SHALL expose a stable skill invocation boundary so skills can be inserted without changing unrelated agent logic.
- **REQ-SKILL-206**: The integration layer SHALL define which state fields a skill may read, emit, or mutate.
- **REQ-SKILL-207**: The integration layer SHALL preserve canonical graph and stage contract compatibility when skills are introduced.
- **REQ-SKILL-208**: The integration layer SHALL support adapter or facade patterns where existing agent code must call into the new skills framework.

### 6.4 Extensibility and Governance

- **REQ-SKILL-301**: The skills framework SHALL provide clear extension points and developer documentation for adding new skills.
- **REQ-SKILL-302**: The system SHALL support traceability from requirements to skills and from skills to test evidence.
- **REQ-SKILL-303**: The system SHOULD support HITL (human-in-the-loop) override or review for skills where subjective judgment is required (e.g., risk likelihood estimation).

### 6.5 Migration Path from Hardcoded Logic

- **REQ-SKILL-401**: The sprint SHALL define a migration path from current hardcoded or implicit agent logic into discrete skills.
- **REQ-SKILL-402**: The migration path SHALL identify priority seams for extraction, starting with low-risk utility skills and read-only analysis skills.
- **REQ-SKILL-403**: The migration path SHALL preserve existing stage behavior until the corresponding skill replacement is validated.
- **REQ-SKILL-404**: The migration path SHALL include regression tests or compatibility checks for each extracted skill.
- **REQ-SKILL-405**: The migration path SHALL document any temporary compatibility shims and their removal criteria.

### 6.6 Architecture Integration Requirements

- **REQ-SKILL-501**: The skills framework SHALL integrate with the LangGraph orchestrator and the existing framework state model.
- **REQ-SKILL-502**: The skills framework SHALL support stage-aware execution so skills can be invoked at defined points in the agent pipeline.
- **REQ-SKILL-503**: The skills framework SHALL support traceable handoffs between existing agents and new skills.
- **REQ-SKILL-504**: The skills framework SHALL define how skill outputs are merged into canonical artifacts, including the graph, mitigations, and report artifacts.
- **REQ-SKILL-505**: The skills framework SHALL support instrumentation sufficient to prove which skill produced which output during a run.
- **REQ-SKILL-506**: The skills framework SHALL be implemented against the backend engine boundary only; UI concerns SHALL be isolated until the backend split is complete.
- **REQ-SKILL-507**: Any GUI-facing skill interactions SHALL use backend service or adapter contracts rather than direct Streamlit dependencies.

---

## 7. Execution Details & Rollout

### 7.1 Rollout Checklist

- [ ] Confirm S12 RC1 baseline is complete and stable.
- [ ] Freeze the backend interface contract before skill extraction begins.
- [ ] Implement the base skill protocol and registry.
- [ ] Implement the backend skill adapter boundary and state contract.
- [ ] Extract low-risk utility skills first, starting with data normalization, reporting helpers, and governance helpers.
- [ ] Add tests and fixtures for each extracted skill before enabling the next wave.
- [ ] Add risk-analysis skills after utility skills pass contract and regression checks.
- [ ] Add avionics and mitigation skills after the core contract is stable.
- [ ] Verify skill outputs merge cleanly into canonical graph, mitigation, and report artifacts.
- [ ] Verify instrumentation captures which skill produced which output during a run.

### 7.2 Skill Rollout Waves

- [ ] Wave 1: registry, base protocol, skill metadata, and backend adapter.
- [ ] Wave 2: core utility skills and test harnesses.
- [ ] Wave 3: risk scoping, impact, probability, and register skills.
- [ ] Wave 4: avionics, boundary enforcement, and mitigation skills.

### 7.3 Rollback and Compatibility Checklist

- [ ] Keep existing agent logic as the fallback path until each skill replacement passes regression tests.
- [ ] Document every temporary compatibility shim and isolate it behind backend adapters.
- [ ] If a skill fails validation, keep the legacy path active for that stage.
- [ ] Record the rollback trigger for each skill family before it is enabled by default.

### 7.4 Ownership and Control Points

- [ ] Backend owner: orchestrator/state contract and skill adapter boundary.
- [ ] Skill owners: one owner per skill family, with explicit code and test responsibility.
- [ ] Governance owner: review traceability, HITL handling, and migration sign-off.
- [ ] Approval gate: no skill family advances without test evidence, requirement traceability, and owner sign-off.

---

## 8. Governance & Rollout

### 8.1 Governance Controls

- Each skill SHALL have a lifecycle state: planned, implemented, validated, released, deprecated.
- All skill changes SHALL map to a requirement, a test, and evidence.
- Any likelihood estimate skill SHALL require HITL review when confidence is low or input quality is uncertain.
- Any public API or artifact change SHALL be reviewed for compatibility with the release baseline from S12.

### 8.2 Migration Rollout

- [ ] Freeze the backend interface contract before skill extraction begins.
- [ ] Extract one skill family at a time and validate it in isolation.
- [ ] Keep the legacy stage implementation in place until the new skill is proven equivalent or superior.
- [ ] Record compatibility shim removal criteria before enabling each skill family by default.
- [ ] Promote skills only after traceability and test evidence are complete.

### 8.3 Handoff Criteria

- S12 release baseline remains stable and packaged cleanly.
- Backend/GUI split is complete and not coupled to Streamlit test-only behavior.
- Skill registry, adapter boundary, and initial migration path are approved.

---

## 9. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Skill framework too tightly coupled to old agent logic | Medium | High | Enforce adapter boundary and staged extraction |
| Likelihood estimation is weak or subjective | High | Medium | Require HITL review and confidence metadata |
| Migration breaks canonical graph/state contracts | Medium | High | Add contract tests before swapping each skill |
| Skills introduce release packaging drift | Low | High | Keep S13 aligned to S12 RC1 packaging baseline |
| Integration scope expands beyond sprint capacity | Medium | Medium | Keep rollout in waves and defer nonessential skills |

---

## 10. Sprint Success Metrics

- Base skill protocol and registry are implemented and tested.
- At least one complete skill family is migrated behind the backend adapter.
- Risk analysis skills have explicit HITL support and traceability.
- Canonical artifact merge and stage handoff contracts are validated.
- No GUI coupling is introduced before the backend split is complete.

---

**Document Version**: 1.0
**Last Updated**: 2026-05-18
**Next Review**: 2026-06-03 (Mid-sprint check-in)

# Governance Autoflow Orchestration

## Purpose
Define default, context-driven governance automation so repository process alignment does not depend on a specific individual requesting a specific skill or agent.

## Design Principles
- Local-first and deterministic.
- Policy-profile aware (strict/default/advisory).
- Source-to-evidence traceability centric.
- Explicit phase gating for sprint planning, execution, closeout, and portfolio staging.

## Agent Set
Core orchestrators:
- independent-review-orchestrator
- repo-governance-autoflow-orchestrator

Governance specialists:
- requirements-baseline-steward
- architecture-contract-enforcer
- verification-coverage-planner
- artifact-lineage-auditor
- sprint-intake-gatekeeper
- sprint-execution-compliance-monitor
- sprint-closeout-certifier
- multi-sprint-portfolio-planner
- governance-policy-compiler
- kpi-drift-analyst
- remediation-readiness-strategist
- source-to-evidence-traceability-auditor
- requirements-implementation-auditor
- architecture-design-traceability-auditor

## Skill Set
Existing:
- independent-repo-review
- issue-governance-review
- remediation-readiness
- source-to-evidence-traceability

Scaffolded for extended governance:
- requirements-baseline-steward
- architecture-contract-enforcer
- verification-coverage-planner
- artifact-lineage-auditor
- sprint-intake-gatekeeper
- sprint-execution-compliance-monitor
- sprint-closeout-certifier
- multi-sprint-portfolio-planner
- governance-policy-compiler
- kpi-drift-analyst

## Context Routing Matrix
- planning kickoff:
  - requirements-baseline-steward
  - sprint-intake-gatekeeper
  - governance-policy-compiler
- pre-commit:
  - requirements-baseline-steward
  - architecture-contract-enforcer (scope-filtered)
- pre-merge-commit:
  - architecture-contract-enforcer
  - verification-coverage-planner
  - sprint-execution-compliance-monitor
- pre-push:
  - independent-review-orchestrator
  - source-to-evidence-traceability-auditor
  - kpi-drift-analyst
  - artifact-lineage-auditor
- sprint closeout:
  - sprint-closeout-certifier
  - remediation-readiness-strategist
- portfolio planning:
  - multi-sprint-portfolio-planner
  - kpi-drift-analyst

## Start of Implementation
Implemented in this repository iteration:
- One-time KPI backfill utility and over-time trend report generation.
- Extended governance agent and skill scaffolding under .github/agents and .github/skills.
- Documentation updates for default governance autoflow behavior.

Remaining implementation steps:
1. Add execution wrapper script to invoke route-specific agent/skill bundles by context.
2. Connect wrapper script into git hooks and planning/closeout operator commands.
3. Add policy-compiled route overrides by branch and run context.
4. Add CI informational checks for governance metadata completeness without replacing local-first gates.

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
- architecture-design-traceability-auditor
- requirements-implementation-auditor
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
- architecture-design-traceability-auditor
- requirements-implementation-auditor
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
  - architecture-design-traceability-auditor
  - sprint-intake-gatekeeper
  - governance-policy-compiler
- pre-commit:
  - requirements-baseline-steward
  - architecture-contract-enforcer (scope-filtered)
- pre-merge-commit:
  - architecture-contract-enforcer
  - architecture-design-traceability-auditor
  - requirements-implementation-auditor
  - verification-coverage-planner
  - sprint-execution-compliance-monitor
- pre-push:
  - independent-review-orchestrator
  - architecture-design-traceability-auditor
  - requirements-implementation-auditor
  - source-to-evidence-traceability-auditor
  - kpi-drift-analyst
  - artifact-lineage-auditor
- sprint closeout:
  - sprint-closeout-certifier
  - remediation-readiness-strategist
- portfolio planning:
  - multi-sprint-portfolio-planner
  - kpi-drift-analyst

## Routing Map

- Data-configured routing map: `config/governance_autoflow_routing.json`
- `scripts/governance_autoflow.py` reads this file for:
  - branch/profile selection behavior
  - run-context mapping
  - enforcement mode
  - declared agent and skill chains by context

The dispatcher currently resolves several stages to concrete local commands and runs them once per unique command key:

- independent review -> `scripts/independent_repo_review.py`
- requirements baseline / architecture-design / implementation-coverage stages -> `scripts/independent_repo_review.py`
- traceability baseline / audit / closure stages -> `scripts/verify_sprint_traceability.py`
- architecture contract enforcement -> `scripts/verify_dependency_boundary.py`
- artifact lineage enforcement -> `scripts/archive_hygiene.py`
- governance policy compilation -> `scripts/validate_cross_domain_exception_policy.py`
- KPI drift analysis -> `scripts/run_kpi_drift_analysis.py`
- sprint closeout certification -> `scripts/run_sprint_closeout_certification.py`
- remediation readiness -> `scripts/run_remediation_readiness.py`
- multi-sprint portfolio planning -> `scripts/run_multi_sprint_portfolio_planning.py`

Remediation readiness is advisory only: it records the current health score, remediation floor, theme-based intake guidance, and suggested next actions, but it does not itself block merge or closeout.
It also writes a separate legacy findings backlog artifact so older issues can be carried forward into remediation sprints without reintroducing them as hard gates.

## Execution Ledger

Governance autoflow writes auditable ledger artifacts on every run:

- `local_reviews/latest/governance_execution_ledger_latest.json`
- `local_reviews/latest/governance_execution_ledger_latest.md`
- `local_reviews/history/governance_execution_ledger.jsonl`

Each entry includes context, branch, profile, enforcement mode, declared agent chain, declared skill chain, command(s), and outcome.

Each entry now also includes per-stage execution records for both agents and skills with:

- order and stage name
- stage kind (`agent` or `skill`)
- status (`success`, `failed`, or `declared`)
- execution mode (`direct` or `declared-only`)
- started/ended timestamps and duration seconds
- optional `command_ref` linking a stage to the underlying command record
- notes describing whether the stage was directly executed or is still scaffolded only

This makes the ledger distinguish between:

- stages that actually ran in the current orchestration path
- stages that are declared in the route but not yet individually invoked
- the shared command payload and exit code that produced a direct stage result
- the shared stage labels that show which agent and skill names were covered by each command

## Hook and Operator Wiring

Git hooks call governance autoflow directly:

- `.githooks/pre-commit` -> `--context pre-commit`
- `.githooks/pre-merge-commit` -> `--context pre-merge-commit`
- `.githooks/pre-push` -> `--context pre-push`

Planning and closeout operator commands are provided:

- `scripts/run_governance_planning.ps1`
- `scripts/run_governance_closeout.ps1`
- `scripts/run_governance_planning.sh`
- `scripts/run_governance_closeout.sh`

## Start of Implementation

Implemented in this repository iteration:

- One-time KPI backfill utility and over-time trend report generation.
- Extended governance agent and skill scaffolding under .github/agents and .github/skills.
- Documentation updates for default governance autoflow behavior.
- Multi-stage governance dispatcher in `scripts/governance_autoflow.py`.
- First real command-backed stage invocations for traceability, dependency boundary, artifact hygiene, and policy validation checks.
- Dedicated local runners for KPI drift analysis, sprint closeout certification, and multi-sprint portfolio planning.

Remaining implementation steps:

1. Move stage command selection into the JSON routing map once the command surface stabilizes.
1. Add CI informational checks for governance metadata completeness without replacing local-first gates.

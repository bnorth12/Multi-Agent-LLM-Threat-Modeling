# HITL Framework and Implementation Options

## Purpose

Define implementation options for human-in-the-loop control points so the project can choose governance strength, user experience complexity, and operational cost.

## Option A Minimal Gate Workflow

Summary:

- Manual review at a small number of gates with simple approve or reject actions.

Characteristics:

- lower implementation effort
- lower analyst overhead
- limited edit granularity

Recommended use:

- early internal prototype phase

## Option B Structured Review Workflow

Summary:

- Manual review at all major stages with typed actions and rationale capture.

Characteristics:

- balanced governance and throughput
- explicit approve, reject, edit, and rerun actions
- full audit metadata

Recommended use:

- baseline production workflow for internal programs

## Option C Tiered Governance Workflow

Summary:

- Role-specific review depth with adaptive gating by risk and confidence.

Characteristics:

- strongest governance and traceability
- selective escalation to reviewer and approver roles
- highest implementation complexity

Recommended use:

- high-assurance or externally audited environments

## Implementation Profiles

Profile P1 Local Review Console:

- lightweight internal UI
- optimized for single-team operation

Profile P2 Service-Based API Plus UI:

- backend policy service and dedicated review UI
- supports multi-team and automation integration

Profile P3 Workflow Engine Integration:

- external workflow orchestration integration
- strongest enterprise governance controls

## Recommended Default

Default recommendation:

- Option B with Profile P2

Rationale:

- provides strong auditability with manageable complexity
- supports role-based actions and selective reruns
- compatible with future evolution to Option C

## Required Action Set

All chosen options should support:

- approve
- reject
- edit with rationale
- rerun from selected stage
- defer with comment

## Required Audit Fields

Each HITL decision record should include:

- run_id
- stage_id
- actor_id
- actor_role
- action
- rationale
- timestamp
- artifact_diff_reference

## Integration Points

Expected stage gates:

- after context merge
- after trust boundary validation
- after STRIDE scoring
- after threat generation
- after mitigation generation
- before final release

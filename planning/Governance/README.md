# Repository Governance

**Purpose:** Centralized location for repository-level policies, execution gates, and SDLC standards.

---

## Overview

This directory contains governance artifacts that apply across all sprints and work streams:

- Execution mode definitions (Linear, Branching, Hybrid)
- HITL (Human-in-the-Loop) gate criteria and enforcement
- Code review standards and approval workflows
- Release policies and versioning schemes
- Architectural decisions and standards

---

## Planned Governance Documents

### 1. Execution Mode Policy
**File:** `Execution_Mode_Policy.md` (To be created)

Defines project execution modes:
- **Linear Mode**: Sequential gate progression; no branching until gate completion
- **Branching Mode**: Parallel work streams with merge gates
- **Hybrid Mode**: Mixed parallel/sequential based on gate type

---

### 2. HITL Gate Definitions
**File:** `HITL_Gate_Definitions.md` (To be created)

Human-in-the-loop gate criteria for stage transitions:
- Gate 1: Requirements validation
- Gate 2: Design review and approval
- Gate 3: Test readiness review
- Gate 4: Release readiness
- Gate 5: Production deployment authorization

Each gate includes:
- Entry criteria
- Review checklist
- Approval authority
- Escalation path

---

### 3. Code Review Policy
**File:** `Code_Review_Policy.md` (To be created)

Standards for peer review and approval:
- PR naming conventions
- Review checklist
- Approval requirements (# approvers, specific reviewers)
- Merge conditions
- Blocking conditions (tests, linting, coverage)

---

### 4. Release Policy
**File:** `Release_Policy.md` (To be created)

Versioning and release standards:
- Version numbering scheme (semver, calver, or custom)
- Release branch strategy
- Release notes standards
- Rollback procedures
- Breaking change communication

---

### 5. Architecture Standards
**File:** `Architecture_Standards.md` (To be created)

Technical standards and architectural patterns:
- Code organization principles
- Module dependency rules
- Technology choices and justification
- Testing requirements
- Documentation standards

---

## Current Status

- ✅ Governance directory created (Phase 2)
- ⬜ Policy documents pending creation (Phase 2 follow-up or Phase 4)
- ⬜ Policy review and approval by stakeholders
- ⬜ Integration with CI/CD pipeline for automated enforcement

---

## Implementation Timeline

1. **Phase 2 (Current)**: Create governance directory scaffold
2. **Phase 4**: Draft governance policies and submit for review
3. **Phase 5**: Stakeholder approval and refinement
4. **Phase 6**: Automate enforcement via CI/CD gates

---

## Related Documents

- **Planning Guide**: `planning/README.md` - Overview of planning structure
- **Reorganization Plan**: `planning/00_Repository_Structure_Reorganization_Plan.md` - Phases 1-7 roadmap
- **Requirements**: `planning/Requirements/` - What we're building and why
- **Sprint Details**: `planning/Sprints/` - Active sprint work
- **Governance Automation Backlog**: `planning/Governance/Governance_Automation_Improvement_Backlog.md` - Governance debt and policy-automation improvements
- **Application Tech Debt Backlog**: `planning/work_items/Application_Tech_Debt_Backlog.md` - Product/runtime technical debt backlog kept separate from governance automation debt

---

## Getting Started

To review governance policies:

1. Check relevant policy document in this directory
2. Reference policy in code reviews, PRs, and gate decisions
3. Flag policy gaps or conflicts for discussion
4. Contribute policy recommendations via issue or PR

## Feedback & Updates

Governance policies should evolve based on:
- Lessons learned from sprints
- Team feedback and process improvements
- Industry best practices
- Scaling requirements

Submit governance change requests as PRs with rationale and impact analysis.

## Governance Backlog Triage Automation

Use the triage script to append new proposed governance-automation backlog items from the latest remediation obligation report using deterministic IDs.

```bash
# Preview only
python scripts/triage_governance_obligations_backlog.py --dry-run

# Append new items
python scripts/triage_governance_obligations_backlog.py
```

Deterministic ID format:

- `GOV-AUTO-OBL-<8_HEX>` where hash input is `rule_id|level|finding`

The script only appends rows not already present in `planning/Governance/Governance_Automation_Improvement_Backlog.md`.

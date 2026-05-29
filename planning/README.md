# Planning & Governance

Purpose: centralized directory for sprint work, governance policies, issue tracking, and archival evidence.

---

## Directory Structure

```
planning/
├── README.md
├── Governance/
├── issues/
├── Sprints/
├── archives/
├── work_items/
├── Sprint_2026_12_*.md
├── Sprint_2026_13_*.md
└── Sprint_2026_14_*.md
```

---

## Navigation Guide

### For Sprint Teams

- Current and prior sprint planning narratives: `planning/Sprint_2026_12_*.md`, `planning/Sprint_2026_13_*.md`, `planning/Sprint_2026_14_*.md`
- Issue records: `planning/issues/`
- Sprint-scoped folders and work items: `planning/Sprints/`, `planning/work_items/`
- Archived closure evidence: `planning/archives/`

### For Leadership

- Governance policies and process controls: `planning/Governance/`
- Sprint traceability matrices and closure records: `planning/Sprint_*_Traceability_Matrix.md`, `planning/archives/`
- Release artifacts: `Releases/`

### For New Contributors

- Getting started: root README.md and CONTRIBUTING.md
- Governance policies: planning/Governance/
- Active issue and sprint records: planning/issues/ and planning/Sprints/

---

## Sprint Organization

Sprints may be represented as either dedicated subfolders under `Sprints/` or top-level sprint documents in `planning/`.

```
Sprints/Sprint_YYYY_MM/
├── README.md
├── issues/
└── work_items/
```

## Historical Record Policy

- Files under `planning/archives/` and completed sprint folders are historical records.
- Historical records should preserve time-of-execution context rather than being rewritten to present tense.
- Current-state corrections should be made in active indexes and operational docs (root README, docs/, Releases/).

---

## Governance Framework

Repository-level policies and execution gates are managed in `planning/Governance/` and supporting `docs/process/` references.

---

## Requirements & Traceability

See `Requirements/` for:

- **Functional Requirements**: Feature specifications
- **Non-Functional Requirements**: Performance, security, scalability
- **Traceability Matrix**: Maps issues → requirements → test cases
- **Baseline**: Version control of requirements snapshots

---

## New Sprint Setup

To start a new sprint:

1. **Create directory**: `Sprints/Sprint_YYYY_MM/`
1. **Create subdirectories**: `issues/` and `work_items/`
1. **Create README.md**: Use Sprint_Planning_Checklist_Template.md and Sprint_Traceability_Matrix_Template.md
1. **Move issues**: Populate `issues/` with sprint-scoped items
1. **Create work items**: Closeout checklist and execution plan

---

## References

- **Root README**: `README.md` - Project overview and getting started
- **Contributing Guide**: `CONTRIBUTING.md` - Development workflow
- **Test Documentation**: `Tests/README.md` - Test execution and reporting
- **Data Infrastructure**: `data/README.md` - RAG and vector DB patterns
- **Source Code**: `src/` - Application implementation

---

## Key Documents

| Document | Purpose | Location |
|----------|---------|----------|
| Repository Reorganization Plan | Master org plan (Phases 1-7) | `00_Repository_Structure_Reorganization_Plan.md` |
| Audit and Roadmap | Repository audit baseline and recommended follow-on actions | `01_Repository_Audit_And_Phase_3-7_Roadmap.md` |
| Sprint 2026-12 Traceability | Requirement → issue → test mapping for S12 | `Sprint_2026_12_Traceability_Matrix.md` |
| Sprint 2026-12 Closure | S12 closeout and validation records | `Sprint_2026_12_Closure_Checklist.md`, `Sprint_2026_12_Final_Validation_Summary.md` |
| Current issue registry | Cross-sprint issue and implementation tracking | `issues/` |

# Planning & Governance

**Purpose:** Centralized directory for sprint work, governance policies, requirements, and releases.

---

## Directory Structure

```
planning/
├── README.md                                # This file
├── 00_Repository_Structure_Reorganization_Plan.md  # Master org plan
├── 01_Repository_Audit_And_Phase_3-7_Roadmap.md   # Audit & future phases
├── Master_Plan.md                          # [Future] Roadmap across all sprints
├── Sprints/
│   ├── Sprint_2026_11/
│   │   ├── README.md                      # Sprint scope & deliverables
│   │   ├── issues/                        # Sprint issues
│   │   └── work_items/                    # Closeout & execution plans
│   └── Sprint_2026_12/                    # [Future] Next sprint
│
├── Governance/                             # [In Progress] Repo-level policies
│   ├── README.md
│   ├── Execution_Mode_Policy.md            # [Future]
│   ├── HITL_Gate_Definitions.md            # [Future]
│   └── Code_Review_Policy.md               # [Future]
│
├── Requirements/                           # [Existing] System requirements
│   ├── 00_Requirements_Index.md
│   ├── 01_Functional_Requirements.md
│   ├── 02_Non-Functional_Requirements.md
│   ├── 03_Requirements_Baseline_v0.1.md
│   └── 04_Traceability_Matrix.md
│
├── Releases/                               # [Existing] Release artifacts
│   └── Release_v0.1.md
│
├── Templates/                              # [Future] Reusable templates
│   ├── Sprint_Planning_Checklist.md
│   ├── Sprint_Traceability_Matrix.md
│   └── Issue_Template.md
│
└── Archive/                                # [Future] Completed sprints
    ├── Sprint_2026_05/
    └── Sprint_2026_09/
```

---

## Navigation Guide

### For Sprint Teams
- **Active Sprint**: `Sprints/Sprint_2026_11/` → see issues, work items, status
- **Issues**: Each sprint's `issues/` subdirectory with full details
- **Work Items**: Closeout checklists and execution plans in `work_items/`
- **Requirements**: `Requirements/` for traceability and validation
- **Test Evidence**: `Tests/test_reports/` for test run logs and artifacts

### For Leadership
- **Roadmap**: `Master_Plan.md` (across all sprints)
- **Governance**: `Governance/` for policies and gate definitions
- **Releases**: `Releases/` for versioned deliverables
- **Audit**: `01_Repository_Audit_And_Phase_3-7_Roadmap.md` for org improvements

### For New Contributors
- **Getting Started**: Root `README.md` and `CONTRIBUTING.md`
- **Requirements**: `Requirements/` for understanding what we're building
- **Governance**: `Governance/` for SDLC policies and gate criteria
- **Sprint Structure**: `Sprints/Sprint_2026_11/README.md` to understand sprint organization

---

## Sprint Organization

Each sprint has dedicated folder under `Sprints/`:

```
Sprints/Sprint_YYYY_MM/
├── README.md                  # Sprint scope, deliverables, ceremonies
├── issues/
│   └── issue_YYYY_MM_*.md    # Individual issue details & acceptance criteria
└── work_items/
    ├── Sprint_YYYY_MM_Closeout_Todo.md
    └── Sprint_YYYY_MM_Master_Closeout_Execution_Plan.md
```

**Rationale:**
- Clear separation of sprint-scoped vs repo-level artifacts
- Easy navigation when working on specific sprints
- Historical archive of completed sprints for reference
- Scalable structure for long-running project

---

## Governance Framework

Repository-level policies and execution gates managed in `Governance/`:

- **Execution Mode Policy**: Linear vs Branching development modes
- **HITL Gate Definitions**: Human-in-the-loop gate criteria and enforcement
- **Code Review Policy**: Standards for PR review and approval
- **Release Policy**: Version management and release criteria

*Note: Governance subdirectory created as scaffold; policies planned for future definition.*

---

## Requirements & Traceability

See `Requirements/` for:

- **Functional Requirements**: Feature specifications
- **Non-Functional Requirements**: Performance, security, scalability
- **Traceability Matrix**: Maps issues → requirements → test cases
- **Baseline**: Version control of requirements snapshots

---

## Future Sprint Planning

To start a new sprint:

1. **Create directory**: `Sprints/Sprint_YYYY_MM/`
2. **Create subdirectories**: `issues/` and `work_items/`
3. **Create README.md**: Use sprint template from `Templates/`
4. **Move issues**: Populate `issues/` with sprint-scoped items
5. **Create work items**: Closeout checklist and execution plan

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
| Audit & Roadmap | Audit findings + future improvements | `01_Repository_Audit_And_Phase_3-7_Roadmap.md` |
| Traceability Matrix | Requirement → Issue → Test mapping | `Requirements/04_Traceability_Matrix.md` |
| Sprint 2026-11 Details | Active sprint scope and deliverables | `Sprints/Sprint_2026_11/README.md` |
| Requirements Index | System requirements overview | `Requirements/00_Requirements_Index.md` |

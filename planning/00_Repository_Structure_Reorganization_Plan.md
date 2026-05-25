# Repository Structure Reorganization Plan

**Date:** 2026-05-17
**Status:** Planning / In-Review
**Scope:** Logical organization of test artifacts, planning docs, configuration, and future RAG infrastructure.

---

## Executive Summary

Current state has test artifacts, configs, and planning docs scattered across repo root and subdirectories, making navigation and maintenance difficult. This plan reorganizes the repo into clear ownership zones:

- **Root**: Source code, core dependencies, entry points only.
- **docs/**: Architecture, user guides, process documentation.
- **planning/**: Sprint-scoped and repo-level governance (master plan + sprint subdirs).
- **Tests/**: All test configuration, test code, and outputs.
- **src/**: Application source.
- **data/**: Vector DB, RAG inputs, persisted indexes (future).

---

## Current Pain Points

| Issue | Current State | Impact |
|-------|---------------|--------|
| Test config fragmented | `conftest.py` and `pytest.ini` in root | Unclear which configs apply globally vs. test-scoped |
| FQT outputs at root level | `FQT/` folder in repo root | Confuses project deliverables with test artifacts |
| Test reports disorganized | Multiple `*.log` files + subdirs with scattered supporting files | Hard to find complete evidence for a single test run |
| Planning docs scattered | `planning/` has mixed sprint + overall scope without clear hierarchy | Difficult to navigate sprint-specific vs. repo-level decisions |
| No RAG/vector infrastructure | No vector_db or inputs folder structure | Future RAG work blocked by missing scaffold |

---

## Proposed Structure

```
Multi Agent Threat Modeler/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── .env (local secrets, not in repo)
│
├── src/
│   └── threat_modeler/
│       ├── __main__.py
│       └── ... (existing source)
│
├── docs/
│   ├── README.md
│   ├── User_Manual.md
│   ├── HMI_Architecture_Blueprint.md
│   └── ... (existing docs)
│
├── Tests/
│   ├── conftest.py              # ← MOVE from root
│   ├── pytest.ini               # ← MOVE from root
│   ├── requirements_e2e.txt     # ← CONSOLIDATE here
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── fixtures/
│   └── test_reports/            # ← NEW: test outputs only
│       └── YYYY-MM-DD/
│           ├── sprint_traceability/
│           │   ├── report.md
│           │   └── supporting_files/
│           ├── pytest/
│           │   ├── report.json
│           │   └── supporting_files/
│           └── live_browser_e2e_smoke/
│               ├── fqt_uas_20260517_204634/
│               │   ├── report.md
│               │   ├── report.json
│               │   ├── screenshots/
│               │   ├── downloads/
│               │   └── smoke_run.log
│
├── planning/
│   ├── README.md
│   ├── Master_Plan.md           # ← TOP-LEVEL governance
│   ├── Requirements/            # ← Repo-level requirements
│   ├── Releases/                # ← Release artifacts
│   ├── Sprints/                 # ← NEW: sprint-scoped work
│   │   ├── Sprint_2026_09/
│   │   │   ├── README.md
│   │   │   ├── plan.md
│   │   │   ├── traceability_matrix.md
│   │   │   ├── issues/
│   │   │   │   ├── D_S09_001_*.md
│   │   │   │   └── ...
│   │   │   └── work_items/
│   │   └── Sprint_2026_11/
│   │       ├── README.md
│   │       ├── plan.md
│   │       ├── traceability_matrix.md
│   │       ├── issues/
│   │       └── work_items/
│   └── Governance/              # ← NEW: repo-level governance
│       ├── execution_mode_policy.md
│       ├── gate_definitions.md
│       └── ...
│
├── data/                        # ← NEW: vector DB and RAG inputs
│   ├── vector_db/
│   │   ├── README.md
│   │   └── indexes/             # Persistent vector indexes
│   ├── inputs/
│   │   ├── README.md
│   │   ├── Aerospace_Architecture/   # Aerospace ingested docs
│   │   ├── threat_libraries/    # Reference threat data
│   │   └── fixtures/            # Test data
│   └── models/
│       └── README.md
│
├── scripts/
│   ├── run_and_log.py
│   ├── set_test_env.ps1
│   ├── verify_sprint_traceability.py
│   ├── live_browser_e2e_smoke.py
│   └── ... (all standalone scripts)
│
├── Releases/                    # ← MOVE from planning/ if present
├── Requirements/                # ← MOVE from planning/ if present
```

---

## Migration Phases

### Phase 1: Test Infrastructure Consolidation (Immediate)

**Scope:** Organize test artifacts and move test configs.

- [ ] Move `conftest.py` → `Tests/conftest.py`
- [ ] Move `pytest.ini` → `Tests/pytest.ini`
- [ ] Move `FQT/` → `Tests/test_reports/2026-05-17/live_browser_e2e_smoke/fqt_uas_*/`
- [ ] Move `.coverage*` → `Tests/.coverage*`
- [ ] Restructure `test_reports/` per proposed format (report + supporting_files subdir)
- [ ] Update `.gitignore` to ignore `Tests/test_reports/*` except README

**Deliverable:** Clean test directory with clear report-per-run structure.

---

### Phase 2: Planning Reorganization (This Sprint)

**Scope:** Hierarchy for sprint-scoped and repo-level planning.

- [ ] Create `planning/Sprints/` directory
- [ ] Move `planning/issues/` → `planning/Sprints/Sprint_2026_11/issues/` (current sprint)
- [ ] Move sprint-related work items into corresponding sprint folders
- [ ] Create `planning/Governance/` for repo-level policies
- [ ] Move gate definitions, execution mode policy, etc. to `planning/Governance/`
- [ ] Create `planning/Master_Plan.md` summarizing all active sprints + roadmap
- [ ] Update `planning/README.md` with new hierarchy

**Deliverable:** Sprint-scoped planning clearly separated from repo-level governance.

---

### Phase 3: Data Infrastructure Setup (Next Sprint)

**Scope:** Prepare vector DB and RAG input structure (scaffolding only for now).

- [ ] Create `data/vector_db/` with README
- [ ] Create `data/inputs/` with subdirs: `Aerospace_Architecture/`, `threat_libraries/`, `fixtures/`
- [ ] Document data schema and ingestion patterns in `data/README.md`
- [ ] Add `.gitignore` entries for vector indexes and temp files

**Deliverable:** Structure ready for RAG implementation in 2026-12.

---

### Phase 4: Configuration Consolidation (Post-Phase 1)

**Scope:** Centralize test and build configs.

- [ ] Move `pyproject.toml` configs into `Tests/` as needed
- [ ] Consolidate `Tests/requirements_e2e.txt` from scattered E2E deps
- [ ] Create `Tests/README.md` with test running guides
- [ ] Update root `README.md` to point to `Tests/README.md` for test docs

**Deliverable:** Clear test configuration story.

---

## File Movements: Detailed

### Test Config Files

| File | Current | New | Rationale |
|------|---------|-----|-----------|
| `conftest.py` | `/` | `/Tests/` | Pytest configuration belongs in test dir |
| `pytest.ini` | `/` | `/Tests/` | Pytest config belongs in test dir |
| `.coverage` | `/` | `/Tests/` | Coverage artifacts are test outputs |
| `.coveragerc` | `/` | `/Tests/` | Coverage config belongs in test dir |

### Test Artifacts

| Directory | Current | New | Rationale |
|-----------|---------|-----|-----------|
| `FQT/` | `/` | `/Tests/test_reports/YYYY-MM-DD/live_browser_e2e_smoke/` | FQT = formal qualification test = test output |
| `test_reports/` | `/` | `/Tests/test_reports/` | Test outputs belong in test dir |

### Planning Hierarchy

| Directory | Current | New | Rationale |
|-----------|---------|-----|-----------|
| `planning/issues/` | `/planning/issues/` | `/planning/Sprints/Sprint_*/issues/` | Sprint issues scoped to sprint |
| `planning/work_items/` | `/planning/work_items/` | `/planning/Sprints/Sprint_*/work_items/` | Sprint work scoped to sprint |
| Requirements | `/Requirements/` or `/planning/Requirements/` | `/planning/Requirements/` | Repo-level requirements consolidated |
| Releases | `/Releases/` or `/planning/Releases/` | `/planning/Releases/` | Release artifacts consolidated |

---

## .gitignore Updates

```gitignore
# Test artifacts (moved to Tests/)
/Tests/test_reports/*
!/Tests/test_reports/README.md
/Tests/.coverage*

# Vector DB and RAG artifacts (not for repo)
/data/vector_db/indexes/*
/data/inputs/fetched/*
*.sqlite
*.faiss
```

---

## Rollout & Approval Gates

- [ ] **Review Phase**: User review of proposed structure
- [ ] **Phase 1 Gate**: Confirm test directory consolidation before moving FQT and test_reports
- [ ] **Phase 2 Gate**: Confirm planning hierarchy before mass move
- [ ] **Phase 3 Gate**: Confirm data structure scaffold before implementation
- [ ] **Cutover**: Execute moves, update configs, test runs, commit to repo

---

## Success Criteria

- [ ] All test configs centralized in `/Tests/` with clear ownership
- [ ] Each test run has exactly one report file + one supporting_files subdir
- [ ] Sprint-scoped planning is in `/planning/Sprints/Sprint_*/`
- [ ] Repo-level governance is in `/planning/` or `/planning/Governance/`
- [ ] `data/` scaffold exists and documented
- [ ] Root directory is clean (no test, planning, or data clutter)
- [ ] All tests pass after moves
- [ ] Git history is preserved via git mv

---

## Notes

- **Backward Compatibility**: Update CI/CD configs to point to new locations
- **Scripts**: Update `scripts/run_and_log.py` and other test runners to use new paths
- **Documentation**: Update README files in each new directory to explain purpose and structure
- **Commit Strategy**: Use `git mv` for all file moves to preserve history

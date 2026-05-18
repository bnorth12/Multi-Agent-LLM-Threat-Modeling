# Repository Structure Audit & Recommendations
## Final Phase Adjustments (Phase 3+)

**Date:** 2026-05-17  
**Completed Phases:** Phase 1 (Test Infrastructure) ✅, Phase 2 (Planning Reorganization) ✅  
**Next Steps:** Phase 3 (Data Scaffolding), Phase 4 (Config Consolidation), Phase 5+ (Additional Improvements)

---

## Audit Summary

### Phase 1 & 2: Completed Actions ✅

| Phase | Task | Status | Impact |
|-------|------|--------|--------|
| **Phase 1** | Move `conftest.py`, `pytest.ini` → `Tests/` | ✅ Complete | Test configs consolidated |
| **Phase 1** | Move `FQT/` → `Tests/test_reports/YYYY-MM-DD/live_browser_e2e_smoke/` | ✅ Complete | FQT runs organized by date |
| **Phase 1** | Reorganize `test_reports/` with report + supporting_files structure | ✅ In Progress | Test artifacts now grouped by run |
| **Phase 2** | Create `planning/Sprints/Sprint_2026_11/` | ✅ Complete | Sprint work clearly scoped |
| **Phase 2** | Move sprint issues & work items to sprint folders | ✅ Complete | Sprint artifacts consolidated |
| **Phase 2** | Create `planning/Governance/` scaffold | ✅ Complete | Repo-level policy location ready |

---

## Additional Findings: Root-Level Clutter

### Current Root Files (Non-Standard)
| File | Size | Purpose | Recommendation |
|------|------|---------|-----------------|
| `generate_exports_for_manual.py` | Utility | Exports threat data | **Move to** `scripts/generators/export_manual.py` |
| `Python_Dependency_Strategy.md` | Doc | Dependency guidance | **Move to** `docs/governance/` |
| `.coverage` | 68KB | Test coverage data | **Move to** `Tests/.coverage` (already done for pytest.ini) |
| `CONTRIBUTING.md` | Doc | Contribution guide | **Keep in root** (standard location) |
| `README.md` | Doc | Project overview | **Keep in root** (standard location) |
| `LICENSE` | Legal | License file | **Keep in root** (standard location) |

### Recommended Root Structure After Cleanup
```
/ (root)
├── README.md              ✅ Project overview
├── LICENSE                ✅ Legal
├── CONTRIBUTING.md        ✅ Contribution guidelines
├── requirements.txt       ✅ Top-level dependencies
├── pyproject.toml         ✅ Project config
├── .gitignore            ✅ VCS config
├── .env                  ✅ Local env (not in repo)
│
├── src/                  ✅ Application source
├── Tests/                ✅ All test code & config
├── docs/                 ✅ Documentation
├── scripts/              ✅ Utilities, tools
├── planning/             ✅ Sprint & governance
│
└── data/                 ⬜ NEW: Vector DB & inputs (Phase 3)
```

---

## Detailed Recommendations: Phases 3–5

### Phase 3: Data Infrastructure Scaffolding (Next Sprint)

**Status:** Prep phase for RAG implementation (2026-12)

```
data/
├── README.md
├── vector_db/
│   ├── README.md
│   ├── indexes/           # Persistent FAISS/Chroma indexes
│   ├── config.yaml        # Embedding model & dimension config
│   └── .gitignore         # Ignore indexes, keep config
├── inputs/
│   ├── README.md
│   ├── architecture_docs/ # System documentation for ingestion
│   ├── threat_libraries/  # Reference threat catalogs
│   ├── fixtures/          # Test data
│   └── fetched/           # Downloaded/ingested content (.gitignore)
├── models/
│   ├── README.md
│   └── embeddings.yaml    # Embedding model catalog
└── outputs/
    ├── README.md
    └── .gitignore         # Ignore generated outputs
```

**Deliverable:** Directory structure + README with ingestion patterns and RAG contract.

---

### Phase 4: Configuration Consolidation (After Phase 1 Stable)

**Move** test-specific configs under `Tests/`:

```
Tests/
├── pytest.ini             ✅ Moved (Phase 1)
├── conftest.py            ✅ Moved (Phase 1)
├── .coveragerc            ✅ In place
├── pyproject.toml         ← NEW: Extract test-only sections
└── requirements_e2e.txt   ← Consolidate browser test deps
```

**Action Items:**
- Extract `[tool.pytest]` config from root `pyproject.toml` → `Tests/pyproject.toml`
- Move `.coveragerc` to `Tests/.coveragerc` (currently in root)
- Create `Tests/README.md` with test running guide (reference `run_and_log.py`)

---

### Phase 5: Script Organization (After Phase 4)

**Organize scripts/ by category:**

```
scripts/
├── README.md               # Guide to scripts
├── run_and_log.py          ✅ Unified test runner
├── set_test_env.ps1        ✅ Environment setup
├── verify_sprint_traceability.py  ✅ Traceability check
├── live_browser_e2e_smoke.py      ✅ Browser smoke test
│
├── generators/             ← NEW: Code generators & exporters
│   ├── export_manual.py    (move from root)
│   ├── generate_stix.py
│   └── generate_diagrams.py
│
├── utilities/              ← NEW: Maintenance & utility scripts
│   ├── setup_git_hooks.sh
│   ├── rebuild_cache.py
│   └── cleanup_old_runs.py
│
└── ci_cd/                  ← NEW: CI/CD pipeline scripts
    ├── run_tests.sh
    ├── publish_release.sh
    └── validate_build.sh
```

**Deliverable:** Organized scripts with each category's README.

---

### Phase 6: Planning Document Consolidation (Before Sprint Close)

**Current State:** Planning root has ~30 sprint-specific docs mixed with templates and processes.

**Recommendation:** Archive completed sprint docs, keep active sprint + templates visible.

```
planning/
├── README.md                         # Top-level planning guide
├── Master_Plan.md                    # Roadmap (all sprints)
├── Governance/
│   ├── Execution_Mode_Policy.md
│   ├── HITL_Gate_Definitions.md
│   └── Code_Review_Policy.md
├── Sprints/
│   ├── Sprint_2026_11/
│   │   ├── README.md
│   │   ├── plan.md
│   │   ├── issues/
│   │   └── work_items/
│   └── Sprint_2026_12/               ← NEW: Next sprint stub
├── Templates/                         ← NEW: Planning templates
│   ├── Sprint_Planning_Checklist.md
│   ├── Sprint_Traceability_Matrix.md
│   └── Issue_Template.md
├── Requirements/                      ✅ Already present
└── Releases/                          ✅ Already present
└── Archive/                           ← NEW: Completed sprint docs
    └── Sprint_2026_05/
    └── Sprint_2026_09/
    └── Sprint_2026_10/
```

**Action Items:**
- Create `planning/Master_Plan.md` (roadmap view of all sprints)
- Create `planning/Templates/` with reusable templates
- Create `planning/Archive/` and move completed sprint docs there
- Update `planning/README.md` with navigation guide

---

## Root-Level Cleanup Checklist

- [ ] **Move** `generate_exports_for_manual.py` → `scripts/generators/export_manual.py`
- [ ] **Move** `Python_Dependency_Strategy.md` → `docs/governance/Python_Dependency_Strategy.md`
- [ ] **Move** `.coverage` → `Tests/.coverage` (if applicable)
- [ ] **Update** `.gitignore` to reflect new paths
- [ ] **Verify** all imports/references are updated
- [ ] **Test** build and test pipelines after moves

---

## Summary Table: Complete Reorganization Roadmap

| Phase | Scope | Status | Est. Impact | Timeline |
|-------|-------|--------|-------------|----------|
| **1** | Test infrastructure (configs, FQT, reports) | ✅ Complete | Clean root, organized test outputs | Done |
| **2** | Planning hierarchy (sprint-scoped work) | ✅ Complete | Clear sprint vs repo-level separation | Done |
| **3** | Data infrastructure (RAG scaffold) | ⬜ Scheduled | Prep for 2026-12 RAG work | Next sprint |
| **4** | Configuration consolidation (pytest, coverage) | ⬜ Planned | Further test directory cleanup | Post-Phase-1-stable |
| **5** | Script organization (categorized tooling) | ⬜ Planned | Better discoverability of utilities | Post-Phase-4 |
| **6** | Planning cleanup (archive old sprints) | ⬜ Planned | Reduced planning root clutter | Sprint close |
| **7** | Root cleanup (move generators, docs) | ⬜ Planned | Minimal, clean root directory | Final polish |

---

## Next Action: Push Changes & Create Session Summary

1. **Commit Phase 2 changes** → `git push` ✅
2. **Create Phase 3 scaffold** (data/) for next sprint
3. **Document this audit** in memory for future reference
4. **Provide user with summary** of completed work and roadmap

---

## Notes for Future Reference

- **UTF-8 Environment Handling**: Now enforced in `run_and_log.py` and `set_test_env.ps1`
- **Test Report Structure**: Each run gets one report + `supporting_files/` subdir
- **Sprint Scoping**: All sprint-specific artifacts now under `planning/Sprints/Sprint_YYYY_MM/`
- **Git History**: All moves used `git mv` to preserve commit history

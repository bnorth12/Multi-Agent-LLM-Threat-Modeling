# Sprint 2026-12: Release Engineering & Test Environment Separation

**Date**: 2026-05-18
**Status**: Planning
**Sprint Length**: 2 weeks
**Target End**: 2026-06-01
**Sprint Lead**: [To be assigned]

---

## Executive Summary

Sprint 2026-12 marks a **strategic transition from development to release engineering**. The primary goal is to establish a **production-ready release architecture** by separating test infrastructure from the production codebase, creating a standalone GUI without test-framework dependencies, and delivering the **first official Release Candidate (RC1)** for v1.0.0.

This sprint is the foundation for a sustainable release process: clean separations enable independent testing, deployment validation, and user-facing functionality without test harness pollution.

---

## Story Map

The story map is the execution source of truth for the sprint. Strategic objectives summarize intent; stories define the delivery slices and the checklist items below execute them.

| Story ID | Epic | Story Detail | Exit Evidence |
|----------|------|--------------|---------------|
| S12-01 | Dependency Isolation | Separate test infrastructure from production dependencies and imports. | `requirements-prod.txt`, `requirements-dev.txt`, clean `src/` import tree |
| S12-02 | GUI Separation | Make the Streamlit GUI production-clean and remove test harness coupling. | Standalone GUI entry point, `tests_only/` structure |
| S12-03 | Release Engineering | Add semantic versioning, build config, and release artifact controls. | RC1 tag, wheel/sdist artifacts, release notes |
| S12-04 | Release Validation | Define and execute release smoke tests and clean-environment validation. | `Release_RC1_Validation_Report.md` |
| S12-05 | Release Publication | Publish RC1 and document the release promotion path. | GitHub release pre-release, promotion checklist |
| S12-06 | Governance Handoff | Lock the S13 handoff on the release-clean backend baseline. | Handoff checklist, S13 preview alignment |

---

## Strategic Objectives

1. **Test Environment Separation**: Refactor repository structure to isolate test infrastructure (pytest, test fixtures, test utilities) from production code. Enable independent deployment of the application without test dependencies.

2. **Standalone GUI Implementation**: Create a production GUI that does not depend on Streamlit test-framework functionality. GUI shall be distributable and functional independent of test suite.

3. **Release Candidate Generation (RC1)**: Configure and build v1.0.0-rc1 as a formal release artifact with:
   - Version tagging in git
   - Release notes documenting features, fixes, known issues
   - Build/distribution configuration
   - Deployment validation checklist

4. **Release Configuration & Testing**: Set up release-specific testing policies:
   - Define what "release testing" means (smoke tests, integration tests, NOT full dev test suite)
   - Configure GitHub release artifact generation
   - Validate RC1 can be deployed and run independently

5. **Production Readiness Gate**: Establish HITL checklist for release promotion from RC1 to GA (v1.0.0):
   - Documentation completeness
   - No known critical/high defects
   - Deployment tested in staging-like environment
   - User manual validated

---

## 0. Scope & Deferrals

### In-Scope for Sprint 2026-12

- Repository architecture refactoring to separate test infrastructure from production
- Streamlit GUI removal from production code paths (keep test E2E Streamlit as test-only)
- Build configuration (e.g., `setup.py`, `pyproject.toml` updates) to exclude test dependencies from production
- Release artifact generation (v1.0.0-rc1 tagging, release notes, build outputs)
- Release testing strategy and validation checklist
- GitHub release page configuration and publication of RC1

### Out-of-Scope for Sprint 2026-12 (Defer to Sprint 2026-13)

- Full production deployment automation (CI/CD for releases)
- Alternative frontend implementations (Web UI, REST API service wrapper)
- Performance tuning or scalability improvements
- Full user acceptance testing or beta program

---

## 1. Current State Baseline

**As of Commit**: `092ff19` (sprint-2026-11-closeout)

**Key Facts**:

- Repository clean; main/local synced; all S11 deliverables committed
- Non-live tests passing (Unit, Integration, E2E)
- Live LLM test deferred (streamlit dependency)
- Streamlit integrated into `src/threat_modeler/ui/` as optional runtime dependency
- Test infrastructure (pytest, test fixtures, E2E smoke scripts) scattered in `Tests/` and `scripts/`
- No formal release configuration; versioning ad-hoc in comments

**Release Gap**: Repository structured as development project; no production-clean distribution available.

---

## 2. Key Misalignments to Resolve

| Misalignment | Current State | Target State | Priority |
|---|---|---|---|
| **Test imports in production code** | Test utilities imported in production paths | Test imports isolated to `tests_only/` or test-marked code paths | HIGH |
| **Streamlit in production bundle** | Streamlit dependency in main requirements.txt | Streamlit only in `[extras]` or `[dev]` deps | HIGH |
| **No version/release management** | Version strings ad-hoc in code | Semantic versioning (v1.0.0-rc1) in setup.py + git tags | HIGH |
| **Unstructured release artifacts** | No formal build/dist configuration | Build outputs (wheel, sdist) reproducible and tested | MEDIUM |
| **No release test policy** | All tests run for release validation | Explicit "release smoke test" suite defined | MEDIUM |
| **No GitHub release integration** | No release page or artifacts on GitHub | RC1 published as GitHub Release with notes + artifacts | LOW |

---

## 3. Phase-Ordered Sprint Execution

### Phase 1: Test Infrastructure Audit & Dependency Isolation (Days 1-4)

**Objective**: Map all test dependencies and create a clean separation between test and production code.

**Tasks**:

- [ ] **Story S12-01 / T1.1**: Audit all imports in `src/` for test-framework references (pytest, mock, test fixtures)
  - Generate report: `planning/Test_Dependency_Audit_Sprint_2026_12.md`
  - Identify files with mixed concerns

- [ ] **Story S12-01 / T1.2**: Audit production requirements
  - Review `requirements.txt` and `pyproject.toml`
  - Segregate into: core, optional (streamlit, dev tools, test tools)
  - Document in: `planning/Dependency_Segregation_Plan.md`

- [ ] **Story S12-01 / T1.3**: Create `requirements-prod.txt` and `requirements-dev.txt`
  - Production: only core deps (langchain, langgraph, pydantic, etc.)
  - Dev: prod + streamlit + pytest + dev tools

- [ ] **Story S12-01 / T1.4**: Validate production import tree
  - Confirm `src/` has zero test-framework imports
  - Fix any violations (move to test-only modules or add lazy imports)

**Phase 1 Exit Criteria**:
- [ ] Dependency audit complete; no test imports in `src/` (except lazy imports or optional features)
- [ ] requirements-prod.txt verified installable without pytest
- [ ] Evidence: audit report + updated requirements files in git

**Acceptance Gate**: Team review + PO sign-off on separation strategy

---

### Phase 2: GUI & Streamlit Refactoring (Days 5-8)

**Objective**: Make Streamlit UI optional and remove test harness dependencies from production GUI code.

**Tasks**:

- [ ] **Story S12-02 / T2.1**: Refactor `src/threat_modeler/ui/` to remove test-framework dependencies
  - Move test-only Streamlit components to `tests_only/` module (new)
  - Streamlit app remains in `src/` but with clean import boundaries

- [ ] **Story S12-02 / T2.2**: Create `tests_only/` directory structure
  ```
  tests_only/
    __init__.py
    e2e/
      streamlit_test_components.py  (test-harness UI code)
      browser_fixtures.py
    fixtures/
      (existing test fixtures)
    utils/
      (existing test utilities)
  ```

- [ ] **Story S12-02 / T2.3**: Update test imports to use `tests_only/`
  - Tests now import from `tests_only.e2e` instead of `src`
  - Confirms test code is decoupled from production UI

- [ ] **Story S12-02 / T2.4**: Create standalone Streamlit app entry point
  - `src/threat_modeler/ui/app.py` as pure Streamlit application
  - No test dependencies; production-ready
  - Can be run: `streamlit run src/threat_modeler/ui/app.py`

**Phase 2 Exit Criteria**:
- [ ] `src/` code has zero test-framework imports
- [ ] `tests_only/` module created and test suite migrated
- [ ] Streamlit GUI runs standalone without test infrastructure
- [ ] All tests still pass using `tests_only/` imports

**Acceptance Gate**: Integration test pass + manual Streamlit app validation

---

### Phase 3: Release Configuration & Versioning (Days 9-11)

**Objective**: Configure repository for formal release process and generate v1.0.0-rc1.

**Tasks**:

- [ ] **Story S12-03 / T3.1**: Set up semantic versioning
  - Update `pyproject.toml` with `version = "1.0.0rc1"`
  - Update `src/threat_modeler/__init__.py` with `__version__ = "1.0.0rc1"`
  - Add version retrieval function for runtime access

- [ ] **Story S12-03 / T3.2**: Create release configuration
  - Update `setup.py` / `pyproject.toml`:
    - Exclude `tests_only/` and `Tests/` from distribution
    - Set production dependencies (requirements-prod.txt)
    - Mark optional dependencies: `streamlit` (for CLI use), dev tools

- [ ] **Story S12-03 / T3.3**: Build release artifacts
  - `python -m build`  → generates wheel + sdist
  - Verify artifact contents (no test files, no test fixtures)
  - Test artifact install: `pip install dist/threat-modeler-1.0.0rc1.whl`

- [ ] **Story S12-05 / T3.4**: Create release notes
  - File: `Releases/v1.0.0-rc1_Release_Notes.md`
  - Content:
    - Key features delivered (LangGraph orchestration, HITL gates, multi-agent threat modeling)
    - Known issues (streamlit in live CI deferred to next sprint, etc.)
    - Installation instructions
    - Quick-start guide
    - Breaking changes (if any)

- [ ] **Story S12-03 / T3.5**: Create release tag in git
  - Tag: `v1.0.0-rc1`
  - Message: Release notes excerpt
  - Push to origin

**Phase 3 Exit Criteria**:
- [ ] Versioning consistent across codebase
- [ ] Release artifacts built and tested
- [ ] Release notes published
- [ ] Git tag v1.0.0-rc1 pushed to origin

**Acceptance Gate**: Release artifact validation + notes review

---

### Phase 4: Release Testing & Validation (Days 12-13)

**Objective**: Validate RC1 is production-ready; establish release test policy.

**Tasks**:

- [ ] **Story S12-04 / T4.1**: Define "Release Test" suite
  - Create `Tests/e2e/test_release_smoke.py`
  - Smoke test suite covering:
    - Threat model creation (basic workflow)
    - Report generation
    - API responses under normal load
    - UI loads and responds (if GUI included)
  - NOT full unit/integration suite (too heavy for release validation)

- [ ] **Story S12-04 / T4.2**: Test RC1 in clean environment
  - Fresh Python venv
  - Install from artifact: `pip install dist/threat-modeler-1.0.0rc1.whl`
  - Run smoke test suite
  - Document results: `test_reports/Release_RC1_Validation_Report.md`

- [ ] **Story S12-02 / T4.3**: Test Streamlit GUI (optional feature)
  - Install with `pip install .[gui]` (if configurable extras)
  - `streamlit run app.py`
  - Manual validation: UI loads, basic workflow functional
  - Document: `test_reports/Streamlit_GUI_RC1_Validation.md`

- [ ] **Story S12-05 / T4.4**: Create Release Promotion Checklist
  - File: `Releases/Release_Promotion_Checklist_v1.0.0.md`
  - HITL gate items for GA promotion:
    - [ ] All smoke tests pass
    - [ ] No critical/high defects open
    - [ ] Release notes reviewed by PO
    - [ ] Documentation updated (README, User Manual)
    - [ ] Deployment tested in staging
    - [ ] Security audit (if applicable) passed

**Phase 4 Exit Criteria**:
- [ ] Release smoke test suite passes
- [ ] RC1 validation report complete; no blockers found
- [ ] Release Promotion Checklist ready for next sprint
- [ ] Evidence: test reports + validation docs

**Acceptance Gate**: Release validation sign-off + promotion checklist PO review

---

### Phase 5: GitHub Release Publication (Day 14)

**Objective**: Publish RC1 on GitHub as formal release artifact.

**Tasks**:

- [ ] **Story S12-05 / T5.1**: Publish GitHub Release
  - Go to GitHub repo Releases tab
  - Create Release from tag `v1.0.0-rc1`
  - Upload build artifacts (wheel, sdist)
  - Paste release notes
  - Mark as **Pre-release** (not GA)
  - Publish

- [ ] **Story S12-05 / T5.2**: Update top-level README
  - Add section: "Latest Release: v1.0.0-rc1 (Release Candidate)"
  - Link to release page
  - Update install instructions: `pip install threat-modeler==1.0.0rc1`

- [ ] **Story S12-06 / T5.3**: Create sprint closure summary
  - File: `planning/Sprint_2026_12_Closure_Summary.md`
  - What was delivered: test env separation, RC1 build, release policy
  - What's pending: GA promotion (requires PO sign-off in S13)
  - Lessons learned

**Phase 5 Exit Criteria**:
- [ ] GitHub Release published and publicly visible
- [ ] Installation via PyPI/artifact link works
- [ ] Sprint closure docs complete

---

## 4. Traceability Matrix

| Req ID | Description | Issue | Status | Test File | Evidence |
|--------|-------------|-------|--------|-----------|----------|
| S12-001 | Audit test dependencies in src/ | D-S12-001 | To Start | N/A | `planning/Test_Dependency_Audit_Sprint_2026_12.md` |
| S12-002 | Segregate production vs dev requirements | D-S12-002 | To Start | `tests_only/test_requirements_isolation.py` | `requirements-prod.txt`, `requirements-dev.txt` |
| S12-003 | Refactor GUI to remove test harness deps | D-S12-003 | To Start | `tests_only/e2e/test_streamlit_production_gui.py` | Streamlit app runs standalone |
| S12-004 | Create tests_only/ module structure | D-S12-004 | To Start | N/A | `tests_only/` directory committed |
| S12-005 | Configure semantic versioning | D-S12-005 | To Start | `tests/unit/test_version_metadata.py` | `__version__` in `__init__.py`, pyproject.toml |
| S12-006 | Build release artifacts | D-S12-006 | To Start | `test_reports/Release_RC1_Validation_Report.md` | Wheel + sdist generated and tested |
| S12-007 | Create release notes for RC1 | D-S12-007 | To Start | N/A | `Releases/v1.0.0-rc1_Release_Notes.md` |
| S12-008 | Define and execute release smoke test suite | D-S12-008 | To Start | `Tests/e2e/test_release_smoke.py` | `test_reports/Release_RC1_Validation_Report.md` |
| S12-009 | Create release promotion checklist | D-S12-009 | To Start | N/A | `Releases/Release_Promotion_Checklist_v1.0.0.md` |
| S12-010 | Publish RC1 on GitHub Releases | D-S12-010 | To Start | N/A | GitHub release page with artifacts |

---

## 5. Acceptance Criteria & Definition of Done

### Sprint-Level Acceptance

- [ ] All test imports removed from `src/`; zero violations confirmed by linter
- [ ] `requirements-prod.txt` installable and functional
- [ ] Streamlit GUI runs standalone: `streamlit run src/threat_modeler/ui/app.py`
- [ ] v1.0.0-rc1 artifacts generated, tested, and reproducible
- [ ] Release smoke test suite defined and passing
- [ ] GitHub Release page published with RC1 artifacts and release notes
- [ ] Release Promotion Checklist ready for PO review in next sprint

### Per-Issue DoD

- [ ] Code changes peer-reviewed
- [ ] Tests written and passing (or rationale documented if N/A)
- [ ] Traceability matrix updated
- [ ] Evidence committed to `test_reports/` or `planning/`
- [ ] No test/prod code mixed in commits

---

## 6. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Test imports deeply embedded in src/ | Medium | High | Phase 1 audit will identify scope; allocate extra time if severe |
| Streamlit refactor breaks UI | Medium | Medium | Phase 2: keep Streamlit as optional; test both with/without |
| Build artifact too large or polluted | Low | Medium | Phase 3: verify artifact contents carefully; use .gitignore + setup.py exclusions |
| Release smoke test inadequate | Low | Medium | Phase 4: collaborate with PO to define minimum coverage |
| GitHub release publication fails | Very Low | Low | Document manual workaround; test in advance |

---

## 7. Sprint Success Metrics

- **Delivery**: ✅ v1.0.0-rc1 published on GitHub Releases
- **Quality**: ✅ Release smoke test suite 100% passing
- **Governance**: ✅ Traceability matrix 10/10 items closed; evidence in git
- **Architecture**: ✅ `src/` has zero test imports; `tests_only/` module functional
- **Documentation**: ✅ Release notes complete; promotion checklist ready for PO

---

## 8. Governance & Rollout

### Release Governance Controls

- [ ] RC1 promotion requires PO sign-off on the Release Promotion Checklist.
- [ ] The release branch/tag is the source of truth for RC1 artifacts.
- [ ] Any production dependency change after RC1 tagging is deferred or handled as a patch release.
- [ ] Build artifacts are verified for content before publication.
- [ ] Release validation evidence is retained in `test_reports/` and referenced from the release notes.

### Rollout Sequence

- [ ] Complete dependency isolation and GUI split.
- [ ] Build and verify RC1 artifacts in a clean environment.
- [ ] Run release smoke tests against the installed artifact.
- [ ] Publish RC1 as a GitHub pre-release.
- [ ] Collect PO review feedback and lock promotion criteria for S13.

### Release Sign-Off Checklist

- [ ] Dependency isolation complete.
- [ ] GUI split complete and validated.
- [ ] RC1 artifact built and verified.
- [ ] Smoke tests pass on installed artifact.
- [ ] GitHub release published as pre-release.
- [ ] PO review complete for promotion path.

### Handoff to Sprint 2026-13

- [ ] S13 consumes the RC1 baseline and builds on the release-clean backend boundary.
- [ ] Any S13 packaging changes remain coordinated with the RC1 artifact model.
- [ ] S13 rollout planning assumes the GUI/backend split is complete and stable.

---

## 9. Next Sprint Planning (S13 Preview)

After RC1 baseline, Sprint 2026-13 will focus on:

- [ ] GA promotion: execute Release Promotion Checklist items (PO review, deployment testing, security audit if needed).
- [ ] v1.0.0 release: promote RC1 to GA; publish v1.0.0 on GitHub Releases and PyPI if applicable.
- [ ] Streamlit live LLM fix: install streamlit in CI live lane and validate E2E test suite.
- [ ] User acceptance: beta user onboarding or limited release validation.

---

## 10. Appendices

### A. Repository Structure After Sprint 2026-12

```
threat-modeler-repo/
├── src/
│   └── threat_modeler/
│       ├── __init__.py              # Contains __version__ = "1.0.0rc1"
│       ├── orchestration/           # Core logic (NO test imports)
│       ├── ui/
│       │   └── app.py               # Streamlit GUI (production-clean)
│       └── ...
├── tests_only/                      # NEW: Test-only infrastructure
│   ├── __init__.py
│   ├── e2e/
│   │   ├── streamlit_test_components.py
│   │   └── browser_fixtures.py
│   └── fixtures/
│       └── (test data and utilities)
├── Tests/                           # Existing test suite (updated imports)
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements-prod.txt            # NEW: Production deps only
├── requirements-dev.txt             # NEW: Dev + test deps
├── pyproject.toml                   # Updated: version, extras, exclusions
├── Releases/
│   ├── v1.0.0-rc1_Release_Notes.md
│   └── Release_Promotion_Checklist_v1.0.0.md
└── planning/
    ├── Sprint_2026_12_Release_Engineering_and_Test_Environment_Separation.md
    ├── Test_Dependency_Audit_Sprint_2026_12.md
    ├── Dependency_Segregation_Plan.md
    └── Sprint_2026_12_Closure_Summary.md
```

### B. Dependency Segregation Examples

**Production** (requirements-prod.txt):
```
langchain
langgraph
pydantic
python-dotenv
```

**Development** (requirements-dev.txt):
```
-r requirements-prod.txt
pytest
pytest-cov
pytest-asyncio
streamlit                 # Optional; for GUI development
black
flake8
```

### C. Release Artifact Checklist

```
v1.0.0-rc1 Artifacts:
  ✅ threat-modeler-1.0.0rc1.whl
  ✅ threat-modeler-1.0.0rc1.tar.gz
  ✅ MANIFEST.in (excludes tests_only/, Tests/)
  ✅ setup.py / pyproject.toml verified
  ✅ wheel contents verified (no .pyc, no test files)
  ✅ Installable in clean venv
  ✅ Release notes in Releases/
  ✅ Git tag v1.0.0-rc1 pushed
```

---

**Document Version**: 1.0
**Last Updated**: 2026-05-18
**Next Review**: 2026-05-23 (Mid-sprint check-in)

# Test Execution Summary — Sprint 2026-06

**Date:** 2026-05-04
**Performer:** BN
**Sprint:** 2026-06
**Branch:** feature/sprint_2026_06
**Baseline commit:** 362fa4d (origin/main at sprint start)

---

## 1. Test Run Results

| Scope | Command | Result |
|-------|---------|--------|
| All non-live tests | `.venv\Scripts\python.exe -m pytest Tests/ -q --tb=short -m "not llm_live"` | **240 passed, 1 deselected, 0 failed** |
| UI shell unit tests | `.venv\Scripts\python.exe -m pytest Tests/unit/test_ui_app_shell.py -q` | **42 passed** |
| Agent pipeline integration | `.venv\Scripts\python.exe -m pytest Tests/integration/test_agent_pipeline_completeness.py -q` | **Included in 240** |
| HITL Gate Set 2 integration | `.venv\Scripts\python.exe -m pytest Tests/integration/test_hitl_gate_set_2.py -q` | **Included in 240** |
| Retrieval evidence linkage | `.venv\Scripts\python.exe -m pytest Tests/integration/test_retrieval_evidence_linkage.py -q` | **Included in 240** |
| E2E artifact generation | `.venv\Scripts\python.exe -m pytest Tests/e2e/test_artifact_generation.py -q` | **Included in 240** |
| LLM live gate (manual, not CI) | `pytest -m llm_live` | Deselected in CI; sprint validation gate deferred — no XAI_API_KEY in this environment |

**Regression baseline comparison:**

| Sprint | Tests Passing |
|--------|--------------|
| S05 closeout | 226 |
| S06 closeout | **240** (+14 new tests) |

---

## 2. Requirement Coverage

| Requirement ID | Name | Issue | Test File | Status |
|----------------|------|-------|-----------|--------|
| PRJ-003 | Deterministic Pipeline | S06-01 | test_agent_pipeline_completeness.py | ✅ Covered |
| PRJ-004 | Stage Validation Gate | S06-01 | test_agent_pipeline_completeness.py | ✅ Covered |
| PRJ-005 | Full Threat Workflow | S06-01, S06-04 | test_agent_pipeline_completeness.py, test_artifact_generation.py | ✅ Covered |
| PRJ-006 | HITL Governance | S06-02 | test_hitl_gate_set_2.py | ✅ Covered |
| PRJ-007 | Immutable Auditability | S06-02 | test_hitl_gate_set_2.py | ✅ Covered |
| PRJ-008 | Configurable Model Selection | S06-01 | test_agent_pipeline_completeness.py | ✅ Covered |
| PRJ-010 | Evidence-Linked Outputs | S06-03 | test_retrieval_evidence_linkage.py | ✅ Covered |
| PRJ-011 | Export Artifact Set | S06-04 | test_artifact_generation.py | ✅ Covered |
| PRJ-016 | Analyst GUI | S06-07 | test_ui_app_shell.py | ✅ Covered |
| PRJ-018 | Agent Prompt Configurability | S06-07 (partial) | test_ui_app_shell.py | ⚠️ Prompt editor GUI deferred to S07 |
| INT-008 | Visualization Read Contract | S06-03 | test_retrieval_evidence_linkage.py | ✅ Covered |
| INT-010 | STIX Export Contract | S06-04 | test_artifact_generation.py | ✅ Covered |
| INT-011 | Report Export Contract | S06-04 | test_artifact_generation.py | ✅ Covered |
| INT-015 | Model Connection Contract | S06-07 (partial) | test_ui_app_shell.py | ⚠️ Connection validation GUI (SCR-014) deferred to S07 |
| HITL-003 through HITL-011 | HITL Gate Behaviors | S06-02 | test_hitl_gate_set_2.py | ✅ Covered |

---

## 3. Issue Acceptance Criteria Verification

### S06-01 — Agent Pipeline Completeness (GH #18)

| AC | Status | Evidence |
|----|--------|----------|
| `build_default_agents()` returns agent_01–agent_09 | ✅ | test_agent_pipeline_completeness.py |
| Golden-path fixture run executes all 9 stages, non-empty canonical graph | ✅ | test_artifact_generation.py (E2E golden-path) |
| Contract validation runs at every stage transition | ✅ | test_agent_pipeline_completeness.py |
| Invalid stage output raises ValidationHaltError before next stage | ✅ | test_artifact_generation.py (negative-path E2E) |
| Live Grok call (llm_live) — sprint validation gate | ⚠️ | Deferred — XAI_API_KEY not present in this environment |
| Fixture/LLM mode selected solely by ModelSelection | ✅ | test_agent_pipeline_completeness.py |
| Agent prompts loaded from docs/agents/ at runtime | ✅ | Inspection — no prompt text in agent classes |

### S06-02 — HITL Gate Set 2 (GH #19)

| AC | Status | Evidence |
|----|--------|----------|
| Gates 3, 4, 5 open after agent_04, agent_05, agent_07 | ✅ | test_hitl_gate_set_2.py |
| Gate 6 triggers only on conflict condition | ✅ | test_hitl_gate_set_2.py |
| Gate 7 triggers only on export consistency failure | ✅ | test_hitl_gate_set_2.py |
| Accept-as-is and accept-changes advance to next stage | ✅ | test_hitl_gate_set_2.py |
| Save-draft does not advance execution | ✅ | test_hitl_gate_set_2.py |
| Reject halts pipeline, sets hitl_rejected_at_gate | ✅ | test_hitl_gate_set_2.py |
| All 5 gate decisions produce audit record | ✅ | test_hitl_gate_set_2.py |
| Selective rerun resumes without recomputing prior stages | ✅ | test_hitl_gate_set_2.py |

### S06-03 — Retrieval Evidence Linkage (GH #20)

| AC | Status | Evidence |
|----|--------|----------|
| Schema includes source_ids and confidence with correct types | ✅ | canonical_graph.schema.json inspection |
| Enabled retrieval: non-empty source_ids, confidence in [0,1] | ✅ | test_retrieval_evidence_linkage.py |
| Disabled retrieval: source_ids=[], confidence=None | ✅ | test_retrieval_evidence_linkage.py |
| chroma_adapter.py passes Retriever interface contract | ✅ | test_chroma_adapter.py |
| Fixture corpus integration test passes (in-memory, no server) | ✅ | test_retrieval_evidence_linkage.py |

### S06-04 — Artifact Generation & E2E Validation (GH #21)

| AC | Status | Evidence |
|----|--------|----------|
| Fixture-mode run emits non-empty JSON, STIX, Mermaid, Markdown | ✅ | test_artifact_generation.py (golden-path) |
| E2E tests validate artifact structure and presence | ✅ | test_artifact_generation.py |
| Negative-path E2E: safe halt, no downstream artifacts | ✅ | test_artifact_generation.py |
| llm_live test present and excluded from CI | ✅ | Test file + ci.yml -m flag |
| All 4 exporters importable from src.threat_modeler.exports | ✅ | test_artifact_generation.py |

### S06-05 — Release & Operational Readiness (GH #22)

| AC | Status | Evidence |
|----|--------|----------|
| New developer setup reproducible from docs | ✅ | docs/user_manual/index.html §2 Installation |
| Release checklist complete and linked to evidence | ✅ | This summary |
| Runbook includes failure handling and rollback guidance | ✅ | docs/user_manual/index.html §5 Troubleshooting |
| docs/screenshots/ contains ≥1 screenshot per screen | ✅ | 4 screenshots: scr_001–scr_004 |
| docs/screenshots/README.md index present | ✅ | docs/screenshots/README.md |
| Screenshot evidence referenced in test execution summary | ✅ | Section 4 below |

### S06-06 — User Manual (GH #23)

| AC | Status | Evidence |
|----|--------|----------|
| User manual exists at docs/User_Manual.md | ✅ | docs/User_Manual.md |
| Tool overview section (9-agent pipeline, HITL governance) | ✅ | HTML manual §1, Markdown §1 |
| Installation and setup instructions | ✅ | HTML manual §2, Markdown §2 |
| Step-by-step workflow walkthrough | ✅ | HTML manual §3, Markdown §3 |
| HITL gate interaction guide (Gates 0–2) | ✅ | HTML manual §4, Markdown §4 |
| Role-based access reference table | ✅ | HTML manual §5 Configuration Reference |
| Troubleshooting section (≥5 scenarios) | ✅ | HTML manual §5 Troubleshooting — 7 scenarios |
| Annotated screenshots/placeholders | ✅ | HTML manual — 4 figures |
| Glossary | ✅ | HTML manual §6 Glossary |
| docs/INDEX.md updated | ✅ | docs/INDEX.md |

### S06-07 — Streamlit App Shell (GH #24)

| AC | Status | Evidence |
|----|--------|----------|
| App launches without error | ✅ | Running at http://localhost:8502 |
| Navigation sidebar present, links to all delivered screens | ✅ | Screenshot: scr_001_home_run_dashboard.png |
| Role selection appears on first load, persists in session state | ✅ | test_ui_app_shell.py + scr_002_role_selection.png |
| Pipeline Configuration renders defaults, accepts edits | ✅ | test_ui_app_shell.py + scr_003_pipeline_configuration.png |
| Run Dashboard shows placeholder progress for all 9 stages | ✅ | scr_001_home_run_dashboard.png |
| All screens accessible for all 3 roles | ✅ | test_ui_app_shell.py (no role gating this sprint) |
| streamlit in requirements.txt | ✅ | requirements.txt |
| SCR-004 Input Entry Form (added scope) | ✅ | test_ui_app_shell.py + scr_004_input_entry_form.png |

---

## 4. Screenshot Evidence

Visual acceptance criteria evidence captured 2026-05-04 by BN from Streamlit app at
http://localhost:8502 (Default theme, fixture mode).

| Screenshot | Screen | GUI Req | Demonstrates |
|------------|--------|---------|--------------|
| `docs/screenshots/scr_001_home_run_dashboard.png` | Home / Run Dashboard | GUI-003 | Stage progress table (9 stages ⬜ Pending), HITL gate section, Refresh button |
| `docs/screenshots/scr_002_role_selection.png` | Role Selection | — | Author/Reviewer/Approver role cards, role persists in sidebar |
| `docs/screenshots/scr_003_pipeline_configuration.png` | Pipeline Configuration | GUI-013 | Provider/model fields, offline mode, stage multiselect, HITL settings, Apply button |
| `docs/screenshots/scr_004_input_entry_form.png` | Input Entry Form | GUI-001 | System name, file uploader, model connection banner, Start Run button (disabled until valid) |

---

## 5. Sprint Demonstration Record

| Field | Value |
|-------|-------|
| Date | 2026-05-04 |
| Performer | BN |
| Scenario | Full Streamlit app shell walkthrough — all 4 screens, Dark mode toggle, file upload form validation |
| Outcome | All screens render without error; navigation works; Input Entry disables Start button when name is empty; Dark theme applies correctly |
| Evidence | Screenshots in docs/screenshots/ (4 PNGs); 240 passing tests |

---

## 6. Open Items Carried to S07

| Item | Reason Deferred | Target Sprint |
|------|----------------|---------------|
| LLM live sprint validation gate (llm_live mark) | XAI_API_KEY not available in current environment | S07 |
| SCR-012 Model Provider Selection (dropdown, Custom/Intranet provider) | Not in S06 scope; identified gap during S06 review | S07 |
| SCR-013 Model Connection Details (API key, endpoint URL, temperature per-agent) | Not in S06 scope | S07 |
| SCR-014 Connection Validation (Test Connection button) | Not in S06 scope | S07 |
| SCR-010/011 Agent Prompt Editor + Version History (PRJ-018) | Not in S06 scope | S07 |
| SCR-003/004/006–009 remaining Blueprint screens | Not in S06 scope | S07+ |

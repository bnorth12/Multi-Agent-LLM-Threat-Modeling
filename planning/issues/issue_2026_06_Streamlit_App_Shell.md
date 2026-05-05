# Issue: Sprint 2026-06 Streamlit Application Shell

## Sprint
2026-06

## GitHub Issue
GH #24

## Owner Role
HMI Architect and Orchestrator Engineer

## Description
Deliver a working Streamlit application skeleton that provides navigation, session state management,
a role authentication stub, and a pipeline status screen. This shell is the foundation that subsequent
HITL gate screens (S06-02) and operational screens (S06-05) are built on top of. The app must launch
without error and support all three analyst roles.

## Scope

### Application Entry Point
- `src/threat_modeler/ui/app.py` — Streamlit entry point; launched with
  `streamlit run src/threat_modeler/ui/app.py`.
- Navigation sidebar listing all registered screens with active-state highlighting.
- Session state initialisation: `run_id`, `role`, `pipeline_state`, `gate_states`.

### Role Authentication Stub
- Analyst selects role on launch screen: Author, Reviewer, Approver.
- Role stored in `st.session_state["role"]`.
- UI elements conditionally rendered based on role (stub — no real auth provider).
- Role access table matches PRJ-012 author/reviewer/approver definitions.

### Screens Delivered
- SCR-001 (Home/Run Dashboard): pipeline status overview showing stage progress and current gate
  state; maps to HMI Blueprint SCR-001.
- SCR-002 (Role Selection): role picker on first load; role shown in sidebar header.
- SCR-003 (Pipeline Configuration): form to set `ModelSelection` fields (provider, model_name,
  offline_only flag) and `PipelineSettings` enabled stages; pre-populated from
  `build_default_settings()`.

### Integration
- App imports from `src.threat_modeler` package directly; no `sys.path` hacks.
- `streamlit` added to `requirements.txt`.
- Screen router pattern: `pages/` subdirectory under `ui/` with one file per screen.

## Acceptance Criteria
- `streamlit run src/threat_modeler/ui/app.py` launches without error in the venv.
- Navigation sidebar is present and links to all three delivered screens.
- Role selection screen appears on first load; selected role persists in session state.
- Pipeline Configuration screen renders current `build_default_settings()` values and accepts edits.
- Run Dashboard screen shows placeholder stage progress indicators for all nine stages.
- All three screens are accessible for all three roles (no screen is role-blocked in this sprint).
- Streamlit is listed in `requirements.txt`.

## Requirement Links
- PRJ-016

## Dependencies
None (parallel with S06-01; no running pipeline required for the app shell).

## Implementation Notes
- Use Streamlit `st.sidebar` for navigation, `st.session_state` for cross-screen state.
- Screen router: `PAGES = {"Home": home_screen, "Config": config_screen, ...}` dict driven from
  sidebar `st.radio` or `st.selectbox`.
- HMI Blueprint (`docs/HMI_Architecture_Blueprint.md`) is the design authority; screen IDs SCR-001
  through SCR-014 are defined there.
- Do not implement HITL gate screens in this issue — those are S06-02.

## Status
- [ ] Not started
- [ ] In progress
- [x] Completed

## Completion Evidence
- Date: 2026-05-04
- Initials: BN
- `src/threat_modeler/ui/app.py` launches without error on port 8502.
- Navigation sidebar present with 4 screens: Home (Run Dashboard), Input Entry, Role Selection, Pipeline Configuration.
- SCR-004 Input Entry Form (`input_entry.py`) added beyond original scope: file upload (CSV/XLSX/MD/TXT/YAML), system name, description, Start Run button, model connection banner.
- Dark/Default theme toggle added to sidebar via `theme.py`.
- `Tests/unit/test_ui_app_shell.py` — 42 tests covering app shell, session, theme, input entry module structure and parsing.
- All screens accessible for all three roles (Author/Reviewer/Approver).
- `streamlit` listed in `requirements.txt`.
- CI test run: 240 passed, 1 deselected (llm_live), 0 failures.

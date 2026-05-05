# Issue: Sprint 2026-06 Release and Operational Readiness

## Sprint
2026-06

## Owner Role
DevOps Engineer and Documentation Owner

## Description
Establish release readiness baseline with reproducible setup, operational runbooks, and evidence packaging.

## Scope
- Reproducible local setup documentation.
- Runbooks for offline and hybrid profiles.
- Release checklist and evidence bundle structure.
- Screenshot evidence package: capture annotated screenshots of all delivered Streamlit screens from S06-02 (Input Entry Form, Pipeline Status Dashboard, HITL Gate screens, Stage Results Viewer, Configuration screens) and store under `docs/screenshots/`.
- Screenshot index document at `docs/screenshots/README.md` cross-referencing each screenshot to its GUI requirement ID and screen inventory entry (SCR-xxx) from `docs/HMI_Architecture_Blueprint.md`.

## Acceptance Criteria
- New developer setup path is reproducible from docs.
- Release checklist is complete and linked to evidence artifacts.
- Runbook includes failure handling and rollback guidance.
- `docs/screenshots/` directory exists and contains at minimum one annotated screenshot per delivered Streamlit screen (GUI-001, GUI-002, GUI-003 as minimum; all delivered screens preferred).
- `docs/screenshots/README.md` index maps each screenshot file to its SCR-xxx screen inventory ID, GUI requirement ID, and sprint issue that delivered the screen.
- Screenshot evidence is referenced in the S06 test execution summary as visual AC evidence for S06-02 screen acceptance criteria.

## Requirement Links
- PRJ-009
- PRJ-011
- PRJ-016 (Analyst GUI)
- GUI-001 through GUI-014 (as screens are delivered in S06-02)

## Status
- [ ] Not started
- [ ] In progress
- [x] Completed

## Completion Evidence
- Date: 2026-05-04
- Initials: BN
- `docs/screenshots/` directory populated with 4 annotated screenshots: `scr_001_home_run_dashboard.png`, `scr_002_role_selection.png`, `scr_003_pipeline_configuration.png`, `scr_004_input_entry_form.png`.
- `docs/screenshots/README.md` index cross-references each screenshot to SCR-xxx, GUI requirement ID, and sprint issue.
- Screenshot evidence referenced in Sprint 2026-06 Test Execution Summary.
- `requirements.txt` updated with all sprint dependencies (streamlit, chromadb, stix2, openpyxl).
- New developer setup path documented in `docs/User_Manual.md` and `docs/user_manual/index.html`.

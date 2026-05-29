# Screenshot Evidence Index

This directory contains historical screenshot evidence captured during Sprint 2026-06/07.
It is retained for provenance and audit traceability.

Current user-manual screenshot assets are maintained in `docs/user_manual/screenshots/`.

Each entry maps a screenshot file to its **business logic screen ID** (Blueprint SCR-xxx per docs/architecture/HMI_Architecture_Blueprint.md), GUI requirement ID, and the sprint issue that delivered or is developing the screen.

Captured: 2026-05-04 by BN from Streamlit app running at <http://localhost:8502>.

---

## Screen Inventory

### Delivered in Sprint 2026-06 (S06-07)

| File | Blueprint SCR | GUI Req | Sprint Issue | Status | Description |
|------|---------------|---------|--------------|--------|-------------|
| `scr_001_home_run_dashboard.png` | SCR-002 | GUI-003 | S06-07 | ✅ Delivered | Home / Run Dashboard — pipeline stage progress table and HITL gate status |
| `scr_002_role_selection.png` | SCR-005 (partial) | GUI-002 | S06-07 | ✅ Delivered | Role Selection — Author / Reviewer / Approver picker with role description cards |
| `scr_003_pipeline_configuration.png` | SCR-012/013 (partial) | GUI-012/013 | S06-07 | ⚠️ Partial | Pipeline Configuration — model provider/name, offline mode, stage selection, HITL settings; **Full Model Provider Selection (S07-02) and Connection Validation (S07-03) deferred** |
| `scr_004_input_entry_form.png` | SCR-001 | GUI-001 | S06-07 | ✅ Delivered | Input Entry Form — system name, file uploader, raw-text paste, Start Run button |

---

## Historical In-Development Snapshot (Sprint 2026-07)

| Blueprint SCR | Screen Name | GUI Req | Sprint Issue | Status | Development Notes |
|---------------|-------------|---------|--------------|--------|-------------------|
| SCR-003 | Stage Results Viewer | GUI-004 | S07-05 | ⏳ Active | Analyst inspection of stage outputs (Context Builder, STRIDE Scorer, Threat Generator) |
| SCR-004 | Threat and Mitigation Review | GUI-005 | S07-05 | ⏳ Active | Analyst review and approval of generated threats and mitigations |
| SCR-007 | Results Export | GUI-006 | S07-06 | ⏳ Active | Export canonical JSON, STIX 2.1, Mermaid diagram, markdown report |
| SCR-008 | Snapshot Export | GUI-007 | S07-06 | ⏳ Active | Save run context for later restoration |
| SCR-009 | Snapshot Restore | GUI-008 | S07-06 | ⏳ Active | Restore prior run from saved snapshot |
| SCR-010 | Agent Prompt Editor | GUI-009 | S07-04 | ⏳ Active | Per-agent prompt editing (advanced configuration for PromptEditor role) |
| SCR-011 | Prompt Version History | GUI-010 | S07-04 | ⏳ Active | Version history and rollback for agent prompts |
| SCR-012 | Model Provider Selection | GUI-012 | S07-02 | ⏳ Active | Provider dropdown with support for Local/Fixture, OpenAI, Anthropic, xAI, Azure, Ollama, Custom/Intranet |
| SCR-013 | Model Connection Details | GUI-013 | S07-02 | ⏳ Active | Connection string/URL input; editable for non-fixture providers |
| SCR-014 | Model Connection Validation | GUI-014 | S07-03 | ⏳ Active | Test model connection and guard Start Run with validation state |

---

## Capture and Update Instructions

### For Delivered Screens

1. Activate the virtual environment:

   ```
   .venv\Scripts\Activate.ps1
   ```
1. Launch the Streamlit app:

   ```
   streamlit run src/threat_modeler/ui/app.py
   ```
1. Navigate to the screen.
1. Take a full-window screenshot and save it with the filename listed in the table above.
1. Annotate each screenshot (arrows/labels) to highlight the key UI elements that satisfy the GUI requirement acceptance criteria.

### Current Capture Location

For current and release-facing documentation updates, capture screenshots under:

- `docs/user_manual/screenshots/`

Do not append new current-state screenshots to this historical folder unless capturing evidence for a historical rerun.

---

## Sprint Closeout Evidence Reference

**Sprint 2026-06 (S06-07) closed with the following evidence:**

- 4 screenshots (scr_001–scr_004) mapping to 4 delivered screens
- Test summary: 240 tests passing (unit + integration + E2E)
- Full test logs in `planning/archives/2026-05/Test_Execution_Summary_Sprint_2026_06.md`

**Sprint 2026-07 evidence was collected incrementally at the time of execution:**

- S07-02 screenshots added when Model Provider/Connection screens complete
- S07-05/06 screenshots added when Results/Export screens complete
- Final test and screenshot evidence compiled in `planning/archives/2026-05/Test_Execution_Summary_Sprint_2026_07.md`

## Archive Reference Policy

Historical screenshot evidence references must point to archived planning records under `planning/archives/`.

Do not add new links to retired root-level planning summary paths when equivalent records exist in `planning/archives/2026-05/`.

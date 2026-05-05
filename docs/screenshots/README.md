# Screenshot Evidence Index — Sprint 2026-06

This directory holds annotated screenshot evidence for the Streamlit HMI screens
delivered in Sprint 2026-06 (S06-07).  Each entry maps a screenshot file to its screen
inventory ID (SCR-xxx), GUI requirement ID, and the sprint issue that delivered the screen.

Captured: 2026-05-04 by BN from Streamlit app running at http://localhost:8502.

---

## Screen Inventory

| File | SCR ID | GUI Req ID | Sprint Issue | Description |
|------|--------|------------|--------------|-------------|
| `scr_001_home_run_dashboard.png` | SCR-001 (Blueprint SCR-002) | GUI-003 | S06-07 | Home / Run Dashboard — pipeline stage progress table and HITL gate status |
| `scr_002_role_selection.png` | SCR-002 (Blueprint —) | GUI-012 | S06-07 | Role Selection — Author / Reviewer / Approver picker with role description cards |
| `scr_003_pipeline_configuration.png` | SCR-003 (Blueprint SCR-012/013) | GUI-013 | S06-07 | Pipeline Configuration — model provider/name, offline mode, stage selection, HITL settings |
| `scr_004_input_entry_form.png` | SCR-004 (Blueprint SCR-001) | GUI-001 | S06-07 | Input Entry Form — system name, file uploader, raw-text paste, Start Run button |

---

## Capture Instructions

1. Activate the virtual environment:
   ```
   .venv\Scripts\Activate.ps1
   ```
2. Launch the Streamlit app:
   ```
   streamlit run src/threat_modeler/ui/app.py
   ```
3. Navigate to each screen listed above.
4. Take a full-window screenshot and save it to this directory using the filename
   listed in the table.
5. Annotate each screenshot (arrows/labels) to highlight the key UI elements that
   satisfy the GUI requirement acceptance criteria.

---

## Sprint Closeout Evidence Reference

The screenshots in this directory are referenced in the Sprint 2026-06 test execution
summary as visual acceptance criteria evidence for the following issues:

- **S06-07** (Streamlit App Shell) — SCR-001, SCR-002, SCR-003
- **S06-02** (HITL Gate Set 2 backend) — HITL gate screens pending S07 GUI delivery

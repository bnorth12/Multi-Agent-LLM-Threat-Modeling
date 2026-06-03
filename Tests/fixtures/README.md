# Test Fixtures

This directory contains test source material.

## Structure

- `inputs/systems/<system>/` — per-system fixture folders containing both ICD and narrative files together
- `inputs/hitl/` — HITL trigger rule configurations
- `expected_outputs/` — expected canonical graph fragments and output checks

## Authoritative Fixture Format

The authoritative input format for pipeline testing uses **two file types together**:

### 1. ICD Spreadsheet (CSV or XLSX)

Describes entities and interfaces. Each row has an `entity_type` column with one of:

| entity_type | Purpose |
|---|---|
| `subsystem` | Top-level subsystem node |
| `component` | Component belonging to a subsystem |
| `function` | Function belonging to a component |
| `interface` | Interface (data flow) between any two entity nodes |

CSV files use a flat single-sheet layout. XLSX files may use two sheets: `Entities` (subsystems, components, functions) and `Interfaces`.

Current fixtures:

- `inputs/systems/alpha/icd_alpha_v1.csv` — Alpha system, 7 entities + 5 interfaces
- `inputs/systems/bravo/icd_bravo_v2.csv` — Bravo system, minimal entities
- `inputs/systems/charlie/icd_charlie_v1.xlsx` — Charlie system, multi-sheet XLSX format
- `inputs/systems/uas_weapon_system/icd_uas_weapon_system_v1.csv` — UAS weapon system, full segment and lower-level coverage

### UAS Program Bundle Layout

For lifecycle alignment, UAS program-level fixtures now support two modes:

- **Early lifecycle top-level modeling:** use only
  - `inputs/systems/uas_weapon_system/icd_uas_weapon_system_v1.csv`
  - `inputs/systems/uas_weapon_system/description_uas_weapon_system.md`
- **Full UAS program modeling in one folder:** use
  - `inputs/systems/uas_weapon_system/full_system_bundle/`

The `full_system_bundle` folder contains top-level UAS files plus Alpha, Bravo, Charlie, and Ground Maintenance files so a single-folder upload can run the combined system threat model.

Additional mission-context pairs included in this fixture family:

- `inputs/systems/alpha/icd_alpha_mission_computer_v1.csv`
- `inputs/systems/alpha/description_alpha_mission_computer.md`
- `inputs/systems/charlie/icd_charlie_mission_planning_computer_v1.csv`
- `inputs/systems/charlie/description_charlie_mission_planning_computer.md`

### 2. Narrative Description (Markdown or plain text)

Describes the system, subsystems, and components in prose. Parsed separately by the narrative parser.

Current fixtures:

- `inputs/systems/alpha/description_alpha.md` — Alpha system narrative
- `inputs/systems/charlie/description_charlie.txt` — Charlie system narrative
- `inputs/systems/cav/description_cav.md` — Combined Charlie + Avionics markdown narrative for browser/live validation
- `inputs/systems/uas_weapon_system/description_uas_weapon_system.md` — UAS weapon system narrative with lower-level segment detail

## Fixture Naming Convention

- `{scenario}_{version}.{ext}` for ICD files (e.g., `icd_alpha_v1.csv`)
- `description_{scenario}.{ext}` for narratives
- Keep fixtures small and deterministic
- Each fixture must be parseable in isolation without external dependencies

## Manual Operator Input Guide

When testing the threat modeler **manually via the browser UI**, operators upload CSV ICD and Markdown description files through the file-selection controls. The following CSV/Markdown pairs are ready for manual testing:

| System | ICD File | Description File | Use Case |
|---|---|---|---|
| **UAS Weapon System** | `inputs/systems/uas_weapon_system/icd_uas_weapon_system_v1.csv` | `inputs/systems/uas_weapon_system/description_uas_weapon_system.md` | Full four-segment ISR system (recommended for comprehensive testing) |
| **UAS Weapon System (Single-Folder Bundle)** | `inputs/systems/uas_weapon_system/full_system_bundle/` | `inputs/systems/uas_weapon_system/full_system_bundle/` | Upload all ICD + narrative files from one folder for full combined-system run |
| **Alpha** | `inputs/systems/alpha/icd_alpha_v1.csv` | `inputs/systems/alpha/description_alpha.md` | Single platform segment |
| **Bravo** | `inputs/systems/bravo/icd_bravo_v2.csv` | `inputs/systems/bravo/description_bravo.md` | Ground processing segment |
| **Avionics** | `inputs/systems/avionics/icd_avionics_v1.csv` | `inputs/systems/avionics/description_avionics.md` | Legacy avionics system |
| **Threat Modeler** | `inputs/systems/threat_modeler/icd_threat_modeler_v1.csv` | `inputs/systems/threat_modeler/description_threat_modeler.md` | Example threat model input |

### Manual Testing Workflow

1. **Start the Streamlit UI:**
   ```bash
   streamlit run src/threat_modeler/ui/app.py
   ```

1. **In the browser UI**, navigate to the input upload panel.

1. **Select CSV ICD file** from the system folder under `Tests/fixtures/inputs/systems/`.

1. **Select Markdown description file** from the same system folder under `Tests/fixtures/inputs/systems/`.
   - **Pairing rule:** The scenario name in both filenames must match (e.g., `icd_uas_weapon_system_v1.csv` pairs with `description_uas_weapon_system.md`).

1. **Click Run** to execute the threat model generation pipeline.

1. **Review outputs** in the Run Dashboard and downloaded STIX/JSON artifacts.

### Fixture Selection Tips

- **First-time testers:** Start with **UAS Weapon System** (`icd_uas_weapon_system_v1.csv` + `description_uas_weapon_system.md`) for a complete multi-segment example.
- **Quick validation:** Use **Alpha** (`icd_alpha_v1.csv` + `description_alpha.md`) for faster threat model generation.
- **Legacy verification:** Use **Avionics** if testing backward compatibility with existing system models.

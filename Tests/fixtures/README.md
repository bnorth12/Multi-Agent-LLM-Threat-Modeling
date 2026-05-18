# Test Fixtures

This directory contains test source material.

## Structure

- `inputs/icd/` — ICD spreadsheet files (CSV and XLSX) describing system entities and interfaces
- `inputs/descriptions/` — narrative system description documents (Markdown and plain text)
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

- `inputs/icd/icd_alpha_v1.csv` — Alpha system, 7 entities + 5 interfaces
- `inputs/icd/icd_bravo_v2.csv` — Bravo system, minimal entities
- `inputs/icd/icd_charlie_v1.xlsx` — Charlie system, multi-sheet XLSX format
- `inputs/icd/icd_uas_weapon_system_v1.csv` — UAS weapon system, full segment and lower-level coverage

### 2. Narrative Description (Markdown or plain text)

Describes the system, subsystems, and components in prose. Parsed separately by the narrative parser.

Current fixtures:

- `inputs/descriptions/description_alpha.md` — Alpha system narrative
- `inputs/descriptions/description_charlie.txt` — Charlie system narrative
- `inputs/descriptions/description_cav.md` — Combined Charlie + Avionics markdown narrative for browser/live validation
- `inputs/descriptions/description_uas_weapon_system.md` — UAS weapon system narrative with lower-level segment detail

## Fixture Naming Convention

- `{scenario}_{version}.{ext}` for ICD files (e.g., `icd_alpha_v1.csv`)
- `description_{scenario}.{ext}` for narratives
- Keep fixtures small and deterministic
- Each fixture must be parseable in isolation without external dependencies

## Manual Operator Input Guide

When testing the threat modeler **manually via the browser UI**, operators upload CSV ICD and Markdown description files through the file-selection controls. The following CSV/Markdown pairs are ready for manual testing:

| System | ICD File | Description File | Use Case |
|---|---|---|---|
| **UAS Weapon System** | `icd_uas_weapon_system_v1.csv` | `description_uas_weapon_system.md` | Full four-segment ISR system (recommended for comprehensive testing) |
| **Alpha** | `icd_alpha_v1.csv` | `description_alpha.md` | Single platform segment |
| **Bravo** | `icd_bravo_v2.csv` | `description_bravo.md` | Ground processing segment |
| **Avionics** | `icd_avionics_v1.csv` | `description_avionics.md` | Legacy avionics system |
| **Threat Modeler** | `icd_threat_modeler_v1.csv` | `description_threat_modeler.md` | Example threat model input |

### Manual Testing Workflow

1. **Start the Streamlit UI:**
   ```bash
   streamlit run src/threat_modeler/ui/app.py
   ```

1. **In the browser UI**, navigate to the input upload panel.

1. **Select CSV ICD file** from `Tests/fixtures/inputs/icd/` directory.

1. **Select Markdown description file** from `Tests/fixtures/inputs/descriptions/` directory.
   - **Pairing rule:** The scenario name in both filenames must match (e.g., `icd_uas_weapon_system_v1.csv` pairs with `description_uas_weapon_system.md`).

1. **Click Run** to execute the threat model generation pipeline.

1. **Review outputs** in the Run Dashboard and downloaded STIX/JSON artifacts.

### Fixture Selection Tips

- **First-time testers:** Start with **UAS Weapon System** (`icd_uas_weapon_system_v1.csv` + `description_uas_weapon_system.md`) for a complete multi-segment example.
- **Quick validation:** Use **Alpha** (`icd_alpha_v1.csv` + `description_alpha.md`) for faster threat model generation.
- **Legacy verification:** Use **Avionics** if testing backward compatibility with existing system models.

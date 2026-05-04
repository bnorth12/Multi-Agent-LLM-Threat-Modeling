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

### 2. Narrative Description (Markdown or plain text)

Describes the system, subsystems, and components in prose. Parsed separately by the narrative parser.

Current fixtures:
- `inputs/descriptions/description_alpha.md` — Alpha system narrative
- `inputs/descriptions/description_charlie.txt` — Charlie system narrative

## Fixture Naming Convention

- `{scenario}_{version}.{ext}` for ICD files (e.g., `icd_alpha_v1.csv`)
- `description_{scenario}.{ext}` for narratives
- Keep fixtures small and deterministic
- Each fixture must be parseable in isolation without external dependencies

# Function Catalog

## Purpose

Provide a machine-readable list of canonical IDs assigned to all currently documented L1 and L2 functions.

## Machine-Readable Artifact

- `function_catalog.csv`

## Columns

- `function_id`
- `function_level`
- `l0_domain`
- `l1_code`
- `l1_name`
- `l2_index`
- `l2_name`
- `variant`
- `source_doc`

## ID Format

- L1: `L0ABBR.CODE.001`
- L2: `L0ABBR.CODE.1NN`

Where:

- `L0ABBR` is one of `AVI`, `NAV`, `COM`, `OPS`
- `CODE` is a stable L1 functional code
- `NN` is the L2 sequence index under the L1 function

## Governance Rule

- Interface producers and consumers must reference IDs from this catalog.
- New functional decomposition entries must update `function_catalog.csv` before interface additions are accepted.

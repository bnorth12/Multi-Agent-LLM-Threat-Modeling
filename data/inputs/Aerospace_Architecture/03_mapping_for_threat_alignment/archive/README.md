# Threat Alignment Archive Index

## Purpose

This folder stores historical analysis artifacts that are no longer active gate inputs but must be retained for auditability and provenance.

## How to Use

1. Move historical files into a dated folder: `YYYY-MM/`.
1. Add one entry in this index per moved file.
1. Keep canonical source-of-truth artifacts in the parent folder.

## Entry Template

- Original path:
- Archived path:
- Archive date:
- Reason:
- Replacement artifact:
- Regenerable: yes/no

## Archive Entries

- Original path: `data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/wave_A_to_E_execution_report.md`
	Archived path: `data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/archive/2026-05/wave_A_to_E_execution_report.md`
	Archive date: 2026-05-24
	Reason: Historical one-off execution report superseded by current canonical matrices and registers.
	Replacement artifact: canonical architecture mapping baselines in parent folder
	Regenerable: no
- Original path: `data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/cross_entrypoint_traceability_audit.md`
	Archived path: `data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/archive/2026-05/cross_entrypoint_traceability_audit.md`
	Archive date: 2026-05-24
	Reason: Historical audit snapshot retained for provenance; future reruns should be stored as dated snapshots.
	Replacement artifact: next dated cross-entrypoint audit snapshot
	Regenerable: yes

## Sweep Notes

- 2026-05-24 second governance report sweep recorded at `data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/archive/2026-05/second_governance_report_sweep.md`.
- Result: no additional low-risk one-off governance reports were moved because the remaining report-like markdown files are active governance or policy surfaces.

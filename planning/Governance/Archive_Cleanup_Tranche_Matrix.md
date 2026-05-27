# Archive Cleanup Tranche Checklist

## Purpose

Track manual archive-cleanup work as a working control artifact so each tranche names the responsible owner, blocking references, required evidence, and validation command before the next narrow enforcement zone is enabled.

## Status Legend

- `completed`: archive move and reference cleanup are finished and validated
- `blocked`: historical file is still referenced by active upstream materials and should remain in place for now
- `not_started`: tranche is identified but not yet cleaned

## Tranche Checklist

| Tranche | Status | Archive Zone | Archive Owner | Blocking References | Required Evidence | Validation Command |
|---|---|---|---|---|---|---|
| T-PLN-01 | completed | `planning/feature_branches/` Sprint 2026-05 historical branch docs | Documentation Owner | none after move; archived self-reference updated | `planning/archives/2026-05/feature_sprint_2026_05.md`; `planning/archives/2026-05/Sprint_2026_05_PR_Template.md`; `planning/archives/2026-05/s05_branch_metadata_cleanup_tranche_2026_05_24.md` | `python scripts/archive_hygiene.py check --paths planning/archives/2026-05/feature_sprint_2026_05.md planning/archives/2026-05/Sprint_2026_05_PR_Template.md --enforce` |
| T-PLN-02 | blocked | `planning/issues/` legacy Sprint 2026-05/06 tracker surfaces | Product Owner and Technical Lead | `planning/Sectioned_Implementation_Plan.md`; `planning/feature_branches/feature_sprint_2026_06.md` | decision note confirming tracker remains active until blockers are cleaned; updated tracker-reference inventory | `python scripts/archive_hygiene.py check --paths planning/issues/Sprint_2026_05_06_Issue_Tracker.md --enforce` |
| T-PLN-03 | completed | `planning/` older closeout checklists and branch-era sprint collateral | Scrum Master | none after retarget; archived documents now point to `planning/archives/2026-05/` | dated tranche note; archive index update; retargeted references | `python scripts/archive_hygiene.py check --paths planning/archives/2026-05/Sprint_2026_08_Closure_Checklist.md --enforce` |
| T-DOC-01 | completed | `docs/screenshots/` historical evidence references | Documentation Owner | none after retarget; screenshot index now references archive-managed planning evidence paths | updated screenshot evidence index and valid archive links; dated tranche note | `npx --yes markdownlint-cli docs/screenshots/README.md planning/archives/README.md planning/archives/2026-05/README.md` |
| T-THR-01 | not_started | `data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/` future dated evidence sweeps | Validation and Schema Engineer | active checklist and canonical matrix references must stay in place; only dated snapshots move | dated sweep note; archive index update; no broken canonical references | `python scripts/archive_hygiene.py check --paths data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/archive/2026-05/second_governance_report_sweep.md --enforce` |

## Working Rule

Complete one tranche at a time: move files, retarget blocking references, record evidence, validate, then enable the next narrow archive-hygiene zone only after the current tranche is clean.

## Current Decision

`planning/issues/Sprint_2026_05_06_Issue_Tracker.md` remains active for now because it still has upstream dependencies in `planning/Sectioned_Implementation_Plan.md` and `planning/feature_branches/feature_sprint_2026_06.md`.

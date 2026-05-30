# Contributing

Thank you for contributing to this project.

## Development Model

This repository uses a feature-branch workflow with issue-linked planning and checklist-based completion gates.

## Required Contribution Flow

1. Create or select a planning issue.
1. Create a feature branch linked to the issue.
1. Implement changes with requirement traceability.
1. Add or update tests.
1. Complete the feature branch checklist.
1. Open a pull request that references related issues.
1. Merge only after review and checklist completion.

## Governance Autoflow Requirement

Before opening or updating a pull request, run governance autoflow for your current phase:

- `python scripts/governance_autoflow.py --context pre-commit --sprint <SPRINT>`
- `python scripts/governance_autoflow.py --context pre-merge-commit --sprint <SPRINT>`
- `python scripts/governance_autoflow.py --context pre-push --sprint <SPRINT>`

For planning and closeout governance activities, use:

- `python scripts/governance_autoflow.py --context planning --sprint <SPRINT>`
- `python scripts/governance_autoflow.py --context closeout --sprint <SPRINT>`
- `python scripts/governance_autoflow.py --context portfolio --sprint <SPRINT>`

Autoflow design and routing matrix are documented in:

- `docs/process/Governance_Autoflow_Orchestration.md`
- `config/governance_autoflow_routing.json`

Planning and closeout operator commands:

- `./scripts/run_governance_planning.ps1 -Sprint <SPRINT>`
- `./scripts/run_governance_closeout.ps1 -Sprint <SPRINT>`
- `./scripts/run_governance_planning.sh <SPRINT>`
- `./scripts/run_governance_closeout.sh <SPRINT>`

## Sprint Identifier Policy

Use sprint identifiers as governed ordinals, not month numbers.

- Canonical repository token: `YYYY_NN`
- Human-readable prose alias: `YYYY-NN`
- Current scripts still use legacy `MM` variable names in places, but the suffix is semantically an ordinal sprint number
- Reserve `YYYY_99` for parking-lot or speculative work that must stay outside active remediation automation
- Completed legacy `YYYY-MM` and `YYYY_MM` sprint artifacts are accepted as historical records and should not be renumbered just for policy conformance
- Governance automation accepts both two-digit and three-digit ordinal inputs so future expansion does not require emergency parser changes

Before creating or renaming sprint artifacts, read `docs/process/Sprint_Naming_Governance.md`.

## Testing The Agent Skill Structure

When changes touch `.github/agents/`, `.github/skills/`, governance routing, or the runner scripts that execute governance stages, validate the structure in three layers:

1. Syntax and import sanity
	- Run `python -m py_compile scripts/governance_autoflow.py scripts/run_remediation_readiness.py scripts/run_kpi_drift_analysis.py scripts/run_sprint_closeout_certification.py scripts/run_multi_sprint_portfolio_planning.py`.

1. Routed execution behavior
	- Run the relevant governance autoflow context for the change, such as `python scripts/governance_autoflow.py --context pre-commit --sprint <SPRINT>` or `--context closeout` / `--context portfolio` when those routes are affected.
	- Confirm the expected commands write artifacts into `independent_reviews/latest/`.

1. Documentation and evidence checks
	- Update `docs/process/Governance_Autoflow_Orchestration.md` whenever routing or stage behavior changes.
	- Update `README.md` when the governance agent/skill structure or repository layout changes.
	- Update this file when contribution steps or validation expectations change.
	- Run `npx --yes markdownlint-cli **/*.md` on touched markdown files.

## Branch Naming

Recommended format:

- feature short description
- fix short description
- docs short description

Use issue IDs in branch names when practical.

## Pull Request Requirements

Each pull request should include:

- Linked issue IDs
- Summary of requirement IDs addressed
- Verification evidence summary
- Test results
- Any follow-up tasks

## Python Standards

- Use Python for runtime implementation.
- Prefer typed functions and dataclasses or Pydantic models for contracts.
- Keep modules focused and testable.
- Add tests for new behavior and bug fixes.

## Documentation Standards

- Keep requirements in the formal requirement record format.
- Update affected README files when directory purpose changes.
- Keep interface and traceability docs in sync with implementation.
- Preserve canonical architecture baselines and archive historical analysis artifacts instead of deleting by default.

Markdown quality gate:

- Follow docs/process/Markdown_Style_Guide.md for markdown authoring rules.
- Run markdownlint and resolve issues in files changed by the branch.
- Avoid introducing any new markdownlint errors.

## Required Validation Gates for Architecture Mapping Changes

If a branch changes files under `data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/`, run:

- `python scripts/validate_cross_domain_exception_policy.py`
- `python scripts/validate_cross_domain_exception_policy.py --proposal-only --propose-missing --proposal-out test_reports/cross_domain_exception_proposals.csv`

These checks are part of CI and local pre-push hook enforcement.

If historical analysis files are superseded, archive them under:

- `data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/archive/`

Record archive metadata in the archive index and follow the policy document:

- `data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/ARTIFACT_RETENTION_AND_ARCHIVE_POLICY.md`

## Archive Hygiene for Historical Governance Evidence

If a branch moves or updates historical planning, sprint-closeout, or one-off governance evidence, run:

- `python scripts/archive_hygiene.py check --paths <changed files>`

Use the scaffold helper to create a dated batch note and reminder checklist:

- `python scripts/archive_hygiene.py scaffold --archive-root planning/archives --batch YYYY-MM --note-name archive_sweep_note.md --title "Planning Archive Sweep"`
- `python scripts/archive_hygiene.py scaffold --archive-root data/inputs/Aerospace_Architecture/03_mapping_for_threat_alignment/archive --batch YYYY-MM --note-name archive_sweep_note.md --title "Threat Alignment Archive Sweep"`

Local hooks and CI now enforce archive hygiene on staged changes, merge commits, upstream push diffs, and pull-request diffs.

## Release and Checklist References

- See Requirements/07_Release_Process.md for release workflow.
- See Requirements/08_Feature_Branch_Checklist_Template.md for required branch checklist.

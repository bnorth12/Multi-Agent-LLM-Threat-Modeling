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

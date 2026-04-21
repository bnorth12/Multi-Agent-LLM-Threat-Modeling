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

Markdown quality gate:

- Follow docs/process/Markdown_Style_Guide.md for markdown authoring rules.
- Run markdownlint and resolve issues in files changed by the branch.
- Avoid introducing any new markdownlint errors.

## Release and Checklist References

- See Requirements/07_Release_Process.md for release workflow.
- See Requirements/08_Feature_Branch_Checklist_Template.md for required branch checklist.

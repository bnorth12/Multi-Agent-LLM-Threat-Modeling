# Release Process

## 1. Purpose

Define a repeatable release workflow that requires completed feature branch checklists and synchronized issue and pull request state.

## 2. Release Stages

1. Plan Release Scope

- Collect candidate features from planned issues.
- Confirm each candidate feature has a dedicated branch and owner.

1. Validate Branch Readiness

- Confirm each feature branch has a completed checklist artifact.
- Confirm branch PR references related planning issue IDs.

1. Integrate and Verify

- Merge approved feature branches.
- Execute integration tests and release validation checks.

1. Conduct Release Readiness Review

- Review checklist completion status for all included branches.
- Review unresolved issues, known risks, and mitigation plans.

1. Publish Release

- Tag release.
- Publish release notes with linked issues and merged PRs.
- Archive release checklist bundle.

## 3. Required Entry Criteria for Release Candidate

- Every included feature branch has a merged PR.
- Every merged PR references one or more planning issues.
- Every included feature branch has a completed checklist artifact.
- Required verification outcomes are passed or approved with waivers.

## 4. Required Exit Criteria for Release

- Release tag created.
- Release notes published.
- Issues synchronized to released state.
- Checklist bundle archived with release artifacts.

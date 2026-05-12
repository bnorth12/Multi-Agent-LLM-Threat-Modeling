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
- Component semantic version manifest is generated and reviewed.
- Component file version inventory is generated and mapped to component versions.
- RC validation approach is documented as manual-gated for the candidate when automation is excluded.

## 4. Required Exit Criteria for Release

- Release tag created.
- Release notes published.
- Issues synchronized to released state.
- Checklist bundle archived with release artifacts.
- Component semantic version manifest archived with release artifacts.
- Component file version inventory archived with release artifacts.

## 5. Version Governance Requirements

- Component versioning SHALL use semantic version format `major.minor.patch`.
- File version identifiers SHALL be deterministic and reproducible from source control state (for example: commit SHA + path fingerprint).
- Release notes SHALL declare component versions changed since the previous release.
- RC approval board SHALL reject release candidates that do not include both component and file-level version artifacts.

## 6. Candidate Validation Mode

- Release candidates MAY use manual validation gating when declared by sprint release plan.
- When manual validation gating is active, automated tests are informational-only and SHALL NOT be release-blocking for that candidate.
- Manual validation evidence SHALL be archived with release artifacts and linked in the release decision record.

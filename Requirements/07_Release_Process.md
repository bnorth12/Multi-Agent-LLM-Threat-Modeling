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
- Release-candidate merge verification report retained in-repo and linked from SVD (or equivalent verification index).

## 5. Version Governance Requirements

- Component versioning SHALL use semantic version format `major.minor.patch`.
- File version identifiers SHALL be deterministic and reproducible from source control state (for example: commit SHA + path fingerprint).
- Release notes SHALL declare component versions changed since the previous release.
- RC approval board SHALL reject release candidates that do not include both component and file-level version artifacts.

## 6. Candidate Validation Mode

- Release candidates MAY use manual validation gating when declared by sprint release plan.
- When manual validation gating is active, automated tests are informational-only and SHALL NOT be release-blocking for that candidate.
- Manual validation evidence SHALL be archived with release artifacts and linked in the release decision record.

## 7. Release-Candidate Merge Verification Report (Required)

For every release-candidate merge, a verification report SHALL be generated and committed to the repository.

### 7.1 Required Report Content

- Requirement coverage table that lists every in-scope requirement ID.
- For each requirement, artifact evidence links that back verification claims.
- Type-aware verification artifact mapping (for example: tests for functional, governance artifacts for policy, design+analysis artifacts for design constraints).
- Traceability matrices used for the candidate decision.
- Coverage summary and explicit list of any waivers or deferred items.

### 7.2 Retention and Publication Boundary

- The release-candidate merge verification report SHALL be retained in-repo as a controlled governance artifact.
- The report SHALL NOT be packaged as a published release deliverable by default.
- Release notes MAY reference the report path, but the report itself remains repository-retained evidence.

### 7.3 SVD Reference Rule

- The SVD (or equivalent verification authority document) SHALL reference the in-repo report path and commit context.
- SVD references MUST be stable and specific enough to recover the exact evidence set used for release-candidate merge approval.

### 7.4 Recommended Location and Naming

- Recommended path: `planning/release_validation/`
- Recommended filename: `Release_Candidate_Merge_Verification_<version>.md`

Use the repository template when available:

- `planning/release_validation/Release_Candidate_Merge_Verification_Template.md`

Release-candidate merge evidence remains repository-retained unless explicitly promoted.

<!-- End of release process policy -->

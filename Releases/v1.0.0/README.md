# v1.0.0 Release Candidate (Deployment Package)

Purpose: provide a deployment-ready release payload containing runtime code and end-user/operator instructions only.

## Included Folders

- `code_snapshot/`
  - Runtime application code and runtime dependency manifests.
  - Frontend deployable build output in `frontend/dist/`.

- `documentation/`
  - `User_Manual_v1.0.0.md`
  - `User_Manual_v1.0.0.html`
  - `Deployment_Guide_v1.0.0.md`
  - `Release_Notes_v1.0.0.md`

## Exclusion Rule

This package excludes developer workflow assets and governance/test-evidence payloads that are not required to deploy and operate the application.

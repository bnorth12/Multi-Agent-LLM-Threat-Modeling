# Deployment Guide: v1.0.0 Release Candidate

## 1. Purpose

This guide defines deployment steps for the v1.0.0 release-candidate package, including installation, configuration, validation, and rollback.

## 2. Release Candidate Policy

- The release candidate uses a **two-stage validation gate**.
- Stage 1: deployment smoke validation must pass before manual campaign starts.
- Stage 2: manual operator validation campaign is release-gating after automated pass.

## 3. Deployment Preconditions

- Access to release artifacts:
  - `code_snapshot/`
  - `documentation/User_Manual_v1.0.0.md`
  - `documentation/User_Manual_v1.0.0.html`
  - `documentation/Deployment_Guide_v1.0.0.md`
  - `documentation/Release_Notes_v1.0.0.md`
- Environment prerequisites:
  - Python 3.11+
  - OS: Windows, Linux, or macOS
  - Network access for configured live LLM provider (if live mode is used)

## 4. Artifact Integrity Validation

1. Verify the required folders/files above are present in the release package.
1. Confirm version-locked documentation names under `documentation/`.
1. Confirm frontend deployable assets are present under `code_snapshot/frontend/dist/`.

## 5. Installation Procedure

### 5.1 Prepare Python Environment

```powershell
cd code_snapshot
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 5.2 Launch Runtime

```powershell
python -m threat_modeler --host 127.0.0.1 --port 8600
```

## 6. Runtime Configuration

1. Set provider configuration (fixture or live).
1. For live mode, configure endpoint/model and credentials.
1. Validate connection from configuration screen before run.

## 7. Manual RC Validation Checklist

Automated entry gate (must pass before checklist execution):

- [x] Run deployment smoke validation from this release candidate package:

```powershell
.venv\Scripts\python.exe -m threat_modeler --host 127.0.0.1 --port 8600
```

- [x] Latest result: startup and endpoint health verified before manual RC walkthrough.

The following checks are release-gating for this release candidate:

- [ ] App starts successfully.
- [ ] Full 9-stage run completes in target environment.
- [ ] All 7 HITL gates are actionable and resume works.
- [ ] Results Export provides STIX, canonical graph, Mermaid, report, and token usage artifacts.
- [ ] S09 viewer features render correctly (STIX, canonical, Mermaid, STRIDE).
- [ ] STRIDE standalone export works.
- [ ] Quick Preview controls function.
- [ ] Component semantic version manifest is present and correct.
- [ ] Component-file version inventory is present and mapped to components.
- [ ] User manual and deployment guide are accessible in release bundle.
- [ ] User manual markdown and HTML instructions are validated against product behavior.
- [ ] Product documentation used for release operations is reviewed for consistency (requirements, process docs, release notes).
- [ ] Deployment guide walkthrough is executed start-to-finish in a clean environment.

Execution reference:

- Perform step-by-step operator validation using this checklist and `User_Manual_v1.0.0.md`.
- Record step outcomes as `PASS`, `FAIL`, or `BLOCK` and attach release-candidate evidence artifacts.

Validation loop target:

- Complete RC validation in 1-2 defect-fix loops.
- If more than 2 loops are required, pause publication and run release readiness escalation.

## 8. Operational Handoff Notes

- Record deployment date/time, environment, and operator.
- Record any known issues and accepted risks.
- Archive manual validation evidence with release decision record.

## 9. Rollback Procedure

1. Stop running service/process.
1. Reinstall prior stable version package.
1. Restore prior configuration snapshot.
1. Re-run smoke validation (start + one pipeline run + artifact export).
1. Log rollback reason and impacted scope.

## 10. Post-Deployment Monitoring

- Monitor startup errors and provider connection failures.
- Review pipeline completion rate and gate progression behavior.
- Track user-reported issues during RC feedback window.

## 11. Ownership and Sign-off

- Deployment Owner: Release Manager
- Validation Owner: QA Lead (manual validation)
- Technical Sign-off: Technical Lead

---

**Document Owner**: Release Manager
**Last Updated**: 2026-05-27
**Status**: Active release-candidate deployment guide.

# Deployment Guide: v1.0.0-rc1

## 1. Purpose

This guide defines deployment steps for Release Candidate 1 (v1.0.0-rc1), including installation, configuration, validation, and rollback.

## 2. RC1 Release Policy

- RC1 uses **manual validation gating**.
- Automated test execution is **not required** for RC1 release approval.
- If automated tests are run, results are informational evidence only.

## 3. Deployment Preconditions

- Access to release artifacts:
  - `threat-modeler-1.0.0rc1-py3-none-any.whl`
  - `threat-modeler-1.0.0rc1.tar.gz`
  - `USER_MANUAL.md`
  - `DEPLOYMENT_GUIDE.md`
  - `RELEASE_NOTES.md`
  - `SHA256SUMS.txt`
- Environment prerequisites:
  - Python 3.11+
  - OS: Windows, Linux, or macOS
  - Network access for configured live LLM provider (if live mode is used)

## 4. Artifact Integrity Validation

1. Verify checksums from `SHA256SUMS.txt`.
2. Confirm artifact names and versions match `v1.0.0-rc1`.
3. Confirm component semantic version manifest and component-file version inventory are present in release evidence bundle.

## 5. Installation Procedure

### 5.1 Install from Wheel

```powershell
pip install threat-modeler-1.0.0rc1-py3-none-any.whl
```

### 5.2 Install from Source Archive

```powershell
pip install threat-modeler-1.0.0rc1.tar.gz
```

### 5.3 Verify Installed Version

```powershell
python -c "import threat_modeler; print(getattr(threat_modeler, '__version__', 'unknown'))"
```

Expected output: `1.0.0-rc1` (or equivalent rc version string used in package metadata).

## 6. Runtime Configuration

1. Set provider configuration (fixture or live).
2. For live mode, configure endpoint/model and credentials.
3. Validate connection from configuration screen before run.

## 7. Manual RC Validation Checklist

The following checks are release-gating for RC1:

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

- Perform step-by-step test execution using `Tests/Test_Plan.md`, Section `6. Manual RC Test Cases` (TC-RC-001 through TC-RC-011).
- Record step outcomes as `PASS`, `FAIL`, or `BLOCK` and attach evidence artifacts per case instructions.

Validation loop target:

- Complete RC validation in 1-2 defect-fix loops.
- If more than 2 loops are required, pause publication and run release readiness escalation.

## 8. Operational Handoff Notes

- Record deployment date/time, environment, and operator.
- Record any known issues and accepted risks.
- Archive manual validation evidence with release decision record.

## 9. Rollback Procedure

1. Stop running service/process.
2. Reinstall prior stable version package.
3. Restore prior configuration snapshot.
4. Re-run smoke validation (start + one pipeline run + artifact export).
5. Log rollback reason and impacted scope.

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
**Last Updated**: 2026-05-09
**Status**: Draft for S09 completion

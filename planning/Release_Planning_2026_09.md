# Release Planning: v1.0.0-RC1 (Post-S09)

## 1. Release Objectives

### Primary Goals
- Deliver Release Candidate 1 (v1.0.0-rc1) with complete UI viewer suite
- Validate all 9-stage pipeline with new artifact viewers
- Establish production-ready documentation and quality standards
- Publish a deployment guide with release-specific installation and operations steps
- Enable community feedback collection before GA release

### Timeline Target
- **S09 Feature Completion**: May 22, 2026
- **RC1 QA & Documentation**: May 23-27, 2026
- **RC1 Release**: May 28, 2026
- **RC Feedback Window**: May 28 - June 3, 2026
- **GA Release v1.0.0**: June 4, 2026

## 1.1 S09 Requirements and Implementation Document Control

During S09 Requirements Phase and S09 Implementation Phase, the release team SHALL treat the following as living controlled documents and update them whenever scope, acceptance criteria, or test evidence expectations change:

- `Requirements/10_GUI_Requirements.md`
- `Requirements/01_Project_Requirements.md`
- `Requirements/05_Verification_Strategy.md`
- `Requirements/07_Release_Process.md`
- `Tests/Test_Plan.md`
- `planning/Sprint_2026_09_Traceability_Matrix.md`
- `planning/issues/Sprint_2026_09_Issue_Tracker.md`
- `Releases/Deployment_Guide_v1.0.0-rc1.md`

S09 baseline requirements/features that must remain in scope tracking:

- GUI-018 through GUI-025
- PRJ-021 and PRJ-022
- VS-008

## 2. RC1 Readiness Criteria

### ✅ Feature Completeness (from S09)
- [ ] GUI-018: STIX Threat Model Viewer (fully functional in Results Export)
- [ ] GUI-019: Canonical Graph Viewer (fully functional in Results Export)
- [ ] GUI-020: Mermaid Diagram Viewer (fully functional in Results Export)
- [ ] GUI-021: STRIDE Threat Model Viewer & Export (with standalone artifact)
- [ ] GUI-022/023: Quick Preview defect fixed and verified
- [ ] GUI-025: Markdown Viewer and Editor functional for tool-managed markdown files

**Acceptance**: All S09 GUI features functional end-to-end with live LLM execution

### ✅ User Documentation Updates
- [ ] [docs/User_Manual.md](docs/User_Manual.md) updated with all new screens
- [ ] Workflow diagrams updated to show new export/viewer options
- [ ] Screenshots captured for all 9 result screens
- [ ] Troubleshooting section enhanced for preview/export features
- [ ] HTML user manual regenerated and validated
- [ ] Deployment guide drafted and finalized at [Releases/Deployment_Guide_v1.0.0-rc1.md](Releases/Deployment_Guide_v1.0.0-rc1.md)

**Acceptance**: Complete walkthrough of new features documented with screenshots

### ✅ Quality Gate Requirements
- [ ] Manual RC validation checklist executed and attached as release evidence
- [ ] No critical bugs in manual regression validation
- [ ] `verify_sprint_traceability.py --audit --closure` passes for S09
- [ ] All 7 HITL gates validated with new viewers in active
- [ ] Artifact generation verified for STIX, canonical graph, Mermaid, STRIDE
- [ ] Documentation validation completed for user manual, product documentation set, and deployment guide

**Acceptance**: Zero critical bugs, manual validation evidence complete, traceability closure gate passes

### ✅ RC1 Automation Policy
- [ ] RC1 candidate sign-off confirms test automation is excluded from release gating
- [ ] Manual validation evidence bundle archived with release artifacts
- [ ] Any automated test output collected is marked informational-only and not release-blocking
- [ ] Manual RC validation campaign completed within bounded defect-fix iterations (target <= 2 validation loops)

**Acceptance**: RC1 decision record explicitly documents manual-only release gating

### ✅ Governance & Traceability
- [ ] S09 Sprint closure checklist complete
- [ ] All 5 feature issues linked to GUI requirements
- [ ] All 3 deferred issues tagged with S09 disposition
- [ ] Test evidence captured and linked (min: 1 per feature)
- [ ] Smoke run evidence with full pipeline completion

**Acceptance**: Traceability matrix audit passes with no gaps

### ✅ Versioning & Release Artifacts
- [ ] Version bumped to 1.0.0-rc1 in all config files:
  - `pyproject.toml` (version field)
  - `src/threat_modeler/__init__.py` (__version__)
  - GitHub Release tag: `v1.0.0-rc1`
- [ ] Release notes generated from S09 commits
- [ ] CHANGELOG.md created with feature summary
- [ ] Download artifacts packaged and checksummed

**Acceptance**: Version consistent across all sources, artifacts ready for distribution

## 3. User Manual Update Plan

### Documentation Structure (Post-S09)
```
docs/User_Manual.md (top-level guide)
├── 1. Introduction & Quick Start
├── 2. Configuration & Provider Setup
├── 3. Pipeline Overview (9 stages + 7 HITL gates)
├── 4. Input Entry Screen
├── 5. Threat Review Screen (HITL Gate Workflow)
├── 6. Results Export Screen
│   ├── 6.1 STIX Threat Model Viewer [NEW]
│   ├── 6.2 Canonical Graph Viewer [NEW]
│   ├── 6.3 Mermaid Diagram Viewer [NEW]
│   ├── 6.4 STRIDE Threat Model Viewer [NEW]
│   ├── 6.5 Standalone Artifact Export [NEW]
│   └── 6.6 Markdown Viewer and Editor [NEW]
├── 7. Last Prompt & Token Usage Screens
├── 8. Troubleshooting, Quick Preview, and Markdown Editing [UPDATED]
└── 9. Advanced Configuration

docs/user_manual/screenshots/ (new)
├── scr_001_dashboard_hitl_paused.png
├── scr_003_configuration_validated.png
├── scr_005_threat_review_hitl.png
├── scr_006_results_export_populated.png
├── scr_007_stix_viewer.png [NEW]
├── scr_008_canonical_graph_viewer.png [NEW]
├── scr_009_mermaid_diagram_viewer.png [NEW]
├── scr_010_stride_viewer.png [NEW]
└── scr_011_quick_preview_fixed.png [NEW]
```

### Regeneration Process
1. Capture 4 new viewer screenshots during S09 feature implementation
2. Update User_Manual.md with viewer interaction steps and use cases
3. Add section on artifact interpretation (STIX, canonical graph structure, etc.)
4. Regenerate HTML version via markdown-to-html tool
5. Validate all images and links in HTML output

## 4. Quality Assurance Checklist (Pre-RC1)

### Functional Testing
- [ ] All 9 pipeline stages complete successfully with live LLM
- [ ] All 7 HITL gates functional (approve/reject/resume actions)
- [ ] New viewers render artifacts without errors
- [ ] Export functionality generates valid STIX/Mermaid/CSV artifacts
- [ ] Quick Preview controls responsive and non-blocking
- [ ] Browser reload preserves run state across all screens

### Regression Testing
- [ ] Manual regression walkthrough completed for all S09 acceptance criteria
- [ ] Manual bug triage completed for all open RC1 blockers
- [ ] Optional automated checks (if run) recorded as informational evidence
- [ ] Full manual release candidate validation completed and signed off

### Documentation Validation
- [ ] User Manual renders correctly in browser (HTML)
- [ ] All code examples execute without errors
- [ ] All links (internal and external) valid
- [ ] Screenshots display with correct aspect ratios
- [ ] Product documentation set reviewed for release consistency (Requirements, process docs, and release notes)
- [ ] Deployment guide walkthrough executed end-to-end in a clean environment

## 4.1 Manual RC Validation Campaign (No Automation Gate)

RC1 SHALL run a complete manual validation campaign to prove release functionality without automation gating.

Required campaign scope:

1. Full end-to-end run validation (input, all 9 stages, all 7 HITL gates, and exports).
2. UI validation for S09 features (STIX, canonical graph, Mermaid, STRIDE viewer, STRIDE export, quick preview).
3. Documentation validation for:
  - User Manual markdown and HTML.
  - Product documentation used for release operations (requirements/process/release docs).
  - Deployment guide operational walkthrough.
4. Evidence bundle generation with screenshots/logs and pass-fail matrix.

Iteration policy:

- Target no more than 2 defect-fix validation loops before RC publication.
- If a third loop is required, escalate to release readiness review before publish decision.

## 4.2 Run Snapshot Strategy (S09 Execution)

To simplify restart and recovery during long live runs, save snapshots at the following checkpoints:

1. Post-configuration validation (before first run start).
2. First HITL pause reached (baseline gate-state checkpoint).
3. Mid-pipeline after at least one resume cycle.
4. Pre-export completion state (all stages complete, before final export checks).

Snapshot use policy:

- Use snapshots for controlled restart at known-good stages when execution is interrupted.
- Reference snapshot IDs in test execution notes and issue investigations.
- If a blocking defect is found after a snapshot, log issue and requirement impact before resuming from checkpoint.

### Deployment Validation
- [ ] Docker build successful (if applicable)
- [ ] Installation via pip succeeds
- [ ] Runtime dependencies complete and documented
- [ ] Configuration files have sensible defaults

## 5. Release Notes Template (S09 Summary)

```markdown
# v1.0.0-rc1 Release Notes

## What's New in RC1

### 🎨 UI Artifact Viewers (S09 Feature Complete)
- **STIX Threat Model Viewer**: Interactive visualization of STIX 2.1 bundle objects
- **Canonical Graph Viewer**: Navigable threat model dependency graph
- **Mermaid Diagram Viewer**: In-app rendering of threat flow and architecture diagrams
- **STRIDE Threat Model Viewer**: Dedicated STRIDE threat analysis export

### ✨ Export Enhancements
- Standalone STRIDE export artifact (CSV/JSON formats)
- Quick Preview controls fully functional and responsive
- Artifact format validation on export

### 🔧 Stability Improvements
- Runtime stability hardening (resume idempotency, gate state management)
- Session state persistence across browser reload
- HITL gate action validation and duplicate prevention

### 📚 Documentation
- Updated User Manual with complete viewer workflows
- New screenshots for all result screens
- Enhanced troubleshooting and quick start guides

## Known Limitations

- Quick Preview is read-only (no editing of exported artifacts)
- Canonical graph viewer optimized for graphs < 500 nodes
- STRIDE export currently supports CSV and JSON; XML planned for v1.1

## Testing & Validation

- 109+ unit/integration tests passing
- Full 9-stage pipeline validated with live LLM (xAI/Grok)
- E2E artifact generation verified
- Community feedback collection: May 28 - June 3

## Installation & Upgrade

See [Installation Guide](docs/README.md) for setup instructions.

## Feedback & Support

- Report issues: https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues
- Discussion: https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/discussions
- RC Feedback Window: Closes June 3, 2026
```

## 6. Governance Checklist

### Release Authority
- [ ] All S09 issues closed and verified
- [ ] Traceability matrix audit passes
- [ ] No open critical or high-severity bugs
- [ ] Sprint closure checklist signed off

### Communication
- [ ] Release notes published to GitHub Releases
- [ ] Release announcement posted (if applicable)
- [ ] Community notified of feedback collection window
- [ ] RC download links tested and validated

### Versioning
- [ ] Git tag created: `git tag -a v1.0.0-rc1 -m "Release Candidate 1: UI Viewer Suite Complete"`
- [ ] Version numbers updated across codebase
- [ ] Commit log reviewed for release notes accuracy

## 7. Post-RC1 Feedback Integration (Before GA)

### Feedback Categories
1. **Critical Bugs** (block GA)
2. **UX Issues** (viewer interaction, export workflows)
3. **Documentation Gaps** (missing or unclear instructions)
4. **Feature Requests** (deferred to v1.1 roadmap)

### RC Feedback Resolution
- Weekly triage meetings (May 28, 30, June 2)
- Critical bugs fixed and validated by June 3
- UX/doc feedback incorporated into v1.0.0 GA build
- Feature requests documented for future roadmap

### GA Release Preparation
- Merge all RC feedback fixes to main branch
- Final regression test run (109+ tests)
- Tag GA release: `v1.0.0` (no -rc suffix)
- Publish GitHub Release with final notes

## 8. Release Artifacts

### Deliverables for v1.0.0-rc1
```
releases/v1.0.0-rc1/
├── threat-modeler-1.0.0rc1-py3-none-any.whl
├── threat-modeler-1.0.0rc1.tar.gz
├── RELEASE_NOTES.md
├── USER_MANUAL.md (snapshot)
├── DEPLOYMENT_GUIDE.md
├── INSTALLATION_GUIDE.md
├── CHANGELOG.md
└── SHA256SUMS.txt
```

### Quality Metadata
- Build timestamp and commit SHA
- Test coverage report (if applicable)
- Dependency manifest (pinned versions)

## 9. Success Criteria for RC1

✅ **RC1 is successful if:**
1. All 5 new viewers functional with live LLM execution
2. Zero critical bugs in regression testing
3. Documentation complete and validated
4. Traceability audit passes
5. Community feedback mechanism active
6. Artifact generation verified for all formats
7. Browser compatibility confirmed (Chrome, Firefox, Safari)

## 10. Timeline & Milestones

| Date | Milestone | Owner | Status |
|------|-----------|-------|--------|
| May 22 | S09 Feature Complete | Dev Team | Not Started |
| May 23 | Release Documentation Prep | Tech Writer | Not Started |
| May 24 | QA Testing & Bug Fix | QA Lead | Not Started |
| May 25 | User Manual Finalization | Tech Writer | Not Started |
| May 26 | Final Regression Testing | QA Lead | Not Started |
| May 27 | RC1 Build & Artifacts | DevOps | Not Started |
| May 28 | RC1 Published | Release Manager | Not Started |
| June 3 | RC Feedback Window Closes | Project Manager | Not Started |
| June 4 | GA v1.0.0 Released | Release Manager | Not Started |

---

**Document Owner**: Release Manager
**Last Updated**: 2026-05-09
**Status**: Draft (Activated at S09 Kickoff)

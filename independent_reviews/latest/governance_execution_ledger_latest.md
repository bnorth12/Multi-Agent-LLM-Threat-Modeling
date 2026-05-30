# Governance Execution Ledger (Latest)

- Timestamp: 2026-05-30T15:12:23
- Context: pre-commit
- Branch: main
- Policy Profile: strict
- Enforcement Mode: off
- Outcome: warning
- Exit Code: 0
- Open Remediation Obligations: None

## Remediation Obligations
- Open obligation count: None
- Obligation report (Markdown): n/a
- Obligation report (JSON): n/a
- Notes: Obligation report is only generated for pre-push independent review runs.

## Agent Chain
- repo-governance-autoflow-orchestrator
- requirements-baseline-steward
- architecture-design-change-author
- architecture-design-traceability-auditor
- requirements-implementation-auditor
- architecture-contract-enforcer

## Skill Chain
- requirements-baseline-steward
- architecture-design-change-author
- architecture-design-traceability-auditor
- requirements-implementation-auditor
- architecture-contract-enforcer

## Agent Stage Results
- 1. repo-governance-autoflow-orchestrator | status=success | mode=direct | duration=0.000s
  note: Context router executed locally before stage dispatch.
- 2. requirements-baseline-steward | status=failed | mode=direct | duration=0.487s
  note: Executed via sprint traceability verification.
- 3. architecture-design-change-author | status=success | mode=direct | duration=0.313s
  note: Executed via architecture/design authoring workpack generator.
- 4. architecture-design-traceability-auditor | status=failed | mode=direct | duration=0.487s
  note: Executed via sprint traceability verification.
- 5. requirements-implementation-auditor | status=failed | mode=direct | duration=0.487s
  note: Executed via sprint traceability verification.
- 6. architecture-contract-enforcer | status=success | mode=direct | duration=0.322s
  note: Executed via dependency boundary guard.

## Skill Stage Results
- 1. requirements-baseline-steward | status=failed | mode=direct | duration=0.487s
  note: Executed via sprint traceability verification.
- 2. architecture-design-change-author | status=success | mode=direct | duration=0.313s
  note: Executed via architecture/design authoring workpack generator.
- 3. architecture-design-traceability-auditor | status=failed | mode=direct | duration=0.487s
  note: Executed via sprint traceability verification.
- 4. requirements-implementation-auditor | status=failed | mode=direct | duration=0.487s
  note: Executed via sprint traceability verification.
- 5. architecture-contract-enforcer | status=success | mode=direct | duration=0.322s
  note: Executed via dependency boundary guard.

## Commands
- [1] key=traceability status=failed exit=1 duration=0.487s stages=agent:requirements-baseline-steward, agent:architecture-design-traceability-auditor, agent:requirements-implementation-auditor, skill:requirements-baseline-steward, skill:architecture-design-traceability-auditor, skill:requirements-implementation-auditor :: C:\Users\brian\OneDrive\Documents\GitHubRepos\Multi Agent Threat Modeler\.venv\Scripts\python.exe C:\Users\brian\OneDrive\Documents\GitHubRepos\Multi Agent Threat Modeler\scripts\verify_sprint_traceability.py --sprint 2026_12
- [2] key=architecture-design-authoring status=success exit=0 duration=0.313s stages=agent:architecture-design-change-author, skill:architecture-design-change-author :: C:\Users\brian\OneDrive\Documents\GitHubRepos\Multi Agent Threat Modeler\.venv\Scripts\python.exe C:\Users\brian\OneDrive\Documents\GitHubRepos\Multi Agent Threat Modeler\scripts\run_architecture_design_authoring.py --sprint 2026_12 --out-dir independent_reviews/latest
- [3] key=dependency-boundary status=success exit=0 duration=0.322s stages=agent:architecture-contract-enforcer, skill:architecture-contract-enforcer :: C:\Users\brian\OneDrive\Documents\GitHubRepos\Multi Agent Threat Modeler\.venv\Scripts\python.exe C:\Users\brian\OneDrive\Documents\GitHubRepos\Multi Agent Threat Modeler\scripts\verify_dependency_boundary.py

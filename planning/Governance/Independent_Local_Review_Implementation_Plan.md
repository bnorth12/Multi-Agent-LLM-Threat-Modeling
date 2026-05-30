# Independent Local Review Implementation Plan

Status: In Progress (Phase 7 scaffolding and backfill implementation started)
Owner: Repository governance
Date: 2026-05-29

## Objective
Establish an independent, local-first review system that is decoupled from development agents and GitHub-hosted compliance checks while preserving repository governance traceability.

## Scope
1. Full-scope review coverage:
- Repository structure integrity
- Requirements to implementation linkage
- Requirements to verification linkage
- Requirements to architecture/design traceability
- Features/issues without requirements
- Requirements without implementation or verification
- Local sprint issue and GitHub-link governance quality (from local tracker artifacts)

2. Execution modes:
- On-demand local execution
- Automatic local execution at commit, merge-commit, and pre-push hooks

3. Output policy:
- Reports generated to local-only ignored directories
- No runtime application behavior changes required for report generation

## Managed TODO
- [x] Define independent review architecture and guardrails
- [x] Create specialized in-repo agents under .github/agents
- [x] Create specialized in-repo skills under .github/skills
- [x] Implement local review engine: scripts/independent_repo_review.py
- [x] Add local-only report directory and ignore policy
- [x] Integrate review script into local git hooks
- [x] Execute pilot run and generate initial baseline report
- [x] Calibrate requirement-ID parsing and tracker-table parsing to reduce false positives
- [x] Add severity taxonomy (critical/major/minor/info) and policy thresholds
- [x] Add branch-aware review metadata (current branch, merge base, ahead/behind)
- [x] Add optional GitHub API status sync mode (explicit opt-in only)
- [x] Add trend snapshots (score deltas over time)

## Phase Deliverables

### Phase 1 (Completed)
- .github/agents/independent-review-orchestrator.agent.md
- .github/agents/requirements-implementation-auditor.agent.md
- .github/agents/architecture-design-traceability-auditor.agent.md
- .github/skills/independent-repo-review/SKILL.md
- .github/skills/issue-governance-review/SKILL.md
- scripts/independent_repo_review.py
- local_reviews/README.md
- Hook integration in .githooks/pre-commit, .githooks/pre-merge-commit, .githooks/pre-push

### Phase 2 (Implemented)
- Requirement-ID extraction constrained by known requirement prefix patterns and component-ID structure
- Issue tracker parsing is markdown-table header aware; requirement linkage checks only apply to tables with a Related Requirements column
- Severity policy thresholds implemented with critical/major/minor/informational finding buckets
- Branch-awareness implemented: current branch, HEAD, merge-base with origin/main, ahead/behind, working-tree dirtiness, merge-risk classification

### Phase 3 (Implemented)
- Architecture/design conceptual-vs-as-built split reporting
- Local trend snapshot history and score/severity deltas across runs
- Optional local GitHub issue reconciliation mode (`--github-reconcile`) using `gh` CLI

### Phase 4 (Implemented)
- Configurable severity mapping policy file (repo-governed profile sets)
- Compact trend dashboard window (last N runs with directional indicators)
- Concept maturity tags for planned features (concept, design-ready, implementation-ready)

### Phase 5 (Implemented/In Progress)
- Profile-specific enforcement behavior presets implemented via checked-in profile `enforce_on` lists
- Hook behavior now follows selected profile automatically (default profile is warning-only; strict profile blocks on major/critical)

### Phase 6 (Implemented)
- Optional branch-pattern based policy selection (strict on main and release/* via shared resolver helper)
- Remediation readiness section with health-based trigger floor
- Primary readiness metric standardized as health
- Compact report lifecycle (stable latest, timestamped history archive)
- Dedicated source-to-evidence traceability skill and specialist auditor

### Phase 7 (Implemented/In Progress)
- One-time historical KPI backfill implemented via `scripts/backfill_independent_review_history.py`
- Over-time scoreboard outputs added:
	- `local_reviews/latest/kpi_trend_scoreboard_backfill.md`
	- `local_reviews/latest/kpi_trend_scoreboard_backfill.json`
	- `local_reviews/latest/independent_review_backfill_over_time.md`
- Governance autoflow orchestration scaffolded:
	- `scripts/governance_autoflow.py`
	- `docs/process/Governance_Autoflow_Orchestration.md`
- Extended governance agent and skill scaffold added under `.github/agents/` and `.github/skills/`

### Phase 8 (Next)
- Wire governance autoflow script directly into hook and planning/closeout operator runbooks
- Route newly scaffolded specialist skills through `repo-governance-autoflow-orchestrator`
- Add profile-compiled route overrides and quality checks for policy routing completeness
- Add explicit architecture/design and requirements-implementation iteration stages so the review can distinguish design fit, implementation fit, and end-of-chain traceability

## Runbook

### On-demand
```bash
python scripts/independent_repo_review.py --sprint 2026_12 --run-context manual --report-mode update --out-dir local_reviews/latest
```

### Profile-based blocking mode
```bash
python scripts/independent_repo_review.py --sprint 2026_12 --run-context manual --report-mode update --policy-profile strict --enforcement-mode auto
```

### Manual enforcement mode
```bash
python scripts/independent_repo_review.py --sprint 2026_12 --run-context manual --report-mode update --enforcement-mode manual --enforce-on critical,major
```

### Threshold policy overrides
```bash
python scripts/independent_repo_review.py \
	--sprint 2026_12 \
	--req-impl-threshold 0.75 \
	--req-verify-threshold 0.70 \
	--req-arch-threshold 0.75 \
	--issue-quality-threshold 0.95 \
	--max-planned-missing-requirement 0
```

### Opt-in GitHub reconciliation (local only)
```bash
python scripts/independent_repo_review.py \
	--sprint 2026_12 \
	--github-reconcile \
	--github-repo bnorth12/Multi-Agent-LLM-Threat-Modeling
```

Notes:
- This mode is disabled by default.
- It requires local `gh` CLI availability and authentication.
- The review still runs if reconciliation cannot complete; unresolved items are reported.

### Hook toggles
- INDEPENDENT_REVIEW_SPRINT=YYYY_MM
- INDEPENDENT_REVIEW_PROFILE=default|strict|advisory
- INDEPENDENT_REVIEW_HOOK_FAIL_MODE=profile|warn

### One-time Backfill Runbook
```bash
python scripts/backfill_independent_review_history.py --branch main --sprint 2026_12 --policy-profile strict --replay-timeout-seconds 120
```

### Governance Autoflow Runbook
```bash
python scripts/governance_autoflow.py --context pre-push --sprint 2026_12
```

## Current Baseline
Pilot run generated:
- local_reviews/latest/independent_review_2026-12_20260529_145900.md
- local_reviews/latest/independent_review_2026-12_20260529_145900.json

Phase 2 baseline generated:
- local_reviews/latest/independent_review_2026-12_20260529_150953.md
- local_reviews/latest/independent_review_2026-12_20260529_150953.json

Latest score: 54.3%

Latest Phase 3 report includes:
- branch-awareness merge risk block
- conceptual vs as-built architecture/design gap classification
- trend snapshot and deltas vs prior run
- optional GitHub reconciliation summary block

Latest Phase 4 additions include:
- checked-in policy profile config: `config/independent_review_policy_profiles.json`
- profile selection via `--policy-profile`
- compact trend dashboard section using `--trend-window`
- maturity-tagged conceptual classifications in conceptual vs as-built section

Latest enforcement preset additions include:
- profile enforcement presets from config (`enforce_on`)
- script support for `--enforcement-mode auto|off|manual`
- hooks now pass `--enforcement-mode auto` and selected profile by default

## Governance Note
This system is intentionally local-first and independent from GitHub-hosted workflow checks. Future remote integration, if desired, should be opt-in and documented as a separate control path.

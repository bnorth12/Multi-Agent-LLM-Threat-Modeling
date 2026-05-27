# GitHub Actions Reliability Checklist

Date: 2026-05-26
Scope: CI and governance workflow reliability hardening
Status: Active

## 1. Workflow Inventory and Current Health

| Workflow | Reliability State | Blocking Scope | Current Action |
|---|---|---|---|
| CI | Mixed to stabilizing | Required for code quality | Live lane made non-blocking; non-live remains quality gate |
| Sprint Traceability Enforcement | Unstable historical, now reduced push strictness | Governance check | PR strict, push advisory audit |
| Copilot cloud agent | Stable | Non-blocking | Monitor only |
| Copilot code review | Stable | Non-blocking | Monitor only |
| Dependency Graph | Stable | Non-blocking | Monitor only |

## 2. Reliability Guardrails

1. Branch trigger policy

- CI visibility branches: main, dev, feature/**.
- PR quality gate branch target: main.

1. Blocking policy

- Non-live test lanes are blocking quality signal.
- Live LLM lane is non-blocking operational signal.
- Traceability is strict on pull requests and advisory on push to main.

1. Runtime platform policy

- Force JavaScript actions to Node 24 runtime in workflow environment.
- Upgrade pinned GitHub actions to supported major versions.

1. Secrets and live-test policy

- Live lane runs only on main push or explicit workflow_dispatch opt-in.
- Live lane depends on GROK_API and must not gate merge readiness.

## 3. Deferred Minor Findings Register (Approved)

These are acceptable for defer to next sprint when documented and linked.

| Finding ID | Finding | Severity | Defer Decision | Required Next-Sprint Action |
|---|---|---|---|---|
| ACT-2026-05-001 | Add workflow-level concurrency cancel-in-progress for CI and traceability | Minor | Deferred | Implement in Sprint 2026-13 workflow hardening tranche |
| ACT-2026-05-002 | Add path-based short-circuit to skip full fan-out for docs-only deltas | Minor | Deferred | Add conditional execution matrix and document exemptions |
| ACT-2026-05-003 | Publish failure taxonomy runbook linked from workflow summaries | Minor | Deferred | Add governance runbook and owner routing map |
| ACT-2026-05-004 | Split live lane into dedicated workflow file (scheduled + manual) | Minor | Deferred | Extract job from CI into dedicated live-lane workflow |

## 4. Required Evidence for Deferred Findings

For each deferred finding, record all:

- rationale for defer
- risk statement and expected blast radius
- verification impact statement
- target sprint and target close date
- named owner

## 5. Immediate Verification Checklist

Run after each workflow change:

1. Validate YAML syntax and GitHub Actions rendering.

1. Trigger CI on feature branch and verify:

- non-live lanes run and gate status is enforced
- live lane is skipped unless configured

1. Trigger workflow_dispatch with run_live=true and verify live lane executes without gating failure.

1. Open PR to main and verify Sprint Traceability Enforcement remains strict and blocking for governance defects.

1. Push to main and verify traceability uses advisory audit behavior without hard failure from non-critical governance gaps.

## 6. Exit Criteria

Checklist complete when:

- CI non-live quality gates are green on active branches.
- Live-lane failures no longer fail overall CI workflow status.
- Traceability workflow failures are limited to pull-request governance violations.
- All deferred findings are logged with owner and next-sprint linkage.

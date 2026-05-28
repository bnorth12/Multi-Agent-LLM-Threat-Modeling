# Multi Agent Threat Modeler - Deployment Code Snapshot

This folder is the deployment-focused runtime snapshot for v1.0.0.

## Included

- `src/` - backend runtime source code
- `requirements.txt` - Python runtime dependencies
- `pyproject.toml` - package/runtime metadata
- `frontend/dist/` - deployable frontend build artifacts

## Runtime Startup (Backend)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m threat_modeler
```

Optional custom bind settings:

```powershell
python -m threat_modeler --host 0.0.0.0 --port 9000
```

## Frontend Deployment Notes

- Deploy static assets from `frontend/dist/` using your preferred static web server.
- Configure reverse proxy/API routing so frontend calls target the backend API endpoint.

## Operator Documentation

Use the release documentation folder for deployment and user guidance:

- `../documentation/Deployment_Guide_v1.0.0.md`
- `../documentation/User_Manual_v1.0.0.md`
- `../documentation/User_Manual_v1.0.0.html`

# Proposal-only remediation output for missing exception rows
python scripts/validate_cross_domain_exception_policy.py --proposal-only --propose-missing --proposal-out test_reports/cross_domain_exception_proposals.csv

# Dependency boundary hardening (release/runtime must exclude test-only deps)
python scripts/verify_dependency_boundary.py

# E2E browser tests (requires GROK_API environment variable)
python scripts/run_and_log.py scripts/live_browser_e2e_smoke.py
```

### Sprint 2026-12 Live Test Policy

- Live test execution is standardized to Grok-only in this repository for Sprint 2026-12.
- Required credential for live lanes: `GROK_API` (or `GROK_API_KEY` where supported by script wrappers).
- OpenAI-live execution is excluded by default and is not required for sprint validation in this environment.
- Default CI-safe lane remains:

```bash
python -m pytest Tests/ -q -m "not llm_live and not llm_live_browser"
```

- Approved live validation lane (Grok only):

```bash
python -m pytest Tests/e2e/test_live_llm_validation.py -v -m llm_live -s
```

### Test Organization

- **Unit tests** → `Tests/unit/` — Fast validation of core functions
- **Integration tests** → `Tests/integration/` — Multi-module orchestration tests
- **E2E tests** → `Tests/e2e/` — Full pipeline from input to artifact export
- **Test fixtures** → `Tests/fixtures/` — Sample inputs and expected outputs
- **Test reports** → `Tests/test_reports/YYYY-MM-DD/[test_type]/` — Logs organized by date and type

### Test Infrastructure

- **`scripts/run_and_log.py`** — Universal test runner with UTF-8 logging and environment validation
- **`scripts/set_test_env.ps1`** — Environment setup (PYTHONIOENCODING, browser flags, GROK_API check)
- **`Tests/requirements_e2e.txt`** — Consolidated test dependencies
- **`Tests/conftest.py`** — Pytest configuration and fixtures
- **`Tests/pytest.ini`** — Pytest test discovery and behavior settings

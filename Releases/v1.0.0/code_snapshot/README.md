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

## Scope Boundary

This code snapshot is deployment-focused. Test harnesses, developer-only scripts,
and sprint validation assets are intentionally excluded from this package.

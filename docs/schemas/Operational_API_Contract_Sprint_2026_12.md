# Operational API Contract (Sprint 2026-12)

## Purpose
Defines the REST contract used by the React + MUI frontend for control flow and data flow integration with the Python operational backend.

## Base
- Default host: `127.0.0.1`
- Default port: `8600`
- Content type: `application/json`

## Authentication (S12 staged readiness)
- Default mode: auth disabled (`THREAT_MODELER_AUTH_REQUIRED` not set or false-like)
- Enable auth gate: set `THREAT_MODELER_AUTH_REQUIRED=1`
- Optional strict token match: set `THREAT_MODELER_AUTH_TOKEN=<token>`
  - When set, backend requires `Authorization: Bearer <token>` match on all non-health routes
  - When not set, backend still requires a non-empty bearer token while auth gate is enabled
- Health endpoint (`GET /health`) remains unauthenticated for availability probing

## Health
- `GET /health`
  - Response: `{ "status": "ok" }`

## Execution Plan
- `GET /execution/plan`
  - Response: `{ "plan": { ... } }`
- `POST /execution/plan`
  - Request: `{ "settings": RuntimeSettingsLike }`
  - Response: `{ "plan": { ... } }`

## Runtime Config
- `GET /config`
  - Response: `{ "config": RuntimeSettings }`
- `POST /config`
  - Request: `{ "config": RuntimeSettingsLike }` or inline RuntimeSettingsLike payload
  - Response: `{ "config": RuntimeSettings }`

## Prompts
- `GET /prompts`
  - Response: `{ "prompts": { "agent_01": { "prompt", "expected_output", "temperature", "is_modified" }, ... } }`
- `GET /prompts/{agent_id}`
  - Response: `{ "agent_id", "prompt", "default_prompt", "expected_output", "temperature", "is_modified", "history": [...] }`
- `POST /prompts/{agent_id}`
  - Request fields (optional): `prompt`, `expected_output`, `temperature`
  - Response: `{ "agent_id", "prompt", "expected_output", "temperature" }`

## Runs
- `GET /runs`
  - Response: `{ "runs": [RunEntry, ...] }`
- `POST /runs`
  - Request: `{ "run_id"?, "settings"?, "initial_state"? }`
  - Response: `{ "run_id", "status_url" }`
- `GET /runs/{run_id}`
  - Response: `{ "run": RunEntry }`
- `POST /runs/{run_id}/cancel`
  - Response: `{ "run_id", "cancelled": bool }`
- `DELETE /runs/{run_id}`
  - Response: `{ "run_id", "cancelled": bool }`
- `POST /runs/{run_id}/resume`
  - Request: `{ "gate_id": str, "settings"?, "pipeline_state"? }`
  - Response: `{ "run_id", "resumed_from_gate" }`

## Artifacts
- `GET /runs/{run_id}/artifacts/canonical`
  - Response: `{ "artifact": "canonical", "content": { ... } }`
- `GET /runs/{run_id}/artifacts/stix`
  - Response: `{ "artifact": "stix", "content": { ... } }`
- `GET /runs/{run_id}/artifacts/mermaid`
  - Response: `{ "artifact": "mermaid", "content": { ... } }`
- `GET /runs/{run_id}/artifacts/report`
  - Response: `{ "artifact": "report", "content": "..." }`

## Error Contract
- Unknown route: `404 { "error": "Unknown route: ..." }`
- Unknown run ID: `404 { "error": "Unknown run_id: ..." }`
- Invalid payload fields: `400 { "error": "..." }`
- Cancel conflict: `409 { "run_id": "...", "cancelled": false }`
- Unauthorized request (auth gate enabled): `401 { "error": "Unauthorized", "details": "..." }`

## Notes
- GraphQL endpoint is planned but not implemented in this sprint increment.
- Contract currently prioritizes REST for rapid frontend integration and Playwright test adaptation.

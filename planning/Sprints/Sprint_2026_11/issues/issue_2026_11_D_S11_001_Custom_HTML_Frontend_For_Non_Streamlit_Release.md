# Issue: D-S11-001 — Custom HTML Frontend for Non-Streamlit Release

**Sprint**: 2026-11
**Type**: Feature / Architecture
**Status**: Proposed
**Priority**: High
**Owner**: TBD
**Estimated Effort**: XL (8–12 sprints for full implementation)

---

## Problem Statement

The current web UI is built with Streamlit, which is a development/prototyping framework. For a fielded release, we need:

1. **No Streamlit dependency** in the production binary (reduces package size and complexity).
2. **Custom UI** that maintains feature parity with the current Streamlit experience.
3. **Decoupled frontend-backend** so the operational API in `src/threat_modeler/server/api.py` becomes the single source of truth for runtime control.
4. **Automated test coverage** for the frontend-backend contract.

---

## Proposed Solution

### Architecture

```
┌─────────────────────────────────────────────┐
│     HTML/CSS/JavaScript Frontend            │
│  (Single-Page App, served from /public/)   │
│   - No Streamlit dependency                │
│   - React or vanilla JS                    │
└────────────────┬──────────────────────────┘
                 │ REST/JSON API calls
                 ↓
┌─────────────────────────────────────────────┐
│  Operational Python Backend Server          │
│  (src/threat_modeler/server/api.py)        │
│   - HTTP endpoints for runs, config, plans │
│   - No GUI framework dependency             │
│   - Hosted on port 8600 (or configurable)  │
└─────────────────────────────────────────────┘
```

### Frontend Technology Choices

**Option A: Vanilla JavaScript + HTML/CSS**
- **Pros**: Minimal dependencies, lightweight, no build step.
- **Cons**: More boilerplate for state management and routing.
- **Use case**: Simple dashboards, form-based UI.

**Option B: React (via CDN or bundled)**
- **Pros**: Component-based, familiar tooling, large ecosystem.
- **Cons**: Larger bundle, build step required.
- **Use case**: Complex workflows, real-time state updates.

**Option C: Vue.js**
- **Pros**: Simpler learning curve than React, good for incremental adoption.
- **Cons**: Smaller community than React.
- **Use case**: Middle ground between vanilla and React.

**Recommendation**: Start with **vanilla JS** for MVP; migrate to **React** or **Vue** if complexity grows.

---

## Scope of Work

### Phase 1: Backend API Expansion (2 weeks)

- [ ] Audit `src/threat_modeler/server/api.py` for completeness.
  - Current endpoints: `/health`, `/execution/plan`, `/runs/{run_id}`, POST `/runs`.
  - Missing: POST `/runs/{run_id}/resume`, DELETE `/runs/{run_id}` (cancel), GET `/config`, POST `/config`, GET `/prompts`, POST `/prompts/{agent_id}`.
- [ ] Add endpoints for:
  - Configuration state (model, pipeline settings).
  - Prompt editing and retrieval per agent.
  - Run history and filtering.
  - HITL gate state and gate decision submission.
  - Export artifact download (STIX, Mermaid, report, canonical).

### Phase 2: Frontend Scaffold (3 weeks)

- [ ] Create directory structure:
  ```
  src/threat_modeler/ui/frontend/
    ├── index.html
    ├── css/
    │   ├── theme.css
    │   └── components.css
    ├── js/
    │   ├── app.js
    │   ├── api-client.js
    │   ├── state.js
    │   └── components/
    │       ├── home.js
    │       ├── config.js
    │       ├── input-entry.js
    │       ├── results.js
    │       └── ...
    └── assets/
        └── (icons, images)
  ```
- [ ] Build HTML scaffold with navigation sidebar, page routing.
- [ ] Implement API client library (fetch wrappers, error handling).
- [ ] Implement state management (session storage or in-memory store).

### Phase 3: Feature Parity Pages (4–6 weeks)

Migrate each Streamlit screen to HTML:

1. **Home** — Dashboard, quick-start, status badge.
2. **Role Selection** — Role picker.
3. **Pipeline Configuration** — Model + stage selection UI.
4. **Input Entry** — File upload, raw text, config display.
5. **Stage Results** — Progress, stage output preview.
6. **Threat Review** — Threats table, filtering, editing.
7. **STIX Viewer** — STIX bundle JSON viewer.
8. **Canonical Graph Viewer** — Graph visualization (use D3.js or similar).
9. **Mermaid Viewer** — Diagram rendering.
10. **STRIDE Viewer** — Threat scoring table.
11. **Token Usage** — Token metrics table.
12. **Last Prompt** — Prompt history and diff.
13. **Results Export** — Download links, preview toggles.
14. **Snapshot Manager** — Snapshot CRUD.
15. **Markdown Viewer** — Markdown rendering.
16. **Prompt Editor** — Per-agent prompt and expected output editing.

### Phase 4: Automated Test Suite (2–3 weeks)

- [ ] Set up Selenium/Playwright tests for frontend.
- [ ] Test suite organization:
  ```
  Tests/e2e/
    ├── test_html_frontend_smoke.py    # Basic page loads, navigation
    ├── test_html_frontend_config.py   # Config form submission
    ├── test_html_frontend_run.py      # Full run workflow
    ├── test_html_frontend_prompts.py  # Prompt editor flows
    └── fixtures/
        └── html_server.py             # Backend server fixture
  ```
- [ ] Test coverage:
  - Page loads without errors.
  - Form submission and API calls succeed.
  - Error states display correctly (network errors, validation errors).
  - HITL gate flow (pause, resume, reject).
  - Export artifact download.
  - Theme persistence.

### Phase 5: Deployment & Documentation (2 weeks)

- [ ] Update deployment guide to include frontend serving instructions.
- [ ] Add frontend build/install steps (if using bundler).
- [ ] Create admin guide for self-hosting the HTML frontend.
- [ ] Archive Streamlit-based UI docs (mark as development-only).

---

## Backend API Contract

The frontend will communicate with endpoints in `src/threat_modeler/server/api.py`. Current and proposed endpoints:

### Existing

```
GET    /health                           → { "status": "ok" }
GET    /execution/plan                   → { "plan": {...} }
GET    /runs/{run_id}                    → { "run": {...} }
POST   /runs                             → { "run_id": "..." }
```

### Proposed

```
GET    /config                           → { "config": {...} }
POST   /config                           → { "config": {...} }
GET    /prompts                          → { "prompts": {...} }
GET    /prompts/{agent_id}               → { "prompt": "...", "expected_output": "..." }
POST   /prompts/{agent_id}               → { "success": true }
GET    /runs                             → { "runs": [...] }
POST   /runs/{run_id}/resume             → { "run_id": "..." }
DELETE /runs/{run_id}                    → { "status": "cancelled" }
POST   /runs/{run_id}/gate-decision      → { "status": "resumed|rejected" }
GET    /runs/{run_id}/artifacts/stix     → (binary/JSON)
GET    /runs/{run_id}/artifacts/mermaid  → (markdown)
GET    /runs/{run_id}/artifacts/report   → (markdown)
GET    /runs/{run_id}/artifacts/canonical → (JSON)
```

---

## Testing Strategy

### Unit Tests

- Frontend component logic (state updates, rendering logic).
- API client error handling and retry logic.

### Integration Tests

- Frontend + backend API contract (mock backend if needed).
- Form submission → API call → state update → UI re-render.

### E2E Tests

- Live backend + HTML frontend.
- Full workflow: config → input → run → review → export.
- HITL gate pause/resume/reject flows.
- Error recovery (network timeout, 500 errors, etc.).

### Automated Test Tools

- **Selenium** (existing in codebase via e2e tests) for browser automation.
- **Playwright** (alternative to Selenium).
- **PyTest** for orchestration (existing).
- **Mock/fixture backend server** for isolated frontend testing.

---

## Browser Integration with VS Code Agent

Yes, the deployed HTML frontend can be opened in the VS Code integrated browser:

1. Start the backend server: `python -m threat_modeler --port 8600`
2. Backend serves HTML from `src/threat_modeler/ui/frontend/index.html` at `http://localhost:8600/` or `/ui/`.
3. VS Code browser tool opens `http://localhost:8600/` and interacts with the page.
4. Agent can validate UI state, submit forms, verify error messages, etc.

---

## Deployment Packaging

### Release Artifacts

```
threat-modeler-1.0.0-py3-none-any.whl
├── threat_modeler/
│   ├── server/
│   ├── backend/
│   ├── agents/
│   ├── ui/
│   │   └── frontend/        ← NEW: Static HTML/CSS/JS
│   │       ├── index.html
│   │       ├── css/
│   │       └── js/
│   └── __main__.py
└── (other modules)
```

**No Streamlit dependency** in the release wheel (it's already absent from `requirements.txt`).

---

## Dependencies & Tooling

### Frontend Dependencies (Optional, if using framework)

- **React** (if Option B): Only dev dependency; built bundle included in wheel.
- **D3.js** (optional, for graph visualization): Lightweight, already used in some threat-modeler projects.
- **Markdown-it** (optional, for markdown rendering): Lightweight renderer.

### Backend (No new dependencies)

- Existing: `openai`, `langgraph`, `stix2`, `python-dotenv`, `chromadb`.

---

## Success Criteria

- [ ] Backend API fully supports frontend operations without Streamlit.
- [ ] HTML frontend achieves feature parity with Streamlit UI (all 16 screens functional).
- [ ] E2E test coverage ≥ 80% for critical paths (config, run, HITL, export).
- [ ] Deployment guide includes HTML frontend setup and self-hosting instructions.
- [ ] Deployed release wheel includes HTML frontend; Streamlit dependency is optional/removed.
- [ ] Browser automation tests pass (Playwright/Selenium) on Windows, Linux, macOS.

---

## Acceptance Criteria

1. Deployed release starts with `python -m threat_modeler` and serves HTML at `http://localhost:8600/`.
2. All 16 UI screens render correctly without browser console errors.
3. Full workflow (config → input → run → HITL gates → export) works end-to-end.
4. Automated e2e tests validate at least 3 critical paths (quick run, HITL pause/resume, export).
5. Documentation is updated; no references to Streamlit for operational deployment.

---

## Open Questions

1. **Graph visualization library**: D3.js? Cytoscape? Sigma.js? (Depends on complexity of canonical graph rendering.)
2. **State persistence**: Should frontend state persist to localStorage? Session storage? Backend?
3. **Theme system**: Replicate Streamlit's dark/default themes, or simplify to CSS variables?
4. **Real-time updates**: WebSocket or long-polling for run status? Or simple polling?
5. **Browser support**: IE11+? Modern browsers only (Chrome, Firefox, Safari)?

---

## References

- Operational API: `src/threat_modeler/server/api.py`
- Current Streamlit UI: `src/threat_modeler/ui/app.py`
- E2E test fixture: `Tests/conftest.py`
- Deployment guide: `Releases/Deployment_Guide_v1.0.0-rc1.md`

---

## Related Issues

- **D-S11-002**: Backend API completeness audit.
- **D-S11-003**: Frontend component library (forms, tables, modals).
- **D-S11-004**: Automated e2e test suite for HTML frontend.
- **D-S11-005**: Deployment documentation updates.

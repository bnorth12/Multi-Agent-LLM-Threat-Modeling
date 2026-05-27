## Dependency Management

- Review and document all new dependencies (frontend and backend)
- Add new test/dev dependencies to separate files (e.g., requirements-dev.txt, package.json devDependencies)
- Ensure production/release builds exclude test-only dependencies
- Update build and CI/CD scripts to enforce separation

# Sprint 2026-12 Planning: Web Interface & API Enablement

## Key Tasks

### 1. Expose Backend Endpoints
- Expose REST/GraphQL endpoints for all data and control needs
- Ensure endpoints cover all required GUI functions (data display, control actions, status, etc.)
- Implement authentication/authorization as needed

### 2. Document API Contracts
- Document all API endpoints (OpenAPI/Swagger for REST, schema for GraphQL)
- Define request/response payloads, error codes, and authentication flows
- Share API documentation with frontend team for integration

### 3. Frontend Integration (React + MUI)
- Consume backend endpoints from React app
- Implement data and control flow wiring

### 4. Automated Testing
- Adapt/rewrite Playwright scripts for new frontend and API
- Add/expand tests for new endpoints and UI flows

---

_This plan ensures the new web interface is fully integrated with the backend and testable from day one._

## Proposed GUI Framework

- **Framework:** React + MUI (Material UI)
- **Layout:**
	- Top frame: navigation and status
	- Left frame: detailed navigation
	- Main (right) frame: primary content/pages
	- Bottom (thin) frame: status bar/footer with stage/HITL status (graphical)
- **Theming:**
	- Dark mode: blue/black
	- Light mode: blue/white
	- Blue for borders and background accents
- **Features:**
	- Responsive (CSS Grid/Flexbox)
	- Accessible (keyboard, ARIA, color contrast)
	- Notification area for errors/warnings
	- User/session info in top bar (if needed)
	- Contextual help (optional)
	- Loading/busy states in main and footer
	- Easy theme switching (CSS variables)
- **Testing:**
	- Playwright for E2E/browser automation
	- Jest/React Testing Library for unit/integration
	- Tests to be adapted/recreated for new UI

## Decision Record (Approved)

- **Auth (Sprint 12):** implemented as staged runtime readiness with optional backend enforcement and frontend bearer token support.
- **GraphQL:** deferred to Sprint 13; Sprint 12 is REST-first.
- **Frontend hosting:** separate frontend dev server/runtime integration (no forced static backend hosting in Sprint 12).
- **HITL UX:** controls are exposed in both footer quick actions and page workflows.

## Rebaseline Update (2026-05-19)

- Sprint 12 scope is rebaselined to include full conversion from test-tool-driven UI workflow to standalone HTML framework workflow.
- Sprint 12 now includes all of the following as in-scope and completed:
	- Standalone React + MUI operational GUI shell.
	- Full page workflow actions: run submission, prompt editing, config save, artifact load path.
	- Browser full-workflow lane implementation and passing evidence.
- Sprint 13 should prioritize refactor and GraphQL implementation only; full HTML conversion is no longer deferred.

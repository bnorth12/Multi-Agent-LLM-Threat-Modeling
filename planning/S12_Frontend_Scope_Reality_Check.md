# Sprint 2026-12: HTML Frontend Scope Reality Check

**Date**: 2026-05-19
**Status**: Critical scope gap discovered during validation

---

## Executive Summary

The React+MUI HTML frontend built in S12 is **a basic navigation shell only**—it cannot replicate the Streamlit HMI's threat modeling functionality. The current setup cannot display or interact with:

- Execution stages and HITL gates
- Threat data and mitigation reviews
- LLM interactions and token tracking
- Any actual threat modeling workflow

**Root Cause**: Backend REST API is incomplete. It exposes basic CRUD operations but NOT the detailed state required for threat modeling HMI.

---

## What the Original Streamlit HMI Provides

### 1. Full Threat Modeling Workflow (10-20 minute execution)

**Execution Stages** (9 sequential agents):
- Stage 01: Input Normalizer
- Stage 02: Context Builder
- Stage 03: Trust Boundary Validator
- Stage 04: STRIDE Scorer
- Stage 05: Threat Generator
- Stage 06: STIX Packager
- Stage 07: Mitigation Generator
- Stage 08: Diagram Generator
- Stage 09: Report Writer

**Per-Stage Data Available in Streamlit:**
- Execution messages and context
- LLM prompts, attempts, token usage
- Current stage status (running, complete, pending)
- Timestamp and duration

### 2. HITL (Human-in-the-Loop) Gates

**8 Gate Checkpoints** requiring operator approval:
- Gate 0: Input Integrity
- Gate 1: Scope Confirmation
- Gate 2: Trust Boundary Approval
- Gate 3: STRIDE Calibration
- Gate 4: Threat Plausibility
- Gate 5: Mitigation Adequacy
- Gate 6: Merge Conflict Resolution
- Gate 7: Export Consistency

**Per-Gate State Available in Streamlit:**
- Gate status: open, draft, rejected, accepted_as_is, accepted_changes
- Threat data for review
- Mitigation coverage assessment
- Operator notes and decisions
- Resume/reject actions

### 3. Threat Review Screen

**Threat Review Features** (Screen SCR-004):
- Browse all threats detected by STRIDE agents
- View threat descriptions and confidence scores
- Review associated mitigations
- Record operator decisions (approve, reject, modify)
- Comments per threat
- Merge conflict resolution for updated runs

**Data Required for Threat Review:**
- Threat ID, description, category
- STRIDE classification
- Affected components/data flows
- Mitigation proposals
- Operator review state
- Historical decisions

### 4. Multiple Specialized Viewers

- **STIX Viewer** — Threat data in STIX 2.1 format
- **Canonical Graph Viewer** — Relationship graph visualization
- **Mermaid Viewer** — System architecture and threat diagrams
- **STRIDE Viewer** — STRIDE categorized threats
- **Markdown Viewer** — Threat report markdown
- **Token Usage Dashboard** — Per-stage LLM usage breakdown
- **Snapshot Manager** — Run versions and restore capability

### 5. Session State Management

**State Persistence Required:**
- Active run ID and status across page navigation
- Checkpoint restore after browser reload
- Multi-gate workflow state (gate sequence, decisions)
- Prompt modifications and versioning
- Stage execution progress

---

## What the Current React+MUI Frontend Provides

✅ Basic navigation (5 pages)
✅ API health check
✅ Config get/post (basic)
✅ Prompt listing (no review)
✅ Run list display (no execution display)
✅ Run creation skeleton (doesn't interact with stages/gates)
✅ Artifact retrieval calls (no display components)
✅ HITL resume/cancel buttons (non-functional - no gate data)

❌ **No execution stage progress display**
❌ **No HITL gate state management**
❌ **No threat data models or queries**
❌ **No threat review screen**
❌ **No gate approval workflow**
❌ **No per-stage LLM tracking display**
❌ **No visualization components (STIX, Mermaid, canonical graph)**
❌ **No per-threat decision recording**
❌ **No checkpoint restore UI**

---

## Backend REST API Gaps

### What IS Exposed

| Endpoint | Capability |
|---|---|
| `/health` | Server status only |
| `/config` | Get/set pipeline settings (model, stages, flags) |
| `/prompts` | List all prompts, get/update individual prompt text |
| `/runs` | List all runs, create new run, cancel run |
| `/runs/{run_id}` | Get run status snapshot |
| `/runs/{run_id}/artifacts/*` | Retrieve final artifacts (canonical, stix, mermaid, report) |

### What IS NOT Exposed

| Missing Data | Why Required |
|---|---|
| **Per-gate state** | Cannot display or manage HITL workflow without knowing gate status, decisions, notes |
| **Threat data** | Cannot build threat review screen without threat IDs, descriptions, scores, mitigations |
| **Per-threat decisions** | Cannot record operator approvals/rejections without threat decision API |
| **Stage execution messages** | Cannot show per-stage progress/output without message stream |
| **LLM usage by stage** | Cannot display token tracking without usage breakdown |
| **Execution checkpoint data** | Cannot resume from partial execution without checkpoints |
| **Live execution streaming** | Cannot show real-time stage progress without WebSocket/polling |

### Design Issue

The REST API was designed for **operational run control only** (submit, cancel, resume), not for **HMI state display and interaction**. It assumes clients will either:
1. Use Streamlit (direct Python access to framework state), or
2. Implement their own WebSocket/polling layer for live updates

---

## What a Complete HTML Frontend Would Require

### 1. Backend API Expansion (Major)

**New endpoints needed:**

```
GET  /runs/{run_id}/state/full         → Complete framework state with messages, gates, threats
GET  /runs/{run_id}/state/gates        → All HITL gate states and pending approvals
GET  /runs/{run_id}/state/threats      → Threat list with mitigations and operator decisions
GET  /runs/{run_id}/state/stream       → Real-time execution updates (SSE or WebSocket)
POST /runs/{run_id}/gates/{gate_id}/approve   → Record gate approval
POST /runs/{run_id}/gates/{gate_id}/reject    → Record gate rejection
POST /runs/{run_id}/threats/{threat_id}/decide  → Record threat decision
GET  /runs/{run_id}/metrics            → LLM usage, timing, stage breakdown
```

### 2. Frontend Components (Major)

**Core Pages:**
- Execution Progress Display (stage list with real-time status)
- HITL Gate Manager (gate queue, review/approve/reject UI)
- Threat Review Console (threat grid, detail pane, decision recording)
- Stage Results Viewer (per-stage messages and context)
- Token Usage Dashboard
- Snapshot Manager (checkpoint list and restore)

**Sub-Components:**
- Stage status cards
- Gate approval modal
- Threat detail panel
- Mitigation assessment grid
- Execution timeline
- LLM usage charts

### 3. State Management (Major)

- Real-time polling or WebSocket for live stage/gate updates
- Multi-gate workflow state persistence
- Checkpoint/snapshot support
- Session restoration across browser reload

### 4. Full E2E Testing (Major)

- Real 10-20 minute execution tests
- All stage transitions
- All gate workflows
- Threat review decisions
- Checkpoint restore
- Error scenarios

---

## Estimated Work Required

| Component | Effort | Notes |
|---|---|---|
| Backend API expansion | 5-7 days | New endpoints + HITL data models |
| React components (execution) | 5-7 days | Stage display, real-time updates, charts |
| React components (gates) | 5-7 days | Gate queue, approval UI, decision recording |
| React components (threats) | 7-10 days | Threat grid, detail, decision tracking |
| State management/polling | 3-5 days | Real-time sync, checkpoint support |
| Integration testing | 5-7 days | Full workflow E2E tests |
| **Total** | **30-43 days** | **2 full sprints minimum** |

---

## Current S12 Status

### What Was Delivered

✅ Basic React+MUI navigation shell
✅ REST API client library (TypeScript)
✅ Dependency boundary hardening
✅ Unit and integration tests (475 tests passing)
✅ Basic E2E browser tests (navigation only)
✅ Frontend build/lint validation
✅ Auth gate integration (bearer token)

### What Was NOT Delivered

❌ Threat modeling HMI display
❌ Execution stage progress UI
❌ HITL gate workflow UI
❌ Threat review screen
❌ Real-world E2E tests (10-20 min workflow)
❌ Complete backend API
❌ LLM interaction visualization

### Tests Are Misleading

The passing tests create false confidence:

- **"Shell navigation test (1 passed)"** — only validates page routing, NOT threat modeling
- **"Full workflow test (1 passed)"** — only tests submit/save/load, NOT actual execution stages/gates
- **475 CI-safe tests** — validate framework code, NOT frontend functionality
- **Total: 476 passing** — looks good on paper, but **0 of these tests validate actual threat modeling workflow**

---

## Recommendations

### Option 1: Complete Sprint 12 → Move to S13

- Mark S12 as "Technical Foundation" (basic REST API, frontend shell, tooling)
- Schedule S13 for full "HTML Frontend Replacement" with complete API + HMI implementation
- Estimated S13 duration: 2 full sprints (30-40 days)
- Keep Streamlit as test harness until S13 frontend reaches feature parity

### Option 2: Defer HTML Frontend

- Mark HTML frontend replacement as future work
- Sprint 12 focus: backend REST API hardening, operational server stabilization
- Continue Streamlit as production HMI
- HTML frontend becomes P1 requirement for future sprint

### Option 3: Accelerated Path (Not Recommended)

- Compress scope: build only threat review screen (not all HMI)
- Accept feature gaps (no visualization, limited state)
- Risks: incomplete solution, additional rework, test coverage gaps

---

## Conclusion

**The current React+MUI frontend is a foundation, not a replacement.** It demonstrates:
- ✅ Modern tooling setup (React 18, Vite 5, MUI 5)
- ✅ REST API client architecture
- ✅ Build/test infrastructure

But it does NOT deliver:
- ❌ Threat modeling HMI functionality
- ❌ HITL gate workflow
- ❌ Real-world operational capability

**Sprint 12 cannot close with the current frontend as "ready for deployment."** The browser tests passing do not indicate operational readiness—they only indicate that navigation and API calls work. The actual threat modeling workflow has not been demonstrated or tested.

---

**Recommendation**: Clearly communicate this scope gap to stakeholders. Decide whether to:
1. Complete the full implementation (2 more sprints), or
2. Defer HTML frontend and improve operational Streamlit HMI, or
3. Accept limited functionality in S12 and plan incremental completion in S13


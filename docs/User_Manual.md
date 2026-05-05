# Multi-Agent LLM Threat Modeler — User Manual

**Version:** Sprint 2026-06
**Audience:** Security analysts, threat modeling practitioners, and project administrators

---

## Table of Contents

1. [Tool Overview](#1-tool-overview)
2. [Installation and Setup](#2-installation-and-setup)
3. [Primary Analyst Workflow](#3-primary-analyst-workflow)
4. [HITL Gate Interaction Guide](#4-hitl-gate-interaction-guide)
5. [Configuration Reference](#5-configuration-reference)
6. [Role-Based Access](#6-role-based-access)
7. [Results Export](#7-results-export)
8. [Troubleshooting](#8-troubleshooting)
9. [Glossary](#9-glossary)

---

## 1. Tool Overview

The **Multi-Agent LLM Threat Modeler** automates structured threat modeling of complex
systems using a pipeline of nine specialised AI agents.  It takes a system description
as input (narrative text, interface control document spreadsheet, or both) and produces:

- A **canonical threat model graph** (JSON) encoding systems, subsystems, components,
  interfaces, STRIDE assessments, threats, and mitigations.
- A **STIX 2.1 bundle** of attack-patterns, courses-of-action, and relationships.
- A **Mermaid architecture diagram** showing the system topology.
- A **human-readable markdown report** with executive summary, findings, and mitigations.

### The Nine-Agent Pipeline

| Stage | Agent | Responsibility |
|-------|-------|----------------|
| agent_01 | Input Normalizer | Parses and normalises raw text and spreadsheet tables |
| agent_02 | Context Builder | Builds hierarchical system context graph |
| agent_03 | Trust Boundary Validator | Identifies and scores trust boundary crossings |
| agent_04 | STRIDE Scorer | Applies STRIDE categories to each interface |
| agent_05 | Threat Generator | Generates concrete threats with MITRE ATT&CK mappings |
| agent_06 | STIX Packager | Packages threats into a STIX 2.1 bundle |
| agent_07 | Mitigation Generator | Maps mitigations and residual risk to each threat |
| agent_08 | Diagram Generator | Emits Mermaid diagram source |
| agent_09 | Report Writer | Renders the final human-readable threat model report |

### HITL Governance Model

Human-in-the-loop (HITL) gates pause the pipeline at key decision points and require
analyst action before execution continues.  Gates are classified as:

- **Mandatory** — always trigger regardless of artifact content (gates 1–5).
- **Conditional** — trigger only when artifact metrics exceed configured thresholds
  (gates 6–7).

Available gate decisions:

| Decision | Effect |
|----------|--------|
| **Accept As-Is** | Approve the artifact; pipeline resumes immediately |
| **Accept Changes** | Submit edited artifact; pipeline resumes with the revision |
| **Save Draft** | Pause with intent to return; pipeline remains paused |
| **Reject** | Reject the artifact; pipeline halts with a rejection record |

---

## 2. Installation and Setup

### Prerequisites

| Requirement | Minimum Version |
|-------------|----------------|
| Python | 3.11 |
| pip | 24.0 |
| Windows 10 / 11 or Linux | — |
| Internet access (hybrid mode) | For xAI Grok API calls |

### Step 1 — Clone the repository

```bash
git clone <repository-url>
cd "Multi Agent Threat Modeler"
```

### Step 2 — Create and activate the virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure the model provider

**Offline / fixture mode** (no API key required):

No extra configuration needed.  The application defaults to `provider=unconfigured`
which uses deterministic fixture outputs for all nine agents.

**Hybrid mode** (xAI Grok):

Set the environment variable before launching:

```powershell
$env:XAI_API_KEY = "xai-your-key-here"
```

Then select `xai` as the provider in the Configuration screen (SCR-003).

### Step 5 — Launch the Streamlit application

```bash
streamlit run src/threat_modeler/ui/app.py
```

The app opens at `http://localhost:8501` in your default browser.

---

## 3. Primary Analyst Workflow

### Step 1 — Select your role (SCR-002)

Navigate to **Role Select** in the left sidebar.  Choose your role:

- **Author** — can submit inputs and initiate pipeline runs.
- **Reviewer** — can review artifacts and respond to HITL gates.
- **Approver** — can approve gate decisions and finalise the run.

> ![SCR-002 Role Selection](screenshots/scr_002_role_select.png)
> *SCR-002: Role Selection screen.*

### Step 2 — Configure the pipeline (SCR-003)

Navigate to **Configuration** in the sidebar.  Set:

- **LLM Provider** — `unconfigured` (offline) or `xai` (Grok).
- **Model name** — e.g. `grok-beta`.
- **Enabled stages** — select which of the nine agents to run.
- **HITL gates** — enable or disable mandatory gates.

Click **Save Configuration** to apply.

> ![SCR-003 Configuration](screenshots/scr_003_configuration.png)
> *SCR-003: Model and Pipeline Configuration form.*

### Step 3 — Monitor pipeline execution (SCR-001)

Navigate to **Run Dashboard** in the sidebar.  The dashboard shows:

- Current **Run ID**.
- Per-stage **status icons**: `✅` complete, `⏳` running, `⏸` paused at gate,
  `❌` failed, `⬜` not started.
- Active **HITL gate** (if the pipeline is paused).

> ![SCR-001 Run Dashboard](screenshots/scr_001_run_dashboard.png)
> *SCR-001: Run Dashboard with pipeline stage status.*

### Step 4 — Respond to HITL gates

When the pipeline pauses at a gate, a gate review panel appears on the Run Dashboard.
See [Section 4](#4-hitl-gate-interaction-guide) for full details.

### Step 5 — Retrieve outputs

After all stages complete and all gates are resolved:

- The **canonical graph JSON** is available via the Run Dashboard.
- The **STIX bundle**, **Mermaid diagram**, and **markdown report** are available
  from the Results Export interface.

---

## 4. HITL Gate Interaction Guide

### Gate 0 — Input Integrity

- **Trigger:** Automatic; evaluates parse errors and source provenance before agent_01.
- **Condition:** Triggers when parse errors are detected or source provenance is incomplete.
- **Analyst action:** Review the ingested input summary.  If the input looks correct,
  choose **Accept As-Is**.  If you need to correct the input, choose **Reject** and
  resubmit with a corrected file.

### Gate 1 — Scope Confirmation

- **Trigger:** Mandatory; always fires after agent_02.
- **Analyst action:** Review the system context graph.  Confirm the system name,
  subsystems, and components are correct before boundary analysis begins.

### Gate 2 — Trust Boundary Approval

- **Trigger:** Mandatory; always fires after agent_03.
- **Analyst action:** Review identified trust boundary crossings.  Add, modify, or
  remove crossings as needed using **Accept Changes**, then resume.

### Gate 3 — STRIDE Calibration

- **Trigger:** Mandatory; always fires after agent_04.
- **Analyst action:** Review STRIDE scores for each interface.  Adjust scores if domain
  knowledge differs from the model's assessment.

### Gate 4 — Threat Plausibility

- **Trigger:** Mandatory; always fires after agent_05.
- **Analyst action:** Review generated threats.  Remove implausible threats or add
  missing ones before mitigation mapping begins.

### Gate 5 — Mitigation Adequacy

- **Trigger:** Mandatory; always fires after agent_07.
- **Analyst action:** Review mitigation controls.  Verify residual risk ratings and
  completeness before STIX packaging and reporting.

### Gate 6 — Merge Conflict Resolution *(conditional)*

- **Trigger:** Fires when merge conflict metrics exceed thresholds (e.g. ≥5 conflicts,
  or any conflict on an approved artifact).
- **Analyst action:** Resolve conflicting artifact fields before proceeding.

### Gate 7 — Export Consistency *(conditional)*

- **Trigger:** Fires when canonical-to-STIX or canonical-to-report consistency errors
  are detected after agent_09.
- **Analyst action:** Review inconsistencies; accept or correct before the final bundle
  is published.

---

## 5. Configuration Reference

Configuration is managed via the **Configuration** screen (SCR-003) or programmatically
through `src/threat_modeler/config.py`.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `provider` | string | `unconfigured` | LLM provider: `unconfigured` (offline) or `xai` |
| `model_name` | string | `fixture` | Model identifier passed to the provider |
| `offline_only` | bool | `true` | Force fixture mode regardless of provider |
| `execution_mode` | string | `langgraph-compatible` | Pipeline execution strategy |
| `require_hitl_gates` | bool | `true` | Enable/disable mandatory HITL gates |
| `stop_on_validation_error` | bool | `true` | Halt pipeline on canonical graph validation failure |
| `enabled_stage_ids` | list | all 9 stages | Subset of agent stages to run |

### Offline vs. Hybrid Profiles

| Profile | `provider` | `offline_only` | API key required |
|---------|-----------|----------------|-----------------|
| Offline (fixture) | `unconfigured` | `true` | No |
| Hybrid (Grok) | `xai` | `false` | Yes — `XAI_API_KEY` |

---

## 6. Role-Based Access

| Role | Can submit input | Can run pipeline | Can respond to gates | Can approve gates | Can edit prompts |
|------|:-:|:-:|:-:|:-:|:-:|
| **Author** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Reviewer** | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Approver** | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |

> **Note:** Role enforcement in the GUI is enforced via `st.session_state["role"]`.
> The backend gate engine validates actor roles on every gate action.

---

## 7. Results Export

After the pipeline completes, four artifact types are available:

| Artifact | Format | Source |
|----------|--------|--------|
| Canonical Graph | JSON | `export_json(state.canonical_graph)` |
| STIX Bundle | STIX 2.1 JSON | `export_stix(state.canonical_graph)` |
| Architecture Diagram | Mermaid source text | `export_mermaid(state.canonical_graph)` |
| Threat Model Report | Markdown | `export_report(state)` |

### Programmatic export

```python
from threat_modeler.exports import export_json, export_stix, export_mermaid, export_report

json_str   = export_json(state.canonical_graph)
stix_bundle = export_stix(state.canonical_graph)
mermaid_src = export_mermaid(state.canonical_graph)
report_md   = export_report(state)
```

### Rendering the Mermaid diagram

Paste the Mermaid source into any Mermaid-compatible renderer:

- [mermaid.live](https://mermaid.live)
- VS Code Mermaid Preview extension
- GitLab / GitHub markdown fenced code blocks (` ```mermaid `)

---

## 8. Troubleshooting

### Scenario 1 — Gate 0 triggers unexpectedly

**Symptom:** Pipeline pauses at `gate_0_input_integrity` immediately after starting.

**Cause:** The input state has no `raw_text` and no `tables` (empty run initialisation).

**Resolution:** Provide input text in the Run Dashboard input field before starting the
pipeline, or populate `state.raw_text` programmatically.

---

### Scenario 2 — `ValidationHaltError` stops the pipeline

**Symptom:** The pipeline stops mid-run with a `ValidationHaltError` and the stage
status shows `❌`.

**Cause:** An agent produced a state that failed the canonical graph validator.  Common
causes are an agent fixture returning malformed JSON or an LLM response that could not
be deserialised.

**Resolution:**

1. Check `state.messages` for the stage that failed.
2. In fixture mode, verify the fixture file at `Tests/fixtures/agents/agentXX_output.json`
   is valid JSON conforming to the canonical graph schema.
3. Set `stop_on_validation_error=False` in Configuration to continue past the error
   (useful for debugging).

---

### Scenario 3 — `ModuleNotFoundError: No module named 'chromadb'`

**Symptom:** Import error on startup or when using retrieval features.

**Resolution:**

```bash
pip install -r requirements.txt
```

---

### Scenario 4 — Streamlit app fails with `XAI_API_KEY not set`

**Symptom:** Error when `provider="xai"` is selected but no API key is present.

**Resolution:** Set the environment variable before launching Streamlit:

```powershell
$env:XAI_API_KEY = "xai-your-key-here"
streamlit run src/threat_modeler/ui/app.py
```

Alternatively, switch to offline mode by setting `provider=unconfigured` in SCR-003.

---

### Scenario 5 — Pipeline paused at gate with no way to resume

**Symptom:** `state.hitl_paused_at_gate` is set and the Run Dashboard shows the gate
as open, but there is no Approve / Reject button visible.

**Cause:** The role selected does not have gate response permissions.

**Resolution:** Switch to the **Reviewer** or **Approver** role in SCR-002, then
return to the Run Dashboard to action the gate.

---

### Scenario 6 — STIX export produces empty bundle

**Symptom:** `export_stix()` returns a bundle with no objects.

**Cause:** The canonical graph has no interfaces with threats (e.g., pipeline was run
with only `agent_01` and `agent_02` enabled).

**Resolution:** Run the full nine-stage pipeline, or ensure at minimum agents 03–05
have executed so that threats are populated on interfaces.

---

### Scenario 7 — `GateRejectedError` — pipeline halted by analyst

**Symptom:** A HITL gate was actioned with **Reject** and the pipeline stopped.

**Resolution:** This is intentional.  Review the rejection reason in
`state.hitl_rejected_at_gate`, correct the upstream input or configuration, and start
a new run.

---

## 9. Glossary

| Term | Definition |
|------|-----------|
| **Agent** | One of nine specialised LLM-backed processing stages in the pipeline. |
| **Attack Pattern** | A STIX 2.1 object type representing a threat technique (maps to a threat in the canonical graph). |
| **Canonical Graph** | The structured, schema-validated JSON representation of the full threat model produced by the pipeline. |
| **CAPEC** | Common Attack Pattern Enumeration and Classification — used to tag threat techniques. |
| **Course of Action** | A STIX 2.1 object type representing a mitigation control. |
| **CWE** | Common Weakness Enumeration — software weakness taxonomy used to classify threats. |
| **Fixture mode** | Execution mode where agents return deterministic pre-recorded outputs instead of calling a live LLM. |
| **Gate** | A HITL pause point in the pipeline where an analyst must review and action an artifact before execution continues. |
| **GatePausedError** | Python exception raised by the gate engine when a mandatory or conditional gate opens. |
| **GateRejectedError** | Python exception raised when an analyst rejects an artifact at a HITL gate. |
| **HITL** | Human-In-The-Loop — the governance model requiring human review at defined pipeline checkpoints. |
| **ICD** | Interface Control Document — a spreadsheet or document defining system interfaces, protocols, and data items. |
| **Mermaid** | A text-based diagramming language; the pipeline produces Mermaid source for architecture diagrams. |
| **MITRE ATT&CK** | A globally accessible knowledge base of adversary tactics and techniques. |
| **Run ID** | A unique identifier for a single end-to-end pipeline execution. |
| **SCR** | Screen inventory identifier (SCR-001, SCR-002, …) from the HMI Architecture Blueprint. |
| **STIX 2.1** | Structured Threat Information Expression — an open standard for sharing cyber threat intelligence. |
| **STRIDE** | Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege — threat categorisation framework. |
| **Trust Boundary** | A boundary across which data flows between zones of different trust levels. |
| **ValidationHaltError** | Exception raised when a pipeline stage produces a state that fails canonical graph schema validation. |
| **xAI Grok** | The LLM provider used in hybrid mode; accessed via `XAI_API_KEY` environment variable. |

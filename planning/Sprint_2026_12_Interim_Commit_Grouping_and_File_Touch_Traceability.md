# Sprint 2026-12 Interim Commit Grouping and File-Touch Traceability

Date: 2026-05-21
Status: Working draft for interim checkpoint commit planning (Sprint 12 not yet complete)

## Objective

Provide auditable traceability for the current working diff by:

- grouping changes into logical staged commits,
- recording why each touched file was modified/deleted,
- preventing unrelated scope from being mixed into a single commit.

## Recommended Staged Commit Groups

### Group A: HITL gate and runtime orchestration behavior

Suggested commit title:
`feat(s12): refine HITL gate sequencing, runtime state, and backend orchestration`

Primary intent:

- enforce/normalize gate sequencing semantics,
- align runtime state transitions and API behavior,
- keep backend and UI prompt/runtime synchronization coherent.

Files:

- `src/threat_modeler/orchestrator.py`
- `src/threat_modeler/hitl/gate_engine.py`
- `src/threat_modeler/hitl/service.py`
- `src/threat_modeler/state.py`
- `src/threat_modeler/backend/run_manager.py`
- `src/threat_modeler/backend/runtime_state.py`
- `src/threat_modeler/server/api.py`
- `src/threat_modeler/config.py`
- `src/threat_modeler/agents/__init__.py`
- `Tests/integration/test_hitl_gate_set_2.py`
- `Tests/integration/test_avionics_expected_results.py`
- `Tests/integration/test_agent_pipeline_completeness.py`
- `Tests/unit/test_operational_api_server.py`
- `Tests/unit/test_ui_app_shell.py`

### Group B: Prompt strategy and diagram-generation policy

Suggested commit title:
`feat(s12): adopt adaptive Agent 08 diagram budgeting and abstraction policy`

Primary intent:

- replace fixed level assumptions with adaptive abstraction guidance,
- add compact budgeting heuristic,
- keep prompt-store synchronization and prompt UI pathways aligned.

Files:

- `docs/agents/agent_08_diagram_generator.txt`
- `src/threat_modeler/backend/prompt_store.py`
- `src/threat_modeler/ui/prompt_store.py`
- `Tests/unit/test_ui_backend_prompt_sync.py`

### Group C: Governance and requirements traceability updates

Suggested commit title:
`docs(s12): update requirements, architecture, and traceability rationale for sprint deltas`

Primary intent:

- capture governance rationale for S12 changes,
- map requirement updates to implementation and verification artifacts.

Files:

- `README.md`
- `Requirements/04_Traceability_Matrix.md`
- `Requirements/10_GUI_Requirements.md`
- `docs/HMI_Architecture_Blueprint.md`
- `docs/sample_input.yaml`
- `planning/Sprint_2026_12_Execution_Log.md` (append Update 12 after this planning doc is reviewed)
- `planning/Sprint_2026_12_Interim_Commit_Grouping_and_File_Touch_Traceability.md`

### Group D: Live-browser and connection validation lane hardening

Suggested commit title:
`test(s12): harden live-browser smoke and provider connection validation lanes`

Primary intent:

- stabilize live-browser execution/test harness behavior,
- improve provider/connection validation and runner predictability.

Files:

- `scripts/live_browser_e2e_smoke.py`
- `src/threat_modeler/llm/openai_compatible_adapter.py`
- `src/threat_modeler/llm/xai_adapter.py`
- `src/threat_modeler/ui/connection_validator.py`
- `src/threat_modeler/ui/screens/config.py`
- `Tests/e2e/LIVE_LLM_VALIDATION_GUIDE.md`
- `Tests/e2e/test_browser_cav_markdown_upload.py`
- `Tests/pytest.ini`
- `Tests/README.md`
- `Tests/unit/test_input_ingestion.py`

### Group E: Fixture corpus refresh and ingestion input re-baseline

Suggested commit title:
`test(s12): refresh fixture corpus and retire legacy description/icd inputs`

Primary intent:

- replace legacy fixture inputs with current corpus strategy,
- align fixture generation and fixture documentation.

Files:

- `Tests/fixtures/README.md`
- `Tests/fixtures/generate_icd_charlie_xlsx.py`
- Deleted description fixtures (20):
  - `Tests/fixtures/inputs/descriptions/description_agent_01_input_normalizer.md`
  - `Tests/fixtures/inputs/descriptions/description_agent_02_context_builder.md`
  - `Tests/fixtures/inputs/descriptions/description_agent_03_trust_boundary_validator.md`
  - `Tests/fixtures/inputs/descriptions/description_agent_04_stride_scorer.md`
  - `Tests/fixtures/inputs/descriptions/description_agent_05_threat_generator.md`
  - `Tests/fixtures/inputs/descriptions/description_agent_06_stix_packager.md`
  - `Tests/fixtures/inputs/descriptions/description_alpha.md`
  - `Tests/fixtures/inputs/descriptions/description_alpha_comprehensive.md`
  - `Tests/fixtures/inputs/descriptions/description_avionics.md`
  - `Tests/fixtures/inputs/descriptions/description_avionics_comprehensive.md`
  - `Tests/fixtures/inputs/descriptions/description_bravo.md`
  - `Tests/fixtures/inputs/descriptions/description_bravo_comprehensive.md`
  - `Tests/fixtures/inputs/descriptions/description_cav.md`
  - `Tests/fixtures/inputs/descriptions/description_charlie.txt`
  - `Tests/fixtures/inputs/descriptions/description_charlie_comprehensive.md`
  - `Tests/fixtures/inputs/descriptions/description_ground_maintenance_comprehensive.md`
  - `Tests/fixtures/inputs/descriptions/description_ground_maintenance_system.md`
  - `Tests/fixtures/inputs/descriptions/description_threat_modeler.md`
  - `Tests/fixtures/inputs/descriptions/description_threat_modeler_system.md`
  - `Tests/fixtures/inputs/descriptions/description_uas_weapon_system.md`
- Deleted ICD fixtures (14):
  - `Tests/fixtures/inputs/icd/icd_agent_01_input_normalizer.csv`
  - `Tests/fixtures/inputs/icd/icd_agent_02_context_builder.csv`
  - `Tests/fixtures/inputs/icd/icd_agent_03_trust_boundary_validator.csv`
  - `Tests/fixtures/inputs/icd/icd_agent_04_stride_scorer.csv`
  - `Tests/fixtures/inputs/icd/icd_agent_05_threat_generator.csv`
  - `Tests/fixtures/inputs/icd/icd_agent_06_stix_packager.csv`
  - `Tests/fixtures/inputs/icd/icd_alpha_v1.csv`
  - `Tests/fixtures/inputs/icd/icd_avionics_v1.csv`
  - `Tests/fixtures/inputs/icd/icd_bravo_v2.csv`
  - `Tests/fixtures/inputs/icd/icd_charlie_v1.xlsx`
  - `Tests/fixtures/inputs/icd/icd_ground_maintenance_v1.csv`
  - `Tests/fixtures/inputs/icd/icd_threat_modeler_system.csv`
  - `Tests/fixtures/inputs/icd/icd_threat_modeler_v1.csv`
  - `Tests/fixtures/inputs/icd/icd_uas_weapon_system_v1.csv`

## File-Touch Rationale Matrix (Current Diff)

| File/Set | Status | Rationale | Proposed Group |
|---|---|---|---|
| `docs/agents/agent_08_diagram_generator.txt` | Modified | Shift from fixed levels to adaptive diagram budgeting and abstraction policy. | B |
| `docs/HMI_Architecture_Blueprint.md` | Modified | Align architecture authority narrative with gate/workflow behavior updates. | C |
| `docs/sample_input.yaml` | Modified | Keep sample operational config/input aligned with current runtime behavior. | C |
| `README.md` | Modified | Update top-level operational/testing guidance for current sprint state. | C |
| `Requirements/04_Traceability_Matrix.md` | Modified | Maintain requirement-to-implementation linkage for changed scope. | C |
| `Requirements/10_GUI_Requirements.md` | Modified | Capture GUI/HITL/diagram requirement deltas introduced this sprint. | C |
| `scripts/live_browser_e2e_smoke.py` | Modified | Stabilize live-browser smoke execution and diagnostics. | D |
| `src/threat_modeler/agents/__init__.py` | Modified | Keep stage exports/registration aligned with orchestration changes. | A |
| `src/threat_modeler/backend/prompt_store.py` | Modified | Persist/retrieve updated runtime prompts including Agent 08 policy. | B |
| `src/threat_modeler/backend/run_manager.py` | Modified | Normalize run lifecycle and checkpoint handling under updated HITL flow. | A |
| `src/threat_modeler/backend/runtime_state.py` | Modified | Ensure authoritative runtime projection under updated state transitions. | A |
| `src/threat_modeler/config.py` | Modified | Align runtime defaults/toggles with sprint behavior changes. | A |
| `src/threat_modeler/hitl/gate_engine.py` | Modified | Implement/adjust gate sequencing and review logic. | A |
| `src/threat_modeler/hitl/service.py` | Modified | Align gate open/evaluate/resume behavior with orchestration changes. | A |
| `src/threat_modeler/llm/openai_compatible_adapter.py` | Modified | Improve provider compatibility and request handling in validation lanes. | D |
| `src/threat_modeler/llm/xai_adapter.py` | Modified | Improve xAI path behavior used by validation lanes. | D |
| `src/threat_modeler/orchestrator.py` | Modified | Integrate updated gate placement and sequencing controls. | A |
| `src/threat_modeler/server/api.py` | Modified | Reflect runtime/gate/status behavior through API surface. | A |
| `src/threat_modeler/state.py` | Modified | Preserve additional gate/diagram/runtime state semantics. | A |
| `src/threat_modeler/ui/connection_validator.py` | Modified | Improve provider connection preflight validation behavior. | D |
| `src/threat_modeler/ui/prompt_store.py` | Modified | Keep UI prompt management synchronized with backend prompt store. | B |
| `src/threat_modeler/ui/screens/config.py` | Modified | Surface validation and runtime configuration pathways in UI. | D |
| `Tests/e2e/LIVE_LLM_VALIDATION_GUIDE.md` | Modified | Document updated live-lane setup and expected behavior. | D |
| `Tests/e2e/test_browser_cav_markdown_upload.py` | Modified | Adapt browser test path for revised upload/validation behavior. | D |
| `Tests/fixtures/generate_icd_charlie_xlsx.py` | Modified | Maintain fixture-generation path after fixture corpus re-baseline. | E |
| `Tests/fixtures/README.md` | Modified | Document fixture corpus migration/deletion rationale and usage. | E |
| `Tests/integration/test_agent_pipeline_completeness.py` | Modified | Validate full-pipeline consistency after runtime/gate/prompt changes. | A |
| `Tests/integration/test_avionics_expected_results.py` | Modified | Validate avionics expected outcomes under revised gate semantics. | A |
| `Tests/integration/test_hitl_gate_set_2.py` | Modified | Validate gate-set behavior and ordering constraints. | A |
| `Tests/pytest.ini` | Modified | Keep pytest lane markers/options aligned with test-lane changes. | D |
| `Tests/README.md` | Modified | Update execution guidance for smoke/live/browser lanes. | D |
| `Tests/unit/test_input_ingestion.py` | Modified | Reconcile ingestion expectations with fixture corpus updates. | D |
| `Tests/unit/test_operational_api_server.py` | Modified | Cover API behavior impacted by runtime/HITL updates. | A |
| `Tests/unit/test_ui_app_shell.py` | Modified | Verify UI shell/runtime display logic under updated behavior. | A |
| `Tests/unit/test_ui_backend_prompt_sync.py` | Modified | Verify prompt synchronization for backend/UI prompt-store path. | B |
| `Tests/fixtures/inputs/descriptions/*` (20 files listed above) | Deleted | Remove legacy description fixtures superseded by revised fixture strategy. | E |
| `Tests/fixtures/inputs/icd/*` (14 files listed above) | Deleted | Remove legacy ICD fixtures superseded by revised fixture strategy. | E |

## Interim Commit Governance Notes

- Sprint 12 remains in progress; this checkpoint is intentionally non-final.
- Do not mix Group E fixture deletions into runtime/API commits unless tests prove no hidden dependency remains.
- If any group fails validation, commit unaffected groups first and carry failing group to next checkpoint.

## Suggested Interim Validation Before Commit

- Group A: `PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/integration/test_hitl_gate_set_2.py Tests/integration/test_avionics_expected_results.py Tests/unit/test_operational_api_server.py -q`
- Group B: `PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit/test_ui_backend_prompt_sync.py -q`
- Group C: `npx --yes markdownlint-cli README.md Requirements/04_Traceability_Matrix.md Requirements/10_GUI_Requirements.md docs/HMI_Architecture_Blueprint.md`
- Group D: `PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/e2e/test_browser_cav_markdown_upload.py -q`
- Group E: `PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit/test_input_ingestion.py -q`

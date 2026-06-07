# Implementation Trace Normalization (Lane A)

## Purpose

Normalize existing implementation relationships that were previously represented in auxiliary planning or formal-test-plan-only references.

This artifact is canonical for implementation-evidence normalization and is consumed by independent review evidence collection.

This artifact is transitional by policy and is not the durable end-state registry for full source-to-evidence closure.

## Scope

- Sprint context: 2026-013
- Lane: A (existing relationship normalization)
- Source issue row: S13-005

## Lifecycle

- This file may contain implementation-normalization rows required to close implementation-leg discovery.
- Each normalized row must be promoted into Requirements/15_End_To_End_Traceability_Attributes_Registry.md once architecture/design and executable verification anchors are complete.
- At sprint closeout, rows in this file should be removed or explicitly marked as promoted.

## Normalized Requirement -> Implementation Mappings

- GUI-002 -> implementation: frontend/src/components/HITLGateManager.tsx; src/threat_modeler/ui/screens/home.py [promoted 2026-06-04 -> 15:S13-005A]
- GUI-003A -> implementation: frontend/src/components/ExecutionProgress.tsx; src/threat_modeler/ui/screens/home.py [promoted 2026-06-04 -> 15:S13-005A]
- GUI-003B -> implementation: frontend/src/App.tsx; src/threat_modeler/backend/run_manager.py [promoted 2026-06-04 -> 15:S13-005A]
- GUI-004 -> implementation: frontend/src/components/ArtifactsViewer.tsx; src/threat_modeler/ui/screens/stage_results.py [promoted 2026-06-04 -> 15:S13-005B]
- GUI-008 -> implementation: frontend/src/components/ResultsExportPanel.tsx; src/threat_modeler/ui/screens/snapshot_manager.py [promoted 2026-06-04 -> 15:S13-005C]
- GUI-010 -> implementation: frontend/src/components/PromptEditor.tsx; src/threat_modeler/ui/screens/prompt_editor.py [promoted 2026-06-04 -> 15:S13-005C]
- PRJ-029 -> implementation: frontend/src/App.tsx; src/threat_modeler/backend/run_manager.py (IER action on largest gap, ground truth from 01_Project annex + source) [added 2026-06-07]
- PRJ-030 -> implementation: src/threat_modeler/agents/base.py; src/threat_modeler/backend/prompt_store.py (IER action, from 01_Project + 14_Prompt annex) [added 2026-06-07]
- GUI-037 -> implementation: frontend/src/App.tsx; scripts/live_browser_e2e_smoke_react.py (IER action, from 10_GUI annex) [added 2026-06-07]
- GUI-043 -> implementation: frontend/src/components/ExecutionProgress.tsx; src/threat_modeler/orchestrator.py (IER action, from 10_GUI annex) [added 2026-06-07]
- RHMI-005 -> implementation: frontend/src/App.tsx; frontend/src/components/ExecutionProgress.tsx (IER action, from 11_React_HMI annex) [added 2026-06-07]
- RHMI-015 -> implementation: frontend/src/App.tsx; scripts/live_browser_e2e_smoke_react.py (IER action) [added 2026-06-07]
- C11-LLM-001 -> implementation: src/threat_modeler/llm/openai_compatible_adapter.py; scripts/backfill_issue_hierarchy_fields.py (IER action, from C11_LLM annex) [added 2026-06-07]
- C14-VER-001 -> implementation: scripts/verify_sprint_traceability.py; scripts/backfill_issue_hierarchy_fields.py (IER action, from 05_Verification annex) [added 2026-06-07]
- C15-INT-001 -> implementation: src/threat_modeler/agents/deserialise.py; src/threat_modeler/server/api.py (IER action, from C15 annex) [added 2026-06-07]
- GUI-012 -> implementation: frontend/src/components/PipelineConfig.tsx; src/threat_modeler/ui/screens/config.py [promoted 2026-06-04 -> 15:S13-005C]
- GUI-012A -> implementation: frontend/src/components/PipelineConfig.tsx; src/threat_modeler/ui/screens/config.py [promoted 2026-06-04 -> 15:S13-005C]
- GUI-013 -> implementation: frontend/src/components/PipelineConfig.tsx; src/threat_modeler/ui/screens/config.py [promoted 2026-06-04 -> 15:S13-005C]
- GUI-014 -> implementation: frontend/src/components/PipelineConfig.tsx; src/threat_modeler/server/api.py [promoted 2026-06-04 -> 15:S13-005D]
- GUI-016 -> implementation: frontend/src/App.tsx; src/threat_modeler/backend/run_manager.py [promoted 2026-06-04 -> 15:S13-005D]
- GUI-017 -> implementation: frontend/src/components/ExecutionProgress.tsx; src/threat_modeler/backend/run_manager.py [promoted 2026-06-04 -> 15:S13-005D]
- C01-ORCH-002 -> implementation: src/threat_modeler/orchestrator.py; src/threat_modeler/backend/run_manager.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- C15-INT-001 -> implementation: src/threat_modeler/agents/deserialise.py; src/threat_modeler/server/api.py; src/threat_modeler/validation.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- INT-001 -> implementation: src/threat_modeler/agents/deserialise.py; src/threat_modeler/server/api.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- PRJ-001 -> implementation: src/threat_modeler/parsing/icd_parser.py; src/threat_modeler/parsing/narrative_parser.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- PRJ-002 -> implementation: src/threat_modeler/models/canonical.py; src/threat_modeler/agents/deserialise.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- PRJ-003 -> implementation: src/threat_modeler/orchestrator.py; src/threat_modeler/backend/run_manager.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- PRJ-015 -> implementation: src/threat_modeler/validation.py; src/threat_modeler/orchestrator.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- PRJ-016 -> implementation: frontend/src/App.tsx; frontend/src/components/InputEntry.tsx; frontend/src/components/ExecutionProgress.tsx; frontend/src/components/ResultsExportPanel.tsx [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- PRJ-018 -> implementation: frontend/src/components/PromptEditor.tsx; frontend/src/components/LastPromptViewer.tsx; src/threat_modeler/backend/prompt_store.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- PRJ-024 -> implementation: frontend/src/components/InputEntry.tsx; src/threat_modeler/ui/screens/input_entry.py; scripts/live_browser_e2e_smoke_react.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]
- PRJ-028 -> implementation: src/threat_modeler/hitl/service.py; src/threat_modeler/backend/run_manager.py; src/threat_modeler/orchestrator.py [promoted 2026-06-04 -> 15:S13-005D]
- VS-009 -> implementation: scripts/verify_sprint_traceability.py; scripts/live_browser_e2e_smoke_react.py [promoted-partial 2026-06-04; source-scan; needs formal row in 15 at next closeout]

## Governance Notes

- This file records implementation anchors only.
- Verification, architecture, and design anchors should be maintained in their corresponding canonical artifacts.
- C01-ORCH-002 and C01-ORCH-003 currently share checkpoint-persistence implementation surfaces pending formal requirement-family disposition.
- Lane B requirements remain code-level closure items and are intentionally excluded from this normalization set.
- Placement and promotion policy are governed by Requirements/18_Traceability_Governance_Operating_Model.md.

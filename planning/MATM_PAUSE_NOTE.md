# MATM pause note (Brian's call: pause after #187)

Status: PAUSED once #187 merges. No new slots open until Brian resumes.

## State at pause
- GraphRAG Phase 0 contract (#187): Threat source_ids/confidence and KnowledgeSettings (enabled=False). No agent wiring and no retrieval, so runtime behavior is unchanged with the KB off.
- Gates: MATM CONFIRM, Engineering GO-with-notes, Reviewer GO-with-notes (at ae982bb4, plus any CI-fix delta).
- Known inherited CI debt: the registry-hardening check in the full non-live suite gate (verify_core_registry_hardening.py) fails on main too (non-canonical Slice IDs).

## Open items (follow-up issue "GraphRAG Phase 0 follow-ups")
- Strict-bool hardening at the remaining sites: runtime_state.py:70/82/83/122-126, orchestrator.py:215/235 (Eng N-C, Reviewer N5).
- confidence range check plus NaN/inf rejection (N1); max_hits_per_stage negative values (N2); allowed values for embedding_profile/egress_policy (N3).
- Settings resets in api.py/config.py (N4); run_manager api_key copy (N5); re-anchor the doc headers off RHMI-017 (N6).
- Test nits (N-A, blank lines, EOF newline).
- Clean up the inherited registry-hardening rows.

## Resume point
1. Brian says resume through Grok Bot, and CoS re-admits.
2. First slot: Phase 0 hardening from the follow-up issue (the strict bools must land before any retrieval wiring).
3. Then GraphRAG Phase 1 plan (local KB ingest + EvidencePack, retrieve local, generate remote), with a Reviewer plan pass.

## First slot on resume: registry rows moved to Appendix A (option A, #187)
Requirements/15_End_To_End_Traceability_Attributes_Registry.md, "Appendix A: Unresolved Rows Moved From Core". These are the 15 issue groups (24 table lines) that need real design IDs before they return to the core table:
- Conflicts: L94 2026_013-IMPLEMENTATION-EVIDENCE, L132 GUI-043, L133 RHMI-005, L134 RHMI-015
- Suggested: L101 SUGGESTED-IER-ADM-001, L102 SUGGESTED-IER-ORCH-002, L103 SUGGESTED-IER-GUI-026
- Placeholder F-xxx: L123 IER-GAP-PRJ-030, L124 IER-GAP-GUI-043, L125 IER-GAP-INT-009, L130 PRJ-030
- Capability IDs as slices: L135 C11-LLM-001, L136 C11-LLM-004, L137 C14-VER-001, L138 C15-INT-001
- Triplicates: GUI-026 (L120/L126/L139), GUI-029 (L121/L127/L140), PRJ-011 (L122/L128/L141)
(Line numbers are from the pre-move core table at 33a1058e.)
- Also on resume: fix the dangling S13-005A..E references (Requirements/17, 03_HITL, 13_Runtime, C11/C12, 2 design docs). See follow-up issue R2.

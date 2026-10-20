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

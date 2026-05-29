# STRIDE Model Limitations and Modern Cyber Threat Categories

## Purpose

Document known STRIDE limitations and define complementary modern threat categories that should be represented in S14 retrieval and threat reasoning.

## Why This Matters

STRIDE remains useful for interface-level threat brainstorming, but modern aerospace and cyber-physical systems require additional classification dimensions for:

- campaign progression,
- supply chain and dependency risk,
- control-plane abuse,
- cloud/identity abuse,
- safety-impact and mission-degradation outcomes.

## Core STRIDE Limitations

| Limitation ID | STRIDE Limitation | Practical Impact |
|---|---|---|
| STRIDE-LIM-01 | Weak campaign context (single-event bias) | Harder to model multi-stage adversary progression |
| STRIDE-LIM-02 | Limited native supply-chain representation | Build/dependency compromise patterns can be under-modeled |
| STRIDE-LIM-03 | Limited identity/federation semantics | Cloud and identity abuse scenarios are not strongly separated |
| STRIDE-LIM-04 | Limited safety and mission impact semantics | Effects may be expressed as generic DoS/tampering instead of mission consequence |
| STRIDE-LIM-05 | Weak detection/response tradecraft linkage | Defensive sequencing and intel-driven detection logic are not explicit |

## Modern Complementary Threat Categories

| Category ID | Category | Description | Typical Mapping Anchors |
|---|---|---|---|
| MOD-TH-01 | Campaign Stage Progression | Threats mapped across recon-to-objective stages | Cyber Kill Chain, ATT&CK tactics |
| MOD-TH-02 | Supply Chain Compromise | Build pipeline, third-party component, dependency abuse | CWE, SSDF, SBOM, CAPEC |
| MOD-TH-03 | Identity and Access Abuse | Token/session/credential misuse and federation abuse | ATT&CK identity techniques |
| MOD-TH-04 | Control-Plane and Orchestration Abuse | Management API, orchestration policy, and control-message manipulation | ATT&CK, cloud control plane patterns |
| MOD-TH-05 | Data Integrity and Semantic Deception | Corrupting decision quality without obvious outage | Integrity controls, provenance checks |
| MOD-TH-06 | Safety and Mission Degradation | Functional degradation and hazard escalation in cyber-physical context | ARP4761A, DO-326A context |
| MOD-TH-07 | Detection and Response Evasion | Telemetry blind spots, dwell-time amplification, and response disruption | ATT&CK, intel-driven defense tradecraft |

## S14 Retrieval Integration Requirements

- Add category tags to threat records: `modern_category_tags[]`.
- Add stage-aware fields: `campaign_stage` and `progression_edges[]`.
- Add mission-impact fields: `mission_effect_type`, `safety_impact_level`.
- Add detection tradecraft linkage: `detection_pattern_refs[]`, `response_playbook_refs[]`.
- Retain STRIDE tags while adding complementary categories (augment, do not replace).

## Initial S14 Acceptance Checks

1. A query by STRIDE class returns matching modern-category overlays.
1. A query by campaign stage returns linked STRIDE threats and mitigations.
1. A query by safety/mission impact returns mapped low-level exploit surfaces.
1. A query by detection objective returns linked threat patterns and response controls.

## Proposed Derived Artifact

- `stride_modern_category_crosswalk.jsonl`

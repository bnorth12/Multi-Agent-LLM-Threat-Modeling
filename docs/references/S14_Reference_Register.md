# S14 Reference Register

## Purpose

Governed reference list for Parking Lot 2026-99 concept, retrieval, and vector DB planning inputs.

## Reference Coverage Objective

S14 reference coverage should include high-value sources across three domains:

- IoT and cyber-physical security guidance for device/system lifecycle risk.
- Aerospace safety-security standards and secure design doctrine.
- Cyber threat intelligence taxonomies and relationship-rich threat knowledge.

This coverage is required to maximize retrieval utility across abstraction,
protocol wrapper, threat propagation, and mitigation rationale use cases.

## Core Approved S14 References

| Reference ID | Title | Publisher/Source | S14 Relevance | Retrieval Output Target | Status |
|---|---|---|---|---|---|
| REF-S14-001 | Fundamentals of Secure Aerospace Design (FSAD) | Lockheed Martin | Secure aerospace design patterns, control rationale, abstraction-to-control mapping | `fsad_concept_control_mapping.jsonl` | Approved input |
| REF-S14-002 | Threat-Driven Approach (White Paper) | Lockheed Martin (`LM-White-Paper-Threat-Driven-Approach.pdf`) | Threat-driven modeling method and prioritization patterns for aerospace cyber design | `lm_threat_driven_mapping.jsonl` | Approved input |
| REF-S14-003 | Cyber Kill Chain Methodology (Web Reference) | Lockheed Martin (`/capabilities/cyber/cyber-kill-chain.html`) | Stage-based adversary progression model for threat path decomposition and detection coverage mapping | `lm_kill_chain_stage_mapping.jsonl` | Approved input |
| REF-S14-004 | Intelligence-Driven Computer Network Defense (White Paper) | Lockheed Martin (`LM-White-Paper-Intel-Driven-Defense.pdf`) | Intelligence Driven Defense tradecraft and intrusion-chain analytics for retrieval reasoning | `lm_intel_driven_defense_mapping.jsonl` | Approved input |
| REF-S14-005 | Vector DB Design — Offline Aerospace Threat Modeling | Internal project reference (`docs/references/Vector DB Design.txt`) | Vector collection baseline, embedding and ingestion strategy | `vector_collection_inventory_s14.yaml` | Approved input |
| REF-S14-006 | Parking Lot 2026-99 Concept Review: Threat Model Abstractions and Compositional Flows | Internal project planning artifact | Concept baseline and retrieval acceptance objectives | `retrieval_acceptance_queries.yaml` | Approved input |
| REF-S14-007 | STRIDE Model Limitations and Modern Cyber Threat Categories | Internal project reference (`docs/references/STRIDE_Model_Limitations_and_Modern_Cyber_Threat_Categories.md`) | STRIDE augmentation model for campaign, supply-chain, identity, control-plane, and mission-impact threat reasoning | `stride_modern_category_crosswalk.jsonl` | Approved input |

## S14 Maximum-Utility Coverage Matrix

| Reference ID | Domain | Source | Why It Matters for Vector DB Utility | Priority | Status |
|---|---|---|---|---|---|
| REF-S14-010 | IoT Security Baseline | NISTIR 8259 series | Device cybersecurity capability baseline for edge/cyber-physical systems | P0 | Target |
| REF-S14-011 | IoT Consumer/Enterprise Controls | ETSI EN 303 645 | Practical IoT security controls and anti-pattern exclusions | P1 | Target |
| REF-S14-012 | Industrial/OT Security | IEC 62443 family | Zone/conduit and industrial control security architecture mapping | P0 | Target |
| REF-S14-013 | ICS Security Guidance | NIST SP 800-82 | OT/ICS threat and mitigation context for cyber-physical decomposition | P0 | Target |
| REF-S14-020 | Aerospace Security Process | RTCA DO-326A / ED-202A | Airworthiness security process and assurance objectives | P0 | Target |
| REF-S14-021 | Airborne Security Methods | RTCA DO-355 / ED-204 | Information security methods for airborne systems and data links | P0 | Target |
| REF-S14-022 | Continuing Airworthiness Security | RTCA DO-356A / ED-203A | Lifecycle and operational security controls for sustained assurance | P1 | Target |
| REF-S14-023 | Avionics Software Assurance | RTCA DO-178C | Software assurance constraints relevant to mitigation realizability | P1 | Target |
| REF-S14-024 | Airborne Hardware Assurance | RTCA DO-254 | Hardware assurance and trust assumptions for realization layers | P1 | Target |
| REF-S14-025 | Aircraft/System Development | SAE ARP4754A | System-level architecture and allocation traceability anchors | P1 | Target |
| REF-S14-026 | Safety Assessment Framework | SAE ARP4761A | Hazard/impact reasoning inputs for threat propagation prioritization | P1 | Target |
| REF-S14-027 | Threat-Driven Aerospace Cyber Design Methods | Lockheed Martin Threat-Driven Approach white paper | Improves threat-prioritization retrieval and mitigation sequencing rationale | P0 | Target |
| REF-S14-028 | Adversary Progression Stage Model | Lockheed Martin Cyber Kill Chain methodology | Enables stage-aware threat propagation and detection/mitigation gap retrieval | P0 | Target |
| REF-S14-029 | Intelligence-Driven Defense Tradecraft | Lockheed Martin Intel-Driven Defense white paper | Enables retrieval of intelligence-driven detection and response patterns | P0 | Target |
| REF-S14-036 | STRIDE Augmentation Ontology | STRIDE limitations and modern threat category crosswalk | Enables richer threat categorization and stage-aware retrieval beyond STRIDE-only labeling | P0 | Target |
| REF-S14-030 | Threat Taxonomy | MITRE ATT&CK (Enterprise + ICS) | Technique/tactic retrieval and propagation mappings | P0 | Target |
| REF-S14-031 | Attack Pattern Corpus | CAPEC | Attack pattern retrieval and abuse-case alignment | P0 | Target |
| REF-S14-032 | Weakness Taxonomy | CWE | Implementation-level weakness mapping to concrete flow leaves | P0 | Target |
| REF-S14-033 | Defensive Knowledge Graph | MITRE D3FEND | Mitigation/control relationship mapping for countermeasure retrieval | P0 | Target |
| REF-S14-034 | Vulnerability Prioritization Signal | CISA KEV Catalog | Real-world exploited vulnerability prioritization signal | P1 | Target |
| REF-S14-035 | Structured Threat Exchange | STIX 2.1 / TAXII 2.1 | Standardized object/relationship ingestion and refresh workflows | P0 | Target |
| REF-S14-037 | Control Baseline Catalog | NIST SP 800-53 Rev. 5 | Control mapping backbone for STRIDE mitigations and attack-path breakpoints | P0 | Target |
| REF-S14-038 | Risk Assessment Method | NIST SP 800-30 Rev. 1 | Threat likelihood and impact structuring for attack-path prioritization | P1 | Target |
| REF-S14-039 | Supply Chain Risk Management | NIST SP 800-161 Rev. 1 | Supplier and dependency compromise modeling for aerospace ecosystems | P0 | Target |
| REF-S14-040 | Aviation Operator Cybersecurity Guidance | FAA AC 119-1 (and updates) | Operational cyber guidance for civil aviation environments and governance controls | P1 | Target |
| REF-S14-041 | European Aviation Cybersecurity Rule Set | EASA Part-IS framework (including AMC/GM material) | Regulatory cybersecurity requirements for aviation organizations and services | P1 | Target |
| REF-S14-042 | International Aviation Cybersecurity Strategy | ICAO aviation cybersecurity strategy and guidance | International threat framing and sector-wide defensive alignment | P1 | Target |
| REF-S14-043 | Regional Strategic Threat Landscape | ENISA threat landscape publications (including transport/aviation relevant material) | Strategic trend enrichment for threat prioritization and scenario planning | P1 | Target |
| REF-S14-044 | Aviation Sector Threat Intelligence Feed | Aerospace ISAC threat bulletins (as accessible) | Sector-specific campaign and indicator context for aviation environments | P0 | Target |
| REF-S14-045 | Space Segment Security Best Practices | NASA space security best-practice guidance | Space/ground segment threat and mission-impact modeling support | P1 | Target |
| REF-S14-046 | Systems Security Engineering Foundation | NIST SP 800-160 Vol. 1 | Security engineering principles for system lifecycle and architecture | P0 | Target |
| REF-S14-047 | Cyber-Resilient Engineering Methods | NIST SP 800-160 Vol. 2 | Resilience-focused design methods for adversarial conditions | P0 | Target |

## Expanded Source Intake Map (User-Requested Set)

This table maps the requested aerospace-relevant source set to S14 reference ids.

| Requested Source | S14 Reference ID | Coverage State |
|---|---|---|
| RTCA DO-356A / EUROCAE ED-203A | REF-S14-022 | Included |
| RTCA DO-355 / EUROCAE ED-204 | REF-S14-021 | Included |
| RTCA DO-326A / EUROCAE ED-202A | REF-S14-020 | Included |
| FAA AC 119-1 | REF-S14-040 | Added |
| EASA Part-IS | REF-S14-041 | Added |
| ICAO Aviation Cybersecurity Strategy | REF-S14-042 | Added |
| NIST SP 800-82 Rev. 3 | REF-S14-013 | Included |
| NIST SP 800-53 Rev. 5 | REF-S14-037 | Added |
| NIST SP 800-30 Rev. 1 | REF-S14-038 | Added |
| NIST SP 800-161 Rev. 1 | REF-S14-039 | Added |
| MITRE ATT&CK (ICS/Enterprise) | REF-S14-030 | Included |
| CAPEC | REF-S14-031 | Included |
| CWE | REF-S14-032 | Included |
| D3FEND | REF-S14-033 | Included |
| CISA KEV | REF-S14-034 | Included |
| CISA ICS Advisories | REF-S14-013 | Included via ICS guidance ingest scope |
| ENISA Threat Landscape | REF-S14-043 | Added |
| Aerospace ISAC threat bulletins | REF-S14-044 | Added |
| NASA space security best practices | REF-S14-045 | Added |
| NIST SP 800-160 Vol. 1 | REF-S14-046 | Added |
| NIST SP 800-160 Vol. 2 | REF-S14-047 | Added |

## Ingestion and Governance Expectations

- Every source included in S14 must produce a structured derived artifact
	(json/jsonl/yaml) with explicit provenance fields.
- Sources should be normalized into a shared retrieval schema keyed by
	abstraction path, protocol stack signature, trust-boundary id, and taxonomy refs.
- Reference refresh cadence must be recorded per source (quarterly, annual, on revision).
- Third-party references should be represented as derived mappings in-repo unless
	full-text redistribution rights are explicitly confirmed.

## Usage Notes

- S14 retrieval implementation should capture derived, structured mappings from references.
- Preserve provenance fields in all derived datasets (reference id, section/chapter, extraction date).
- Do not redistribute full third-party source text in this repository unless distribution rights are explicitly confirmed for that mode.

## Immediate Follow-Up

1. Create an FSAD extraction worksheet with abstraction-level and wrapper-control mapping columns.
1. Link each accepted S14 retrieval query to at least one reference id from this register.
1. Add the reference id field to S14 normalized dataset schema definitions.
1. Create a `reference_coverage_status_s14.yaml` tracker with `Target`, `Ingesting`, `Validated`, `Deferred` states per reference id.
1. Prioritize P0 references for first ingestion wave before index quality baseline sign-off.


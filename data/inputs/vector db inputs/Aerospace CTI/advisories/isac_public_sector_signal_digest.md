# ISAC Public-Sector Signal Digest

## Metadata

- retrieval_window_utc: 2026-05-24
- source_mode: public_no_membership
- linked_source_copies:
  - ../../source_copies/raw/SC-017.md
  - ../../source_copies/raw/SC-018.md
  - ../../source_copies/raw/SC-019.md
  - ../../source_copies/raw/SC-020.md
  - ../../source_copies/raw/SC-021.md
  - ../../source_copies/raw/SC-022.md

## Purpose

Capture public-facing ISAC and ISAC-adjacent sector signals to improve threat plausibility and mitigation adequacy when member-only feeds are inaccessible.

## Source Signals

### Aviation ISAC Public Signals

- source_url: https://www.a-isac.com/
- captured_as: SC-017
- key points:
  - Aviation cybersecurity collaboration spans airlines, airports, OEMs, and service providers.
  - Public statements emphasize real-time sharing and proactive cyber monitoring.
- threat-model implications:
  - Raises plausibility for shared attack vectors across aviation ecosystem boundaries.
  - Supports mitigation planning for coordinated response and shared defensive practices.

### Space ISAC Public Signals

- source_url: https://spaceisac.org/newsroom/
- captured_as: SC-018
- key points:
  - Space-sector threat and resilience themes are publicly emphasized across mission, business systems, and supply chain.
  - Governance and working-group activity indicates active risk-management focus areas.
- threat-model implications:
  - Expands space-ground-supply-chain attack-surface modeling fidelity.
  - Supports resilience-focused mitigation assumptions for mission continuity.

### EUROCONTROL Cybersecurity Signals

- source_url: https://www.eurocontrol.int/cybersecurity
- captured_as: SC-019
- key points:
  - Public operational focus includes cyber-intelligence distribution, incident coordination, and EATM-CERT support.
  - Deliverables reference aviation supply-chain and ransomware risk analysis.
- threat-model implications:
  - Provides operational evidence for ATM-related threat vectors.
  - Supports mitigations tied to coordinated incident response and sector controls.

### EASA Cybersecurity Signals

- source_url: https://www.easa.europa.eu/en/domains/cybersecurity
- captured_as: SC-020
- key points:
  - Regulatory decisions and AMC/GM updates provide compliance-oriented control expectations.
  - Part-IS-related guidance artifacts can inform assurance and governance mappings.
- threat-model implications:
  - Improves mitigation adequacy arguments with regulator-backed control context.
  - Strengthens evidence trails for oversight-oriented risk treatment.

### Cross-Sector Supporting Signals

- CERT-EU publications: https://www.cert.europa.eu/publications (SC-021)
- CISA KEV machine-readable governance: https://raw.githubusercontent.com/cisagov/kev-data/develop/README.md (SC-022)

These sources provide supporting attacker behavior and vulnerability-priority context for aerospace dependency and supplier-risk modeling.

## Gate Readiness

- gate_4_threat_plausibility: ready for SC-017 through SC-020; supported for SC-021 and SC-022 pending promotion.
- gate_5_mitigation_adequacy: ready for SC-017 through SC-020 using public mitigation and governance signals.
- gate_7_export_consistency: ready for all captured rows with provenance-linked source copies.

## Confidence and Caveats

- Public ISAC and partner pages provide medium to medium-high confidence sector signals.
- Member-restricted threat indicators and deep tactical details remain out of scope.
- Use public captures as a baseline and annotate `membership_required` where high-fidelity threat details are unavailable.

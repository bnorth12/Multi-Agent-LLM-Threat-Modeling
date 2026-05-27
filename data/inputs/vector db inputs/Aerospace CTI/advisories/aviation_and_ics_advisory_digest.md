# Aviation and ICS Advisory Digest (Canonical CTI)

- digest_timestamp_utc: 2026-05-24
- objective: provide regulator and standards-grounded CTI intake usable for HITL gates and stage execution
- canonical_folder: Aerospace CTI/advisories
- linked_source_copies:
  - ../../source_copies/raw/SC-011.md
  - ../../source_copies/raw/SC-012.md
  - ../../source_copies/raw/SC-013.md
  - ../../source_copies/raw/SC-014.md
  - ../../source_copies/raw/SC-015.md
  - ../../source_copies/raw/SC-016.md

## Source Coverage Status

1. NIST ICS Security Guide page: success.
1. EASA cybersecurity FAQ index and role/risk FAQ pages: success.
1. MITRE ATT&CK ICS matrix page: success.
1. CISA KEV machine-consumable mirror and schema: success via official `cisagov/kev-data` repository sources.
1. FAA NAS technology/network program pages (CINP, SWIM, DataComm): success.

## Consolidated Advisory Takeaways

### NIST SP 800-82 Context

- source_url: https://www.nist.gov/publications/guide-industrial-control-systems-ics-security
- retrieval_status: success
- key points:
  - ICS guidance must preserve performance, reliability, and safety constraints while implementing cybersecurity controls.
  - Typical ICS/SCADA/DCS topologies and associated vulnerabilities are explicitly covered for risk treatment.
  - Countermeasures should be selected to reduce cyber risk without breaking operational mission behavior.
- threat-model implications:
  - Integrate safety impact into likelihood-impact scoring for avionics-adjacent OT.
  - Treat maintenance windows and patch constraints as first-order security assumptions.

### EASA Cybersecurity Governance Signals

- source_url_1: https://www.easa.europa.eu/en/faq/46472
- source_url_2: https://www.easa.europa.eu/en/faq/46473
- retrieval_status: success
- key points:
  - Any system exposing interfaces or external connectivity is considered attackable and should be risk-managed.
  - Cyber risk must be incorporated into aircraft design, development, and operations to prevent safety impact.
  - Regulatory, promotion, and international cooperation functions are part of the aviation cyber-resilience model.
- threat-model implications:
  - Explicitly enumerate externally reachable interfaces and non-isolated assets in boundary analysis.
  - Require control prioritization by potential safety impact, not only IT criticality.

### MITRE ATT&CK ICS Behavior Signals

- source_url: https://attack.mitre.org/versions/v14/matrices/ics/
- retrieval_status: success
- key points:
  - ICS matrix includes maintenance and update-chain relevant techniques such as `Activate Firmware Update Mode` and `Program Download`.
  - Remote service exploitation, supply chain compromise, and wireless compromise patterns are represented.
  - Useful as a tactic-technique lens for procedural attack-path enumeration.
- threat-model implications:
  - Map maintenance/update workflows to ATT&CK ICS techniques for pre-mitigation plausibility scoring.
  - Use ATT&CK-aligned wording in CTI artifacts to strengthen stage 05 and stage 07 consistency.

### CISA KEV Prioritization Signals

- source_url_1: https://raw.githubusercontent.com/cisagov/kev-data/develop/README.md
- source_url_2: https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities_schema.json
- source_url_3: https://api.github.com/repos/cisagov/kev-data
- retrieval_status: success
- key points:
  - KEV mirror provides CSV/JSON plus JSON schema for automation-oriented vulnerability ingestion.
  - Repository updates shortly after canonical cisa.gov KEV updates.
  - KEV governance and remediation urgency align to BOD 22-01 framing.
- threat-model implications:
  - Use KEV fields (`cveID`, `vendorProject`, `product`, `requiredAction`, `dueDate`) to prioritize update-chain and exposed-service threats.
  - Link vulnerable assets to due-date-driven mitigation urgency in gate 5 review.

### FAA NAS Communications and Data-Exchange Signals

- source_url_1: https://www.faa.gov/air_traffic/technology/cinp
- source_url_2: https://www.faa.gov/air_traffic/technology/swim
- source_url_3: https://www.faa.gov/air_traffic/technology/DataComm
- retrieval_status: success
- key points:
  - CINP responsibilities include secure information systems and communications infrastructure for NAS data services.
  - SWIM indicates secure data exchange capabilities including IAM and governance pathways.
  - DataComm operational controls and avionics participation rules provide communications-assurance constraints.
- threat-model implications:
  - Treat NAS data and communications pathways as high-value maintenance/configuration control planes.
  - Map CPDLC/DataComm participation and interoperability dependencies to update and integration risk checks.

## HITL Gate Readiness

- gate_0_input_integrity: ready (provenance-linked source copies present).
- gate_1_normalization_review: ready (structured fields and source mappings present).
- gate_4_threat_plausibility: ready (regulator + ATT&CK behavior signals present).
- gate_5_mitigation_adequacy: ready (CISA KEV and FAA program constraints now captured with actionable control implications).
- gate_7_export_consistency: ready (canonical artifact metadata present).

## Confidence

- Overall confidence: Medium-High.
- Caveat: FAA/CISA captures in this pass are program and dataset governance sources; add exploit-specific advisories for higher tactical fidelity.

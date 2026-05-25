# Non-Conference Advisory Digest: CISA, NIST, FAA, EASA, ATT&CK ICS

- digest_timestamp_utc: 2026-05-24
- objective: seed non-conference authoritative threat context for aerospace and ICS-adjacent modeling

## Executive Synthesis

1. NIST and ATT&CK ICS sources are immediately usable for control objectives, adversary behavior mapping, and detection engineering.
1. EASA cybersecurity FAQ content provides governance and resilience framing that maps to aviation safety assurance narratives.
1. CISA and FAA machine-extractable retrieval paths were not stable in this run; maintain documented placeholders and validate with manual source capture.

## Source Notes By Organization

### CISA

- attempted_url_1: https://www.cisa.gov/news-events/cybersecurity-advisories
- attempted_url_2: https://www.cisa.gov/resources-tools/resources/ics-recommended-practices
- retrieval_status: blocked/redirected to DHS NTAS
- usable_content: no reliable source body extracted in this run
- threat-model use: keep as required authority source pending manual capture

### NIST

- source_url: https://www.nist.gov/publications/guide-industrial-control-systems-ics-security
- retrieval_status: success
- key takeaways:
  - ICS environments require security engineering that preserves operational safety and availability constraints.
  - Foundational controls include architecture segmentation, asset awareness, and disciplined change control.
  - Risk treatment must account for legacy components and constrained patching windows.

### FAA

- attempted_url_1: https://www.faa.gov/air_traffic/technology/cybersecurity
- attempted_url_2: https://www.faa.gov/about/office_org/headquarters_offices/ang/offices/office-cybersecurity-and-advanced-technology
- retrieval_status: failed (no meaningful extraction / 404)
- usable_content: no reliable source body extracted in this run
- threat-model use: retain FAA slot in digest and complete with manual authoritative source capture

### EASA

- source_url: https://www.easa.europa.eu/en/the-agency/faqs/cybersecurity
- retrieval_status: success (FAQ index extraction)
- key takeaways:
  - EASA frames cyber resilience as aviation-system-wide and safety-relevant.
  - Regulatory and operational stakeholders are expected to address vulnerabilities across aviation structures.
  - Governance and preparedness implications include coordination, awareness, and role clarity.

### MITRE ATT&CK ICS

- source_url: https://attack.mitre.org/versions/v14/matrices/ics/
- retrieval_status: success
- key takeaways:
  - ATT&CK ICS matrix provides tactic-technique decomposition for adversary behavior modeling.
  - Useful for traceability from threat events to detection and mitigation controls.
  - Supports scenario-based mapping for remote service abuse, credential misuse, and process-impact outcomes.

## Recommended Follow-On

1. Perform manual browser capture for stable CISA and FAA pages and store artifacts under source_copies/raw with matching extracted docs.
1. Cross-map ATT&CK ICS technique IDs and NIST SP 800-82 controls into the project traceability matrix.
1. Add an authority confidence column to downstream ingestion outputs (official standard, regulator, secondary reference).

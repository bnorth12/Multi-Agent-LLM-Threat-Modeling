# Source Capture Queue

## Status Legend

- `pending`: source identified but no capture stored.
- `captured`: source text/artifact stored with metadata.
- `normalized`: ingestion-ready extracted text created.

## Queue

| Category | Source URL | Type | Status | Notes |
| --- | --- | --- | --- | --- |
| conference | https://www.blackhat.com/us-23/briefings/schedule/index.html#lessons-learned-from-the-ka-sat-cyberattack-response-mitigation-and--information-sharing-34478 | abstract page | normalized | captured via schedule page; normalized to SC-001 |
| conference | https://i.blackhat.com/USA-22/Wednesday/US-22-Wouters-Glitched-On-Earth.pdf | slide deck | normalized | primary PDF blocked; fallback abstract normalized to SC-002 |
| conference | https://i.blackhat.com/BH-US-23/Presentations/US-23-Tokarev-Code16-16-zero-day-vulnerabilities.pdf | slide deck | normalized | primary PDF blocked; fallback abstract normalized to SC-003 |
| conference | https://defcon.org/html/defcon-32/dc-32-speakers.html | speaker abstracts | normalized | normalized curated notes to SC-004; verify with manual pull |
| standards | https://datatracker.ietf.org/doc/html/rfc8446 | RFC | normalized | datatracker fallback to rfc-editor text normalized to SC-005 |
| standards | https://datatracker.ietf.org/doc/html/rfc9147 | RFC | normalized | datatracker blocked; rfc-editor text normalized to SC-006 |
| standards | https://en.wikipedia.org/wiki/ARINC_429 | reference summary | normalized | captured summary normalized to SC-007 |
| standards | https://en.wikipedia.org/wiki/MIL-STD-1553 | reference summary | normalized | captured summary normalized to SC-008 |
| assurance | https://en.wikipedia.org/wiki/ARINC_653 | reference summary | normalized | captured summary normalized to SC-009 |
| assurance | https://en.wikipedia.org/wiki/Separation_kernel | reference summary | normalized | captured summary normalized to SC-010 |
| cti | https://www.nist.gov/publications/guide-industrial-control-systems-ics-security | publication page | normalized | captured and normalized to SC-011 for advisory and maintenance-chain CTI |
| cti | https://www.easa.europa.eu/en/faq/46472 | FAQ answer | normalized | captured and normalized to SC-012 for aviation exposure-risk framing |
| cti | https://www.easa.europa.eu/en/faq/46473 | FAQ answer | normalized | captured and normalized to SC-013 for regulator role mapping |
| cti | https://attack.mitre.org/versions/v14/matrices/ics/ | matrix page | normalized | captured and normalized to SC-014 for ATT&CK ICS mapping |
| cti | https://raw.githubusercontent.com/cisagov/kev-data/develop/README.md | KEV dataset governance | normalized | substantive alternate source normalized to SC-015; includes KEV format/cadence/governance signals |
| cti | https://www.faa.gov/air_traffic/technology/cinp | NAS network program page | normalized | substantive alternate source normalized to SC-016; supported by SWIM and DataComm pages |
| cti | https://www.a-isac.com/ | aviation ISAC public mission page | normalized | seeded and normalized to SC-017; member-only tactical detail remains out-of-scope |
| cti | https://spaceisac.org/newsroom/ | space ISAC public newsroom | normalized | seeded and normalized to SC-018; public trend signals with membership caveat |
| cti | https://www.eurocontrol.int/cybersecurity | aviation cybersecurity program page | normalized | seeded and normalized to SC-019; includes EATM-CERT and deliverables references |
| cti | https://www.easa.europa.eu/en/domains/cybersecurity | regulator cybersecurity publication index | normalized | seeded and normalized to SC-020; guidance index suitable for mitigation mapping |
| cti | https://www.cert.europa.eu/publications | CERT-EU publications feed | normalized | seeded and normalized to SC-021; cross-sector supporting evidence |
| cti | https://raw.githubusercontent.com/cisagov/kev-data/develop/README.md | KEV schema/governance mirror | normalized | seeded and normalized to SC-022; candidate for next manifest promotion |

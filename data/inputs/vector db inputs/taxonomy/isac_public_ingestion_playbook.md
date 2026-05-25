# ISAC Public Ingestion Playbook

## Purpose

Define a repeatable process for using public-facing ISAC and adjacent authoritative sources when member-only intelligence feeds are unavailable.

## Scope

- Aviation and space threat signals for threat-vector realism.
- Attack-surface expansion for aerospace systems and supporting ground ecosystems.
- Mitigation evidence suitable for HITL gate checks.

## Public Source Baseline (No Membership Required)

### Primary Sector Communities

- Aviation ISAC public site: https://www.a-isac.com/
- Space ISAC public site: https://spaceisac.org/

### Sector-Adjacent Authoritative Sources

- EUROCONTROL cybersecurity: https://www.eurocontrol.int/cybersecurity
- EASA cybersecurity domain publications: https://www.easa.europa.eu/en/domains/cybersecurity
- FAA SWIM security/governance context: https://www.faa.gov/air_traffic/technology/swim
- CISA KEV public machine-readable mirror: https://raw.githubusercontent.com/cisagov/kev-data/develop/README.md
- MITRE ATT&CK ICS matrix: https://attack.mitre.org/matrices/ics/
- NIST SP 800-82 ICS baseline: https://www.nist.gov/publications/guide-industrial-control-systems-ics-security
- CERT-EU publications and advisories: https://www.cert.europa.eu/publications

## Intake Rules

1. Prefer official program pages, advisories, and publication repositories over press reposts.
1. Capture source metadata even when content is high-level (community news, program updates, event summaries).
1. Mark each source with `access_tier` as `public` or `member_restricted`.
1. Treat member-only claims as unverifiable unless a public corroboration source exists.
1. Use at least one technical corroboration source for each high-impact threat assertion.

## Mapping to Threat Modeling Outputs

### Threat Vectors

- Convert observed incidents and campaign language into STRIDE-aligned scenarios.
- Map behavior signals to ATT&CK ICS techniques where relevant.

### Attack Surfaces

- Space: mission operations, TT&C pathways, payload command chains, ground segment, supply chain.
- Aviation: ATM/ANS data exchange, SWIM services, maintenance/update paths, airport and service-provider interfaces.

### Mitigations

- Elevate recommendations that include concrete governance or engineering controls.
- Tag control maturity as `conceptual`, `operational`, or `verified`.

## HITL Gate Usage

- `gate_4_threat_plausibility`: public ISAC and regulator evidence can qualify threats as plausible when corroborated.
- `gate_5_mitigation_adequacy`: only promote controls with implementation detail or repeated cross-source support.
- `gate_7_export_consistency`: require provenance paths and schema-complete metadata before export.

## Evidence Quality Rubric

- `high`: public source includes technical detail, exploit/control specifics, and corroboration.
- `medium-high`: official source with strong sector relevance and partial technical detail.
- `medium`: official source with strategic/program-level signal but limited technical specifics.
- `low`: discovery placeholder or uncorroborated public claim.

## Capture Workflow

1. Add candidate source to `source_copies/manifests/manifest_isac_extension.csv`.
1. Capture raw notes into `source_copies/raw/SC-XXX.md`.
1. Normalize extracted content into `source_copies/extracted/SC-XXX_extracted.md`.
1. Add canonical manifest row in `source_copies/manifests/manifest.csv`.
1. Link resulting artifact into Aerospace CTI advisory/backlog documents.

## Public-Only Gap Handling

- If member data is unavailable, explicitly set `coverage_gap_reason` to `membership_required`.
- Add fallback public sources and map what evidence remains missing.
- Do not infer IOC-level specifics from community marketing or event pages.

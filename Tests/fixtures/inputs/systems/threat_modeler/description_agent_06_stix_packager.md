# Agent 06 — STIX Packager

## Theory of Operation

**What:** Agent 06 transforms threat-model data (system identity, threats, mitigations) from the canonical graph into a valid STIX 2.1 bundle—a standardized, interoperable JSON artifact containing identity, attack-pattern, course-of-action, and relationship objects that can be consumed by security information and event management (SIEM) systems, threat intelligence platforms, and external risk management tools.

**When:** Agent 06 executes sixth (final core threat-generation stage) in the pipeline, immediately after Agent 05 populates threats. Its output (STIX 2.1 bundle JSON) is consumed by the orchestrator for artifact download and file system export. STIX packaging must occur after threat generation because bundles represent the complete, approved threat model; only flows with generated threats contribute attack-pattern objects to the bundle.

**Why:** Organizations integrate threat models with security operations platforms, enterprise risk management systems, and third-party threat intelligence services. Raw canonical graphs are internal representations suitable for the threat modeler's LLM pipeline but not for external consumption. STIX 2.1 is a standardized cybersecurity information exchange format (MITRE standard) that enables threat models to be exported, shared with external parties, imported into SOC tools, and correlated with live security events. Standardization also enables long-term interoperability: a STIX bundle generated today remains machine-readable and actionable in future tools. Additionally, STIX relationship objects (attack-pattern → mitigation, threat-actor → attack-pattern) enable security analysts to understand which controls map to which threats, supporting risk-based prioritization of remediation efforts.

**How:** The agent executes five steps: **(1) Fetch** — retrieves threat-populated canonical graph from Agent 05; extracts system identity, all threats (from qualified flows), and mitigation recommendations. **(2) Build STIX Objects** — constructs individual STIX objects: (a) identity object representing the modeled system; (b) attack-pattern object for each unique threat (name = threat name, description = threat description, external_references include MITRE ATT&CK, CAPEC, CWE); (c) course-of-action object for each mitigation; (d) relationship objects linking identity→attack-pattern (system uses/experiences threat) and course-of-action→attack-pattern (control mitigates threat). **(3) Validate STIX** — validates each object: required fields (type, id, spec_version, created, modified), UUID format compliance, reference integrity (all relationship sources/targets resolve to existing objects), schema conformance. **(4) Bundle** — wraps all objects into a STIX 2.1 bundle container with bundle type and spec_version. **(5) Serialize & Emit** — converts bundle to JSON; returns to orchestrator for file download and export.

**Who:** Agent 05 produces the threat-populated graph. Agent 06 depends on STIX 2.1 specification knowledge and UUID generation. Downstream consumers of the STIX bundle: external SIEM platforms, threat intelligence services, risk management tools, and security stakeholders (who use the bundle for interagency threat sharing or import into SOC dashboards). The orchestrator manages STIX bundle downloads and file persistence.

## High-Level Interfaces

$2### Input Interfaces

- **Threat-Populated Graph** — Output from Agent 05; contains all threats with MITRE ATT&CK, CAPEC, CWE references and likelihood/impact ratings
- **STIX 2.1 Schema** — Standardized structure for identity, attack-pattern, course-of-action, relationship, and bundle objects

$2### Output Interfaces

- **STIX 2.1 Bundle JSON** — Machine-readable cybersecurity information artifact with standardized threat representation; ready for export, import into SOC tools, or interagency threat sharing
- **Validation Status** — Indicates STIX schema compliance, object count (identities, attack-patterns, relationships), reference integrity

$2### Internal Processing Interfaces

- **STIX Object Arrays** — Individual identity, attack-pattern, course-of-action, and relationship objects before bundling

## Component Pieces and Parts

$2### Graph Fetcher
Retrieves threat-populated canonical graph from orchestrator state (produced by Agent 05); extracts system identity metadata, all threat objects from qualified flows, and mitigation recommendations (if present); validates graph schema compliance before passing to STIX builder.
$2### STIX Object Builder
Constructs individual STIX 2.1 objects with required fields (type, id, spec_version, created, modified): (1) identity object (identity_class = "system", name = system name); (2) attack-pattern object per unique threat (external_references field includes MITRE ATT&CK, CAPEC, CWE); (3) course-of-action object per mitigation (name, description); (4) relationship objects linking identity→attack-pattern and course-of-action→attack-pattern. Assigns UUIDs to all objects.
$2### Validation Engine
Validates all STIX objects: checks that required fields (type, id, spec_version, created, modified) are present and non-empty; validates UUID format; validates reference integrity (all relationship source_ref and target_ref point to existing objects); ensures all object properties conform to STIX 2.1 schema; rejects non-compliant objects with detailed error.
$2### STIX Bundler
Creates STIX 2.1 bundle container object with type="bundle", spec_version="2.1", id (UUID), created, modified, and objects array containing all identity, attack-pattern, course-of-action, and relationship objects; validates bundle structure.
$2### JSON Emitter
Serializes STIX bundle object to JSON; ensures proper escaping and formatting; returns to orchestrator for file download and persistence; optionally annotates bundle with threat model metadata (run timestamp, system name, analyst, etc.).

## Trust Boundaries

**External Consumption Boundary** — STIX bundle is exported to external systems (SIEM, threat intelligence platforms, third-party risk tools); bundle contents are visible to external consumers; sensitive information (component IDs, internal naming conventions) may be exposed; consider data minimization and sanitization before export.

**Schema Compliance Boundary** — Bundle must strictly conform to STIX 2.1 specification; downstream tools rely on standard structure; non-compliant bundles may be rejected or parsed incorrectly by external systems.

## Error Handling

- **Missing Threats** — If no flows generated threats, bundle contains identity object but no attack-pattern objects; valid but empty threat export
- **Invalid Object UUIDs** — UUID generation or validation fails; detailed error indicates which object failed
- **Reference Integrity Failure** — Relationship references non-existent object; validation engine rejects with error
- **STIX Schema Violation** — Object missing required field or field has wrong type; validation engine rejects with error
- **Serialization Failure** — JSON encoding fails (e.g., circular references); detailed error emitted

## Operational Constraints

- **STIX 2.1 Compliance** — All objects must conform to STIX 2.1 specification; custom fields not in standard schema rejected
- **UUID Format** — All object IDs must follow `type--uuid` format (e.g., `attack-pattern--a1b2c3d4-...`)
- **Relationships** — All relationship objects must have source_ref and target_ref pointing to existing objects; dangling references rejected
- **No Edits Post-Export** — STIX bundles are final artifacts; edits require re-running threat model and re-packaging

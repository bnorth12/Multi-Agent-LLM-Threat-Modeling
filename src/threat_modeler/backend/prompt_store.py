"""File-backed per-agent prompt store.

Pure Python — no Streamlit dependency.  Stores agent system prompts,
version histories, and temperature settings in a JSON file so they persist
across process restarts and are available to any execution context (CLI, web
server, or test runner) without a Streamlit session.

Public API (mirrors ``ui/prompt_store.py``)
-------------------------------------------
get_prompt(agent_id)              -> str
set_prompt(agent_id, text, actor) -> None
get_history(agent_id)             -> list[VersionEntry]
revert_to(agent_id, idx, actor)   -> None
get_temperature(agent_id)         -> float
set_temperature(agent_id, value)  -> None
reset_to_default(agent_id, actor) -> None
is_modified(agent_id)             -> bool
get_default_prompt(agent_id)      -> str

All functions raise ``KeyError`` if *agent_id* is not in ``AGENT_IDS``.
``set_temperature`` raises ``ValueError`` for values outside [0.0, 2.0].

Thread safety
-------------
A module-level ``threading.Lock`` protects all mutations to the global
default store.  A ``PromptStore`` instance can also be used directly when
tests need isolated state (pass ``store_path=None`` for in-memory-only).
"""

from __future__ import annotations

import datetime
import json
import os
import threading
from pathlib import Path
from typing import NamedTuple, Optional

# ---------------------------------------------------------------------------
# Agent catalogue
# ---------------------------------------------------------------------------

AGENT_IDS: tuple[str, ...] = (
    "agent_01",
    "agent_02",
    "agent_03",
    "agent_04",
    "agent_05",
    "agent_06",
    "agent_07",
    "agent_08",
    "agent_09",
)

AGENT_LABELS: dict[str, str] = {
    "agent_01": "01 — Input Normalizer",
    "agent_02": "02 — Hierarchical Context Builder",
    "agent_03": "03 — Trust Boundary Validator",
    "agent_04": "04 — STRIDE Scorer",
    "agent_05": "05 — Concrete Threat Generator",
    "agent_06": "06 — STIX Packager",
    "agent_07": "07 — Mitigation Generator",
    "agent_08": "08 — Diagram Generator",
    "agent_09": "09 — Human Report Writer",
}

_CANONICAL_GRAPH_EXPECTED_OUTPUT = (
    '{\n'
    '  "metadata": {"generation_timestamp": "", "model_level": "system"},\n'
    '  "system": {\n'
    '    "name": "UAS system",\n'
    '    "description": "",\n'
    '    "mission_criticality": "undetermined",\n'
    '    "safety_criticality": "undetermined"\n'
    '  },\n'
    '  "subsystems": [\n'
    '    {"id": "ss_nav", "name": "Navigation", "description": "", "parent_system": "UAS system"}\n'
    '  ],\n'
    '  "components": [\n'
    '    {"id": "c_mc", "name": "Mission Computer", "parent_subsystem": "ss_nav", "hardware": "hosted", "software_modules": ["mc.core"], "description": ""}\n'
    '  ],\n'
    '  "functions": [],\n'
    '  "interfaces": [\n'
    '    {\n'
    '      "id": "if_001",\n'
    '      "name": "Nav Feed",\n'
    '      "description": "",\n'
    '      "from_node": "c_sensor",\n'
    '      "to_node": "c_mc",\n'
    '      "interface_type": "component-component",\n'
    '      "protocol": "ARINC-429",\n'
    '      "data_items": ["position_fix"],\n'
    '      "trust_boundary_crossing": false,\n'
    '      "trust_boundary_name": "",\n'
    '      "stride": {\n'
    '        "S": 0, "S_justification": "Not scored yet.",\n'
    '        "T": 0, "T_justification": "Not scored yet.",\n'
    '        "R": 0, "R_justification": "Not scored yet.",\n'
    '        "I": 0, "I_justification": "Not scored yet.",\n'
    '        "D": 0, "D_justification": "Not scored yet.",\n'
    '        "E": 0, "E_justification": "Not scored yet."\n'
    '      },\n'
    '      "threats": []\n'
    '    }\n'
    '  ]\n'
    '}'
)

_CANONICAL_GRAPH_WITH_THREAT_EXPECTED_OUTPUT = (
    '{\n'
    '  "metadata": {"generation_timestamp": "", "model_level": "system"},\n'
    '  "system": {\n'
    '    "name": "UAS system",\n'
    '    "description": "",\n'
    '    "mission_criticality": "undetermined",\n'
    '    "safety_criticality": "undetermined"\n'
    '  },\n'
    '  "subsystems": [\n'
    '    {"id": "ss_nav", "name": "Navigation", "description": "", "parent_system": "UAS system"}\n'
    '  ],\n'
    '  "components": [\n'
    '    {"id": "c_mc", "name": "Mission Computer", "parent_subsystem": "ss_nav", "hardware": "hosted", "software_modules": ["mc.core"], "description": ""}\n'
    '  ],\n'
    '  "functions": [],\n'
    '  "interfaces": [\n'
    '    {\n'
    '      "id": "if_001",\n'
    '      "name": "Nav Feed",\n'
    '      "description": "",\n'
    '      "from_node": "c_sensor",\n'
    '      "to_node": "c_mc",\n'
    '      "interface_type": "component-component",\n'
    '      "protocol": "ARINC-429",\n'
    '      "data_items": ["position_fix"],\n'
    '      "trust_boundary_crossing": true,\n'
    '      "trust_boundary_name": "Navigation Boundary",\n'
    '      "stride": {\n'
    '        "S": 3, "S_justification": "Source authentication is weak.",\n'
    '        "T": 2, "T_justification": "Integrity checks are limited.",\n'
    '        "R": 1, "R_justification": "Audit exists but is partial.",\n'
    '        "I": 2, "I_justification": "Unencrypted metadata may leak.",\n'
    '        "D": 2, "D_justification": "Single bus path can be saturated.",\n'
    '        "E": 1, "E_justification": "Privilege boundaries exist."\n'
    '      },\n'
    '      "threats": [\n'
    '        {\n'
    '          "name": "Navigation data spoofing",\n'
    '          "description": "Adversary injects crafted ARINC-429 frames.",\n'
    '          "mitre_attack_technique": ["ATT&CK:T0856 - Spoof Reporting Message"],\n'
    '          "capec_id": "CAPEC-148 - Content Spoofing",\n'
    '          "cwe_id": "CWE-290 - Authentication Bypass by Spoofing",\n'
    '          "likelihood": 3,\n'
    '          "impact": 5,\n'
    '          "mitigations_technical": [\n'
    '            {"control_id": "M-001", "title": "Bus integrity validation", "description": "Validate source integrity and sequence consistency.", "residual_risk_after_control": 2}\n'
    '          ],\n'
    '          "mitigations_administrative": [\n'
    '            {"control_id": "M-010", "title": "Secure maintenance policy", "description": "Restrict and log maintenance bus access.", "residual_risk_after_control": 3}\n'
    '          ]\n'
    '        }\n'
    '      ]\n'
    '    }\n'
    '  ]\n'
    '}'
)

_CANONICAL_GRAPH_BOUNDARY_EXPECTED_OUTPUT = (
    _CANONICAL_GRAPH_EXPECTED_OUTPUT
    .replace('"trust_boundary_crossing": false', '"trust_boundary_crossing": true')
    .replace('"trust_boundary_name": ""', '"trust_boundary_name": "Cross-Domain Boundary"')
)

_DEFAULT_PROMPTS: dict[str, str] = {
    "agent_01": {
        "prompt": (
            "Agent 01 Input Normalizer and Graph Builder\n\n"
            "Purpose:\n"
            "Convert raw narrative and tabular architecture input into canonical graph JSON.\n\n"
            "Inputs:\n"
            "- raw_text narrative\n"
            "- tables parsed from ICD rows\n"
            "- optional prior state context\n\n"
            "Outputs:\n"
            "- complete canonical graph JSON with metadata, system, subsystems, components, functions, interfaces\n\n"
            "Preconditions:\n"
            "- at least one architecture evidence source is provided\n"
            "- parser output may be noisy, incomplete, or duplicative\n\n"
            "Postconditions:\n"
            "- output is a single canonical graph JSON document\n"
            "- IDs and topology are stable and deterministic for identical evidence\n\n"
            "System Prompt:\n"
            "You are an aerospace systems engineering parser. "
            "Output ONLY the complete canonical graph JSON with no prose and no markdown fences.\n\n"
            "Rules:\n"
            "1. Include every valid subsystem/component/interface present in input evidence.\n"
            "2. Never invent interfaces that are unsupported by source data.\n"
            "3. Normalize identifiers deterministically and preserve stable IDs when present.\n"
            "4. Map tabular flow rows into interfaces with from_node, to_node, protocol, data_items.\n"
            "5. trust_boundary_crossing must be a JSON boolean (true or false), never a string.\n"
            "6. Keep STRIDE fields initialized but unscored (0 with justification placeholders).\n"
            "7. Return schema-valid JSON only.\n\n"
            "Validation Rules:\n"
            "- include required top-level keys: metadata, system, subsystems, components, functions, interfaces\n"
            "- emit arrays for subsystems/components/functions/interfaces even when empty\n"
            "- preserve known IDs from evidence unless impossible to parse\n\n"
            "Failure Handling:\n"
            "- if evidence conflicts, preserve both candidates with conservative descriptions instead of dropping data\n"
            "- if a field is unknown, emit an empty string or empty array (never prose placeholders)"
        ),
        "expected_output": _CANONICAL_GRAPH_EXPECTED_OUTPUT
    },
    "agent_02": {
        "prompt": (
            "Agent 02 Hierarchical Context Builder\n\n"
            "Purpose:\n"
            "Enrich and reconcile canonical graph structure while preserving architecture continuity.\n\n"
            "Inputs:\n"
            "- canonical graph from prior stage\n"
            "- optional existing approved baseline graph\n\n"
            "Outputs:\n"
            "- complete canonical graph JSON with merged hierarchy context\n\n"
            "Preconditions:\n"
            "- prior-stage canonical graph exists\n"
            "- baseline references may contain partial overlap and naming drift\n\n"
            "Postconditions:\n"
            "- hierarchy is internally consistent with stable parent-child links\n"
            "- no top-level entity class is dropped during reconciliation\n\n"
            "System Prompt:\n"
            "You are a hierarchical systems analyst for aerospace threat modeling. "
            "Output ONLY the complete canonical graph JSON with no prose and no markdown fences.\n\n"
            "Rules:\n"
            "1. Merge non-destructively and preserve approved baseline entities and IDs.\n"
            "2. Preserve and refine subsystem/component relationships and parent links.\n"
            "3. Keep all existing interfaces unless explicitly contradicted by stronger evidence.\n"
            "4. Prefer more specific values when conflicts occur; avoid deleting known-good fields.\n"
            "5. Return all top-level arrays (subsystems, components, functions, interfaces).\n"
            "6. Return schema-valid JSON only.\n\n"
            "Validation Rules:\n"
            "- every component parent_subsystem must resolve to an existing subsystem\n"
            "- interface endpoints must resolve to existing nodes where evidence permits\n"
            "- if metadata exists, preserve it unless superseded by stronger validated context\n\n"
            "Failure Handling:\n"
            "- if hierarchy is ambiguous, preserve both structures with conservative descriptions\n"
            "- never collapse architecture to a smaller graph due to uncertainty"
        ),
        "expected_output": _CANONICAL_GRAPH_EXPECTED_OUTPUT
    },
    "agent_03": {
        "prompt": (
            "Agent 03 Trust Boundary Validator and Enricher\n\n"
            "Purpose:\n"
            "Determine and label trust boundaries for every interface in the canonical graph.\n\n"
            "Inputs:\n"
            "- canonical graph JSON with interfaces\n"
            "- optional policy and architecture context\n\n"
            "Outputs:\n"
            "- complete canonical graph JSON with trust_boundary_crossing and trust_boundary_name validated\n\n"
            "Preconditions:\n"
            "- interface list is present and parseable\n"
            "- policy context may be missing or incomplete\n\n"
            "Postconditions:\n"
            "- every interface has a boundary decision with consistent naming semantics\n"
            "- boundary annotations remain compatible with downstream STRIDE scoring\n\n"
            "System Prompt:\n"
            "You are a trust boundary auditor for aerospace and cyber-physical systems. "
            "A trust boundary exists wherever data crosses security domains, privilege levels, "
            "safety partitions, network enclaves, external links, or ownership/control boundaries. "
            "Output ONLY the complete canonical graph JSON with no prose and no markdown fences.\n\n"
            "Rules:\n"
            "1. Evaluate every interface for boundary crossing using concrete architecture evidence.\n"
            "2. Treat ambiguous cases conservatively: prefer trust_boundary_crossing=true.\n"
            "3. If crossing=true, trust_boundary_name must be non-empty and specific.\n"
            "4. If trust_boundary_name is non-empty, crossing must be true.\n"
            "5. Preserve all entities and IDs; do not remove interfaces.\n"
            "6. Return schema-valid JSON only.\n\n"
            "Validation Rules:\n"
            "- every interface includes both trust_boundary_crossing and trust_boundary_name\n"
            "- boundary names are concise and domain-specific, not generic placeholders\n"
            "- unchanged fields outside trust-boundary scope remain intact\n\n"
            "Failure Handling:\n"
            "- if evidence is incomplete, mark crossing=true and provide the best conservative boundary label\n"
            "- never emit contradictory boundary fields"
        ),
        "expected_output": _CANONICAL_GRAPH_BOUNDARY_EXPECTED_OUTPUT
    },
    "agent_04": {
        "prompt": (
            "Agent 04 STRIDE Scorer\n\n"
            "Purpose:\n"
            "Assign STRIDE scores and justifications to each interface in the canonical graph.\n\n"
            "Inputs:\n"
            "- canonical graph with trust-boundary enrichment\n\n"
            "Outputs:\n"
            "- complete canonical graph JSON with stride object populated for each interface\n\n"
            "Preconditions:\n"
            "- trust-boundary annotations exist for each interface\n"
            "- architecture evidence is sufficient for risk-informed scoring\n\n"
            "Postconditions:\n"
            "- all STRIDE categories are scored and justified on every interface\n"
            "- output supports downstream threat generation thresholds\n\n"
            "System Prompt:\n"
            "You are an aerospace STRIDE analyst. "
            "Output ONLY the complete canonical graph JSON with no prose and no markdown fences.\n\n"
            "Rules:\n"
            "1. Score S, T, R, I, D, E for every interface using integers 0-5.\n"
            "2. Provide concise, non-empty justification fields for each STRIDE category.\n"
            "3. Maintain consistency with trust boundary context and safety criticality.\n"
            "4. Preserve all entities and IDs; update only stride content and related rationale fields.\n"
            "5. Return schema-valid JSON only.\n\n"
            "Validation Rules:\n"
            "- each interface has all six STRIDE numeric scores and six justification fields\n"
            "- score range is 0-5 only, with integers (no floats or strings)\n"
            "- high scores align with stated boundary and exposure context\n\n"
            "Failure Handling:\n"
            "- if evidence is sparse, assign conservative low-to-moderate scores with explicit rationale\n"
            "- do not leave any STRIDE category unscored"
        ),
        "expected_output": _CANONICAL_GRAPH_EXPECTED_OUTPUT
    },
    "agent_05": {
        "prompt": (
            "Agent 05 Concrete Threat Generator\n\n"
            "Purpose:\n"
            "Generate concrete threats for high-risk interfaces using STRIDE context and grounded cyber-physical evidence.\n\n"
            "Inputs:\n"
            "- canonical graph with STRIDE scores and boundary annotations\n"
            "- optional CTI retrieval evidence and prior analyst notes\n\n"
            "Outputs:\n"
            "- complete canonical graph JSON with threat objects populated on qualifying interfaces\n\n"
            "Preconditions:\n"
            "- STRIDE scoring complete\n\n"
            "Postconditions:\n"
            "- threats are concrete, plausible, and evidence-aligned\n"
            "- non-qualifying interfaces retain empty threat arrays\n\n"
            "System Prompt:\n"
            "You are an aerospace red-team threat analyst.\n"
            "Output ONLY the complete canonical graph JSON with no prose and no markdown fences.\n\n"
            "Rules:\n"
            "1. Generate threats only for interfaces where any STRIDE category score is 3 or higher.\n"
            "2. Preserve all existing entities, IDs, and non-threat fields; only add threat objects.\n"
            "3. Each threat must include taxonomy fields and likelihood/impact values (1-5).\n"
            "4. Format taxonomy values with both ID and human-readable name (for example ATT&CK:T0856 - Spoof Reporting Message).\n"
            "5. Keep mitigations_technical and mitigations_administrative as empty arrays at this stage.\n"
            "6. If evidence is weak, emit conservative threats with explicit low-confidence rationale in description.\n"
            "7. Return schema-valid JSON only.\n\n"
            "Reference Examples:\n"
            "- docs/agents/agent_05_concrete_threat_generator_examples.md\n"
        ),
        "expected_output": _CANONICAL_GRAPH_WITH_THREAT_EXPECTED_OUTPUT
    },
    "agent_06": {
        "prompt": (
            "Agent 06 STIX Packager\n\n"
            "Purpose:\n"
            "Convert canonical threat content into a valid STIX 2.1 bundle for downstream exchange.\n\n"
            "Inputs:\n"
            "- canonical graph with threats and taxonomy mappings\n"
            "- optional prior STIX context for stable actor naming\n\n"
            "Outputs:\n"
            "- STIX 2.1 bundle JSON containing attack-pattern, threat-actor, and relationship objects\n\n"
            "System Prompt:\n"
            "You are a STIX 2.1 packaging specialist for aerospace threat intelligence. "
            "Output ONLY STIX JSON with no prose and no markdown fences.\n\n"
            "Rules:\n"
            "1. Emit top-level type=bundle and spec_version=2.1.\n"
            "2. Include only schema-valid STIX object types and IDs for this stage scope.\n"
            "3. Preserve threat semantics from canonical content; do not invent unrelated campaigns.\n"
            "4. Create relationship objects that tie threat actors to attack patterns when evidence exists.\n"
            "5. Keep output deterministic for repeated identical inputs where feasible.\n"
            "6. Return parseable JSON only."
        ),
        "expected_output": (
            '{\n'
            '  "type": "bundle",\n'
            '  "id": "bundle--11111111-1111-4111-8111-111111111111",\n'
            '  "spec_version": "2.1",\n'
            '  "objects": [\n'
            '    {"type": "attack-pattern", "spec_version": "2.1", "id": "attack-pattern--22222222-2222-4222-8222-222222222222", "name": "Navigation data spoofing"},\n'
            '    {"type": "relationship", "spec_version": "2.1", "id": "relationship--33333333-3333-4333-8333-333333333333", "relationship_type": "uses", "source_ref": "threat-actor--44444444-4444-4444-8444-444444444444", "target_ref": "attack-pattern--22222222-2222-4222-8222-222222222222"},\n'
            '    {"type": "threat-actor", "spec_version": "2.1", "id": "threat-actor--44444444-4444-4444-8444-444444444444", "name": "RF-capable adversary"}\n'
            '  ]\n'
            '}'
        )
    },
    "agent_07": {
        "prompt": (
            "Agent 07 Mitigation Generator\n\n"
            "Purpose:\n"
            "Generate actionable technical and administrative mitigations for each threat in the canonical graph.\n\n"
            "Inputs:\n"
            "- canonical graph with populated threat objects\n"
            "- optional controls context and organizational constraints\n\n"
            "Outputs:\n"
            "- complete canonical graph JSON with mitigation entries attached per threat\n\n"
            "System Prompt:\n"
            "You are a mitigation engineer for aerospace and cyber-physical systems. "
            "Output ONLY the complete canonical graph JSON with no prose and no markdown fences.\n\n"
            "Rules:\n"
            "1. Preserve all existing threat records and IDs; do not remove threats.\n"
            "2. Populate mitigations_technical and mitigations_administrative with concrete controls when warranted.\n"
            "3. Each mitigation entry must include control_id, title, description, and residual_risk_after_control (1-5).\n"
            "4. Keep mitigations traceable to threat context and protocol/boundary characteristics.\n"
            "5. If mitigation evidence is weak, provide conservative controls with explicit assumptions.\n"
            "6. Return schema-valid JSON only."
        ),
        "expected_output": _CANONICAL_GRAPH_WITH_THREAT_EXPECTED_OUTPUT
    },
    "agent_08": {
        "prompt": (
            "Agent 08 Diagram Generator\n\n"
            "Purpose:\n"
            "Generate Mermaid data-flow diagrams with adaptive abstraction levels for architecture and risk review.\n\n"
            "Inputs:\n"
            "- canonical graph with boundaries, risks, threats, and mitigations\n\n"
            "Outputs:\n"
            "- Mermaid diagram set with one mandatory top-context diagram and optional deeper levels\n\n"
            "Preconditions:\n"
            "- threat and mitigation enrichment complete\n\n"
            "Postconditions:\n"
            "- diagram set remains readable at each abstraction level\n"
            "- diagram set uses consistent node IDs across diagrams when the same entity appears\n\n"
            "System Prompt:\n"
            "You are an aerospace data-flow diagram specialist.\n\n"
            "Rules:\n"
            "1. Emit MERMAID_LEVEL0 in a mermaid fenced block for every run.\n"
            "2. Emit additional levels only when complexity or risk density justifies deeper decomposition.\n"
            "3. If emitting additional levels, use sequential markers with no gaps (MERMAID_LEVEL0..MERMAID_LEVELN).\n"
            "4. Keep diagram labels concise and include per-category STRIDE maxima where available.\n"
            "5. Preserve trust-boundary visibility and include a short legend in each emitted diagram.\n"
            "6. Prefer split-focused diagrams over dense unreadable single diagrams.\n"
            "7. Return Mermaid markdown only, matching required section marker format.\n\n"
            "Validation Rules:\n"
            "- `MERMAID_LEVEL0` must exist\n"
            "- additional levels are optional and model-determined\n"
            "- if additional levels are emitted, they must be sequential with no gaps (0,1,2,...,N)\n"
            "- each emitted section must contain one Mermaid fenced block\n"
            "- each interface label should include per-category STRIDE maxima when STRIDE data exists\n\n"
            "Failure Handling:\n"
            "- if deeper decomposition is not justified by complexity, emit only `MERMAID_LEVEL0` and `MERMAID_LEVEL1`\n"
            "- if a candidate deep diagram would be unreadable, split it into multiple focused lower-level diagrams\n"
            "- if partition/software stack detail (for example hypervisors, virtual machines, ARINC 653 partitions) is not present in canonical evidence, do not invent it\n\n"
            "Reference Examples:\n"
            "- docs/agents/agent_08_diagram_generator_examples.md"
        ),
        "expected_output": (
            "MERMAID_LEVEL0\n"
            "```mermaid\n"
            "flowchart TD\n"
            "  UAS[\"UAS system\"] -->|\"ARINC-429 S:3 T:2 R:1 I:2 D:2 E:1\"| MC[\"Mission Computer\"]\n"
            "  subgraph LEGEND[\"Legend\"]\n"
            "    L1[\"Labels show per-category STRIDE maxima\"]\n"
            "  end\n"
            "```\n\n"
            "MERMAID_LEVEL1\n"
            "```mermaid\n"
            "flowchart TD\n"
            "  NAV[\"Navigation Sensor\"] -->|\"position_fix S:3 T:2 R:1 I:2 D:2 E:1\"| MC[\"Mission Computer\"]\n"
            "  MC --> FC[\"Flight Control\"]\n"
            "```"
        )
    },
    "agent_09": {
        "prompt": (
            "Agent 09 Report Writer\n\n"
            "Purpose:\n"
            "Produce a governance-ready markdown threat model report from approved run artifacts.\n\n"
            "Inputs:\n"
            "- canonical graph with threat and mitigation content\n"
            "- generated Mermaid/STIX artifacts and gate decisions\n"
            "- optional analyst notes and rationale text\n\n"
            "Outputs:\n"
            "- markdown report suitable for security and safety review boards\n\n"
            "System Prompt:\n"
            "You are a technical report writer for aerospace threat governance. "
            "Output markdown only with no surrounding prose.\n\n"
            "Rules:\n"
            "1. Include required sections: Executive Summary, Methodology, System Scope, Trust Boundaries, STRIDE Findings, Top Threats, and Mitigation Mapping.\n"
            "2. Use concise, auditable language and preserve evidence traceability to canonical artifacts.\n"
            "3. Do not invent systems, interfaces, threats, or mitigations absent from canonical evidence.\n"
            "4. Keep table and heading structure stable for downstream parsing and export.\n"
            "5. Reference Mermaid artifacts when available; otherwise state that no diagrams were produced.\n"
            "6. Return markdown only."
        ),
        "expected_output": (
            "# Threat Model Report\n"
            "\n"
            "## Executive Summary\n"
            "This report provides a comprehensive threat model for the UAS system, summarizing key risks and recommendations.\n"
            "\n"
            "## Table of Contents\n"
            "1. Executive Summary\n"
            "2. Methodology\n"
            "3. System Overview\n"
            "4. Threat Analysis\n"
            "5. Findings\n"
            "6. Mitigation\n"
            "7. Recommendations\n"
            "8. Mermaid Diagrams\n"
            "9. Appendix\n"
            "\n"
            "## Methodology\n"
            "- Approach: STRIDE, STIX 2.1, MITRE ATT&CK\n"
            "- Data sources: Canonical system model, context graph\n"
            "\n"
            "## System Scope and Description\n"
            "- System Name: UAS\n"
            "- Major Components: Mission Computer, Datalink, Ground Station\n"
            "- Diagram: See Mermaid diagram section\n"
            "\n"
            "## Trust Boundaries\n"
            "- Boundary 1: External RF ingress to mission network.\n"
            "- Boundary 2: Maintenance ingress to onboard compute.\n"
            "\n"
            "## Data Flow Diagrams\n"
            "```mermaid\nflowchart TD\n  A[UAS] -->|Datalink| B[Ground Station]\n```\n"
            "\n"
            "## STRIDE Findings\n"
            "| Threat ID | Description | Severity |\n"
            "|-----------|-------------|----------|\n"
            "| T-001     | Spoofing attack on datalink | High |\n"
            "| T-002     | Data tampering in ground station | Medium |\n"
            "\n"
            "## Top Threats\n"
            "- The datalink is vulnerable to spoofing due to lack of encryption.\n"
            "- Ground station authentication is insufficient.\n"
            "\n"
            "## Mitigation Mapping and Residual Risk\n"
            "- Encrypt datalink communications to prevent spoofing.\n"
            "- Implement multi-factor authentication for ground station access.\n"
        )
    },
}

_DEFAULT_TEMPERATURES: dict[str, float] = {agent: 0.2 for agent in AGENT_IDS}

# Default file location for the global store instance.
_DEFAULT_STORE_PATH = Path(
    os.environ.get(
        "THREAT_MODELER_PROMPT_STORE_PATH",
        str(Path.home() / ".multi_agent_threat_modeler_prompts.json"),
    )
)


# ---------------------------------------------------------------------------
# Version entry
# ---------------------------------------------------------------------------

class VersionEntry(NamedTuple):
    version: int     # 1-based sequence number
    text: str        # prompt text at this version
    actor: str       # role or user identifier
    timestamp: str   # ISO-8601 UTC string


# ---------------------------------------------------------------------------
# PromptStore class
# ---------------------------------------------------------------------------

class PromptStore:
    """Thread-safe, optionally file-backed prompt store.

    Args:
        store_path: Path to the JSON backing file.  Pass ``None`` to use an
                    in-memory-only store (useful for isolated unit tests).
    """

    def __init__(self, store_path: Optional[Path] = _DEFAULT_STORE_PATH) -> None:
        self._lock = threading.Lock()
        self._store_path = store_path
        self._prompts: dict[str, str] = {k: v["prompt"] for k, v in _DEFAULT_PROMPTS.items()}
        self._expected_outputs: dict[str, str] = {k: v["expected_output"] for k, v in _DEFAULT_PROMPTS.items()}
        self._histories: dict[str, list[VersionEntry]] = {
            agent_id: [
                VersionEntry(
                    version=1,
                    text=_DEFAULT_PROMPTS[agent_id]["prompt"],
                    actor="system",
                    timestamp=_utc_now(),
                )
            ]
            for agent_id in AGENT_IDS
        }
        self._temperatures: dict[str, float] = dict(_DEFAULT_TEMPERATURES)

        if store_path is not None:
            self._load_from_disk()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_from_disk(self) -> None:
        if self._store_path is None or not self._store_path.exists():
            return
        try:
            payload = json.loads(self._store_path.read_text(encoding="utf-8"))
        except Exception:
            return
        if not isinstance(payload, dict):
            return

        with self._lock:
            prompts = payload.get("prompts", {})
            if isinstance(prompts, dict):
                for aid in AGENT_IDS:
                    if aid in prompts and isinstance(prompts[aid], str):
                        self._prompts[aid] = prompts[aid]

            expected_outputs = payload.get("expected_outputs", {})
            if isinstance(expected_outputs, dict):
                for aid in AGENT_IDS:
                    if aid in expected_outputs and isinstance(expected_outputs[aid], str):
                        self._expected_outputs[aid] = expected_outputs[aid]

            histories = payload.get("histories", {})
            if isinstance(histories, dict):
                for aid in AGENT_IDS:
                    raw = histories.get(aid)
                    if isinstance(raw, list):
                        entries: list[VersionEntry] = []
                        for item in raw:
                            if isinstance(item, dict):
                                try:
                                    entries.append(
                                        VersionEntry(
                                            version=int(item["version"]),
                                            text=str(item["text"]),
                                            actor=str(item["actor"]),
                                            timestamp=str(item["timestamp"]),
                                        )
                                    )
                                except (KeyError, ValueError):
                                    pass
                        if entries:
                            self._histories[aid] = entries

            temperatures = payload.get("temperatures", {})
            if isinstance(temperatures, dict):
                for aid in AGENT_IDS:
                    val = temperatures.get(aid)
                    if isinstance(val, (int, float)) and 0.0 <= float(val) <= 2.0:
                        self._temperatures[aid] = float(val)

    def _save_to_disk(self) -> None:
        if self._store_path is None:
            return
        payload = {
            "prompts": dict(self._prompts),
            "expected_outputs": dict(self._expected_outputs),
            "histories": {
                aid: [
                    {
                        "version": entry.version,
                        "text": entry.text,
                        "actor": entry.actor,
                        "timestamp": entry.timestamp,
                    }
                    for entry in entries
                ]
                for aid, entries in self._histories.items()
            },
            "temperatures": dict(self._temperatures),
        }
        try:
            self._store_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_agent(self, agent_id: str) -> None:
        if agent_id not in AGENT_IDS:
            raise KeyError(f"Unknown agent_id '{agent_id}'. Must be one of {AGENT_IDS}.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_prompt(self, agent_id: str) -> str:
        self._validate_agent(agent_id)
        with self._lock:
            return self._prompts[agent_id]

    def get_expected_output(self, agent_id: str) -> str:
        self._validate_agent(agent_id)
        with self._lock:
            return self._expected_outputs[agent_id]

    def set_expected_output(self, agent_id: str, example: str) -> None:
        self._validate_agent(agent_id)
        with self._lock:
            self._expected_outputs[agent_id] = example
            self._save_to_disk()

    def set_prompt(self, agent_id: str, text: str, actor: str = "user") -> None:
        self._validate_agent(agent_id)
        with self._lock:
            self._prompts[agent_id] = text
            history = self._histories[agent_id]
            next_version = history[-1].version + 1 if history else 1
            history.append(
                VersionEntry(
                    version=next_version,
                    text=text,
                    actor=actor,
                    timestamp=_utc_now(),
                )
            )
            self._save_to_disk()

    def get_history(self, agent_id: str) -> list[VersionEntry]:
        self._validate_agent(agent_id)
        with self._lock:
            return list(self._histories[agent_id])

    def revert_to(self, agent_id: str, version_index: int, actor: str = "user") -> None:
        self._validate_agent(agent_id)
        with self._lock:
            history = self._histories[agent_id]
            if version_index < 0 or version_index >= len(history):
                raise IndexError(
                    f"version_index {version_index} out of range for agent '{agent_id}' "
                    f"(history length {len(history)})."
                )
            prior = history[version_index]
        self.set_prompt(agent_id, prior.text, actor=f"{actor} (revert to v{prior.version})")

    def get_temperature(self, agent_id: str) -> float:
        self._validate_agent(agent_id)
        with self._lock:
            return self._temperatures[agent_id]

    def set_temperature(self, agent_id: str, value: float) -> None:
        self._validate_agent(agent_id)
        if not (0.0 <= value <= 2.0):
            raise ValueError(f"Temperature must be in [0.0, 2.0]; got {value}.")
        with self._lock:
            self._temperatures[agent_id] = value
            self._save_to_disk()

    def reset_to_default(self, agent_id: str, actor: str = "user") -> None:
        self._validate_agent(agent_id)
        self.set_prompt(agent_id, _DEFAULT_PROMPTS[agent_id]["prompt"], actor=f"{actor} (reset to default)")
        with self._lock:
            self._expected_outputs[agent_id] = _DEFAULT_PROMPTS[agent_id]["expected_output"]
            self._temperatures[agent_id] = _DEFAULT_TEMPERATURES[agent_id]
            self._save_to_disk()

    def is_modified(self, agent_id: str) -> bool:
        self._validate_agent(agent_id)
        with self._lock:
            return self._prompts[agent_id] != _DEFAULT_PROMPTS[agent_id]["prompt"]

    def get_default_prompt(self, agent_id: str) -> str:
        self._validate_agent(agent_id)
        return _DEFAULT_PROMPTS[agent_id]["prompt"]


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Global default store instance
# ---------------------------------------------------------------------------

_default_store = PromptStore(store_path=_DEFAULT_STORE_PATH)


# ---------------------------------------------------------------------------
# Module-level public API (delegates to global store)
# ---------------------------------------------------------------------------

def get_prompt(agent_id: str) -> str:
    """Return the current system prompt for *agent_id* from the global store."""
    return _default_store.get_prompt(agent_id)


def set_prompt(agent_id: str, text: str, actor: str = "user") -> None:
    """Save a new prompt for *agent_id* and record a version history entry."""
    _default_store.set_prompt(agent_id, text, actor)


def get_expected_output(agent_id: str) -> str:
    """Return the current expected output for *agent_id* from the global store."""
    return _default_store.get_expected_output(agent_id)

def set_expected_output(agent_id: str, example: str) -> None:
    """Save a new expected output example for *agent_id*."""
    _default_store.set_expected_output(agent_id, example)


def get_history(agent_id: str) -> list[VersionEntry]:
    """Return full version history for *agent_id*, oldest first."""
    return _default_store.get_history(agent_id)


def revert_to(agent_id: str, version_index: int, actor: str = "user") -> None:
    """Restore a prior prompt version by 0-based history index."""
    _default_store.revert_to(agent_id, version_index, actor)


def get_temperature(agent_id: str) -> float:
    """Return configured model temperature for *agent_id*."""
    return _default_store.get_temperature(agent_id)


def set_temperature(agent_id: str, value: float) -> None:
    """Set model temperature for *agent_id* in [0.0, 2.0]."""
    _default_store.set_temperature(agent_id, value)


def reset_to_default(agent_id: str, actor: str = "user") -> None:
    """Reset prompt and temperature for *agent_id* to defaults."""
    _default_store.reset_to_default(agent_id, actor)


def is_modified(agent_id: str) -> bool:
    """Return True when current prompt differs from default for *agent_id*."""
    return _default_store.is_modified(agent_id)


def get_default_prompt(agent_id: str) -> str:
    """Return default prompt text for *agent_id*."""
    return _default_store.get_default_prompt(agent_id)


def get_store_path() -> str:
    """Return the absolute path of the active prompt store file."""
    return str(_DEFAULT_STORE_PATH)

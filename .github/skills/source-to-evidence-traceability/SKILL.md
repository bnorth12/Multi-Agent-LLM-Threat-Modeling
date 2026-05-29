---
name: source-to-evidence-traceability
description: "Audit full source-to-evidence traceability per requirement across source, architecture/design, implementation, and verification artifacts."
---
# Source-to-Evidence Traceability Skill

## Purpose
Validate requirement coverage using a complete chain model:
source requirement artifact -> architecture/design trace -> implementation evidence -> verification evidence.

## Inputs
- Sprint scope
- Requirement corpus in Requirements/
- Architecture and design docs in docs/architecture and docs/design
- Implementation and test evidence references from planning and traceability artifacts

## Procedure
1. Build requirement inventory from Requirements/ documents.
2. For each requirement ID, capture evidence refs for all four chain legs:
- source refs
- architecture/design refs
- implementation refs
- verification refs
3. Classify each requirement chain as:
- complete (all four legs present)
- partial (one or more legs missing)
- missing-link (critical leg absent for planning readiness)
4. Emit chain-aware findings with requirement text and evidence snippets.
5. Summarize chain completeness ratio and top missing-link clusters.

## Expected Outputs
- Chain completeness summary
- Missing-link breakdown by requirement prefix and evidence type
- Requirement-level findings that include readable requirement text and evidence refs

## Guardrails
- Do not infer evidence where no explicit reference exists.
- Do not stop at first-level ID presence.
- Keep analysis local and file-referenced.

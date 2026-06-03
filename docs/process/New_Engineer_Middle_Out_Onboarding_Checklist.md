# New Engineer Middle-Out Onboarding Checklist

## Purpose

Enable a new engineer to start in the middle of repository documentation and still build correct end-to-end understanding in either direction.

## Entry Points

Pick any one path and complete all linked checks.

### Path A: Start from Process

1. Read docs/process/Governance_and_Traceability_Index.md.
1. Confirm sprint lifecycle phases and enforcement points.
1. Follow links to Definition_of_Done.md and Requirements_and_Issues_Policy.md.
1. Cross-check implementation and test surfaces in src/ and Tests/README.md.
1. Trace one requirement from Requirements/04_Traceability_Matrix.md through planning issues and test evidence.

### Path B: Start from Requirements

1. Read Requirements/README.md and 00_Requirement_Taxonomy.md.
1. Pick one requirement ID in Requirements/04_Traceability_Matrix.md.
1. Locate architecture and design linkage in Requirements/15_End_To_End_Traceability_Attributes_Registry.md.
1. Find corresponding issue tracking in planning/issues/.
1. Verify implementation and tests for that requirement in src/ and Tests/.

### Path C: Start from Implementation

1. Read README.md project concept and architecture summary.
1. Identify one implemented feature area in src/.
1. Link code to issue records in planning/issues/.
1. Link issues to requirements and verification evidence.
1. Confirm architecture and design authority documents cover the same behavior.

## Big-Picture Reconstruction Test

A new engineer should be able to answer all items below after completing one path:

- What problem the system solves and who the operator is.
- How architecture authority maps to design and implementation boundaries.
- How requirements are verified and where evidence is captured.
- Which governance gates are blocking versus advisory.
- What artifacts are active versus historical archives.

## Role-Specific Follow-Ons

- Implementer: read docs/design/software/* and relevant src modules.
- Reviewer: read docs/process/* governance docs and independent_reviews/latest outputs.
- QA and verification: read Tests/README.md, Requirements/05_Verification_Strategy.md, and sprint test execution summaries.

## Completion Record

- Date:
- Engineer:
- Entry path used:
- Requirement traced:
- Gaps observed:
- Follow-up issue created:

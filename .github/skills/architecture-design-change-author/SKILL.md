---
name: architecture-design-change-author
description: "Drive architecture/design update authoring during remediation execution and keep implementation plus verification synchronized to the chosen disposition path."
---
# Architecture/Design Change Author Skill

## Purpose
Ensure architecture/design updates are treated as active execution artifacts rather than deferred documentation.

## Inputs
- Authoring workpack from the disposition planner
- Remediation sprint scope and requirement IDs
- Implementation and verification evidence targets

## Required Hierarchy Fields
- parent capability ID
- child function ID
- decomposition level (L0/L1/L2)
- allocated component/module
- verification method

## Procedure
1. Apply the selected disposition path to architecture/design authoring scope.
2. Keep implementation and verification references synchronized with architecture/design changes.
3. Ensure each remediation slice preserves explicit parent-child decomposition and code-level allocation fields.
4. Surface unresolved gaps before merge or closeout.
5. Preserve evidence needed for independent review and closeout certification.

## Outputs
- Updated architecture/design authoring workpack sections.
- Gap list for missing synchronized updates.
- Hierarchy metadata coverage checklist for each remediation slice.
- Disposition compliance checklist for closeout.

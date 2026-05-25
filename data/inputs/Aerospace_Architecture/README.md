# Aircraft Functional Reference Architecture

## Purpose

This folder provides a canonical, hierarchical functional decomposition of aircraft systems to support architecture analysis, threat alignment, and future vector database ingestion.

## Decomposition Model

The primary level-0 mission functions are:

1. Aviate
1. Navigate
1. Communicate
1. Operate

`Operate` is decomposed by aircraft purpose, including passenger transport and missionized variants.

## Folder Structure

- `00_reference_basis/`: nomenclature, scope boundaries, and reference sources.
- `01_functional_decomposition/`: hierarchical function breakdown by level-0 domain.
- `02_cross_cutting/`: control authority, data flows, and aircraft-type variation overlays.
- `03_mapping_for_threat_alignment/`: templates for linking functions to threats, impacts, and STIX entities.
- `04_platform_structures/`: military and commercial structural variants for flight controls, vehicle management, and mission/passenger systems.
- `05_safety_analysis/`: failure mode and hazard safety-analysis baseline with public-source references.

## Intended Use

- Canonical functional basis for system/software architecture discussions.
- Input corpus for threat-model traceability and impact mapping.
- Future ingestion source for RAG and vector retrieval.

## Notes

- This architecture is function-oriented, not implementation-specific.
- Vendor/program-specific avionics realizations should map into this baseline instead of replacing it.

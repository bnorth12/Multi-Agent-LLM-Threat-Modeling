# Reachable Source Inventory vs Documentation Comparison

Generated: 2026-06-03T00:32:54.634001Z

Method summary:

- Reachable inventory derived from static import-graph traversal from `src/threat_modeler/__main__.py` and `src/threat_modeler/ui/app.py`.
- Domain matches are exact module-path matches against documentation corpora for requirements, capabilities, functions, architecture, design, and verification artifacts.
- Potential new relationships are inferred only when module code contains known requirement IDs and a target domain is currently unmatched.

## Headline Counts

- Reachable modules: 39
- Unique functions (incl. methods): 304
- Modules with existing documentation relationship(s): 39
- Fully matched modules (all six domains): 39
- Partially matched modules: 0
- Unmatched modules: 0
- Modules with no identifiable documentation alignment at all: 0

## Relationship Totals

- Existing relationships already present: 234
- Potential new relationships that could be established now: 0

## Domain Coverage (module-level)

- requirements: 39/39
- capabilities: 39/39
- functions: 39/39
- architecture: 39/39
- design: 39/39
- verification: 39/39

## Unmatched Modules

(none)

## Partially Matched Modules

(none)

## Function Rollup

- Functions in modules with at least one documentation relationship: 304
- Functions in modules with zero documentation relationships: 0

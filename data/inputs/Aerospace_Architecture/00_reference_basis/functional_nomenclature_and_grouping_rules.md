# Functional Nomenclature and Grouping Rules

## Purpose

Provide consistent naming and grouping rules for aircraft functions so decomposition artifacts remain comparable across aircraft types.

## Core Principles

1. Define functions by intent and outcome, not by specific equipment brand or implementation.
1. Separate mission functions from enabling services.
1. Keep control authority explicit, especially between pilot, automation, and autonomous subsystems.
1. Treat data production, transformation, and consumption as separate functional responsibilities when risk-relevant.

## Functional Levels

- `L0`: Aviate, Navigate, Communicate, Operate.
- `L1`: Major functional groups within each L0 function.
- `L2`: Subfunctions with operational responsibilities.
- `L3`: Optional detailed subfunctions used for design/program-specific analysis.

## Naming Conventions

- Use verb-noun style where practical: `Manage Route`, `Stabilize Aircraft`, `Fuse Sensor Tracks`.
- Keep names neutral to platform class so fixed-wing and rotorcraft can share baseline terms.
- Mark variants explicitly with suffixes when behavior differs by aircraft purpose.

## Canonical Function ID Scheme

Use stable function identifiers when building traceability matrices, interface catalogs, and STIX-linked architecture mappings.

Pattern:

- `L0.L1.L2`
- Optional detailed function suffix: `L0.L1.L2.L3`

Abbreviation guidance:

- `AVI`: Aviate
- `NAV`: Navigate
- `COM`: Communicate
- `OPS`: Operate

Examples:

- `AVI.STAB.001`: Flight Stability and Maneuvering
- `AVI.GUID.001`: Flight Guidance and Automation
- `NAV.GUID.001`: Guidance and Trajectory Management
- `NAV.RTE.001`: Route and Waypoint Management
- `COM.DLNK.001`: Data Link and Network Exchange
- `OPS.MSN.001`: Mission Management

Usage rules:

- Reuse an ID for the same canonical function across all governance artifacts.
- Introduce a new sequence only when the function boundary changes materially.
- Use child suffixes for L3 functions when finer interface or threat mapping is required.

## Variant Annotation

Use bracket tags when needed:

- `[Passenger]`
- `[Missionized]`
- `[Both]`

Example: `Manage Cabin Services [Passenger]`.

## Boundary Guidance

- `Aviate`: aircraft control and physically sustaining flight.
- `Navigate`: guidance, positioning, route and trajectory intent.
- `Communicate`: external/internal exchange of operational information.
- `Operate`: mission or service-delivery functions beyond pure flight and navigation.

# Agent 08 Diagram Generator Examples

Purpose: hold reference output patterns for Mermaid sectioning and multi-level decomposition.

## Required Section Marker Pattern

```text
MERMAID_LEVEL0
```mermaid
flowchart TD
...
```

MERMAID_LEVEL1
```mermaid
flowchart TD
...
```
```

## Example A (Two Levels)

```text
MERMAID_LEVEL0
```mermaid
flowchart TD
  SYS["Avionics Control System"]
  EXT["External Navigation Source"]
  OPS["Operator Station"]
  EXT -->|"ARINC429 S:2 T:3 R:1 I:2 D:1 E:1"| SYS
  OPS -->|"Mgmt API S:1 T:2 R:2 I:2 D:1 E:1"| SYS
```

MERMAID_LEVEL1
```mermaid
flowchart TD
  subgraph ACS["Avionics Control System"]
    NAV["Navigation"]
    CTRL["Flight Control Logic"]
  end
  NAV -->|"Data Bus S:2 T:3 R:1 I:2 D:1 E:1"| CTRL
```
```

## Example B (Three Levels)

```text
MERMAID_LEVEL0
```mermaid
flowchart TD
  UAS["UAS Weapon System"]
  GMS["Ground Maintenance"]
  MPS["Mission Planning"]
  GMS --> UAS
  MPS --> UAS
```

MERMAID_LEVEL1
```mermaid
flowchart TD
  subgraph UAS["UAS Weapon System"]
    MC["Mission Computer"]
    SENS["Sensor Fusion"]
    WPN["Weapon Control"]
  end
  MPS -->|"Plan Upload S:3 T:4 R:2 I:3 D:2 E:2"| MC
  MC -->|"Targeting Bus S:3 T:4 R:2 I:3 D:2 E:3"| WPN
```

MERMAID_LEVEL2
```mermaid
flowchart TD
  subgraph MCX["Mission Computer Decomposition"]
    HV["Hypervisor"]
    VM1["Mission Apps VM"]
    VM2["Comms VM"]
  end
  HV --> VM1
  HV --> VM2
```
```

## Notes

- Always emit MERMAID_LEVEL0.
- Emit additional levels only when complexity justifies deeper detail.
- Keep levels sequential with no gaps.
- Do not invent stack details absent in canonical evidence.

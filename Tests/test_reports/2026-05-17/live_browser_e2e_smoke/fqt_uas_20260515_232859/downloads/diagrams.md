# Mermaid Diagrams

## level_0
```mermaid
flowchart TD
  subgraph AV["Air Vehicle Segment - HIGH RISK"]
    FMS["Flight Management System"]
  end
  subgraph GS["Mission Processing Ground Station"]
    MPC["Mission Processing Center"]
  end
  subgraph SAT["Satellite Communications Terminal - HIGH RISK"]
    GW["Encryption Gateway"]
  end
  subgraph MAINT["Ground Maintenance System - HIGH RISK"]
    DIAG["Diagnostic & Load System"]
  end
  EXT["External GPS / GCS"] -->|"Encrypted RF AES-256-GCM / max-STRIDE:5"| FMS
  FMS -->|"Encrypted RF AES-256-GCM / max-STRIDE:5"| GW
  GW -->|"HTTPS TLS 1.3 / max-STRIDE:4"| MPC
  DIAG -->|"MIL-STD-1553 RS-422 / max-STRIDE:5"| FMS
  style FMS fill:#ff9999
  style GW fill:#ff9999
  style DIAG fill:#ff9999
  legend["Legend: Red=High STRIDE risk (D/T>=4), Subgraph=Trust Boundary, Flow=Protocol/max-STRIDE"]
```

## level_1
```mermaid
flowchart TD
  subgraph AV["Air Vehicle Segment - HIGH RISK"]
    NAV["Navigation Subsystem"]
    CMD["Command & Control Subsystem"]
    PROC["Processing Subsystem"]
  end
  subgraph GS["Mission Processing Ground Station"]
    MPC["Mission Processing Server"]
  end
  subgraph SAT["Satellite Communications Terminal - HIGH RISK"]
    EGW["Encryption Gateway Subsystem"]
    TRF["Traffic Shaping Subsystem"]
  end
  subgraph MAINT["Ground Maintenance System - HIGH RISK"]
    DIAG["Diagnostic Computer"]
    SLS["Software Load Station"]
    TIM["Test Interface Module"]
  end
  GPS["GPS Constellation"] -->|"UDP / max-STRIDE:3"| NAV
  NAV -->|"SPI / max-STRIDE:2"| CMD
  CMD -->|"Encrypted RF AES-256-GCM / max-STRIDE:5"| EGW
  EGW -->|"HTTPS TLS 1.3 / max-STRIDE:4"| MPC
  DIAG -->|"MIL-STD-1553 / max-STRIDE:5"| TIM
  SLS -->|"RS-422 / max-STRIDE:5"| TIM
  TIM -->|"MIL-STD-1553 / max-STRIDE:5"| AV
  style NAV fill:#ff9999
  style EGW fill:#ff9999
  style TIM fill:#ff9999
  legend["Legend: Red=High STRIDE risk (D/T>=4), Subgraph=Trust Boundary, Flow=Protocol/max-STRIDE"]
```

## level_2
```mermaid
flowchart TD
  subgraph NAV["Navigation Subsystem - highest risk"]
    GPS["C-GPS-01 GPS Receiver"]
    IMU["C-IMU-01 IMU"]
  end
  subgraph CMD["Command & Control - HIGH RISK"]
    CP["C-CMD-01 Command Processor"]
  end
  subgraph TIM["Test Interface Module - highest risk"]
    BC["C-TIM-01 Bus Controller"]
    RS["C-TIM-02 RS-422 Interface"]
  end
  subgraph EGW["Encryption Gateway - HIGH RISK"]
    CG["C-CHARLIE-02 Crypto Gateway"]
  end
  GPS -->|"UDP / max-STRIDE:3"| CP
  IMU -->|"SPI / max-STRIDE:2"| CP
  CP -->|"Encrypted RF AES-256-GCM / max-STRIDE:5"| CG
  BC -->|"MIL-STD-1553 / max-STRIDE:5"| CP
  RS -->|"RS-422 / max-STRIDE:5"| CP
  style GPS fill:#ff9999
  style BC fill:#ff9999
  style CG fill:#ff9999
  legend["Legend: Red=High STRIDE risk (D/T>=4), Subgraph=Trust Boundary, Flow=Protocol/max-STRIDE"]
```

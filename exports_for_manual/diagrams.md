flowchart LR
    Avionics_Data_Network["Avionics Data Network"]
    ss_01["Flight Management Subsystem"]
    Avionics_Data_Network --> ss_01
    ss_02["Ground Data Link Subsystem"]
    Avionics_Data_Network --> ss_02
    cmp_01["FMS Core"]
    ss_01 --> cmp_01
    cmp_02["VHF Data Radio"]
    ss_02 --> cmp_02
    cmp_02 -->|"[TB] Ground to FMS Route Uplink"| cmp_01

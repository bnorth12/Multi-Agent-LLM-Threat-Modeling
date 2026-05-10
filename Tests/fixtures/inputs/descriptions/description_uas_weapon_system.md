# UAS Weapon System

The UAS Weapon System is a multi-segment intelligence, surveillance, and reconnaissance (ISR) system
comprising four operationally and physically separated segments. Each segment is developed and operated
by a distinct engineering or operations team, and the segments communicate over defined, bounded
interfaces. A complete system threat model may be constructed by supplying all segment documentation
together; individual segment threat models may be produced by supplying only the files for that segment.

## System Segments

### Segment Alpha — UAS Air Vehicle

The Alpha segment is the airborne platform. It carries the sensor payload, executes autonomous flight
control, and maintains a continuous command-and-control link with the ground via the Charlie satellite
communications relay. Alpha is the only segment that crosses the air-to-ground trust boundary during
normal operations. Physical access to the Alpha air vehicle is controlled through the Delta ground
maintenance segment when the vehicle is on the ground.

**Segment designator:** ALPHA
**Responsible team:** Airworthiness and Vehicle Systems Engineering

### Segment Bravo — Mission Processing Ground Station

The Bravo segment is a fixed-site facility that receives, processes, stores, and disseminates ISR
intelligence products. Bravo ingests sensor data forwarded from Charlie over the classified operations
network, runs payload processing algorithms, and routes finished intelligence to authorised consumers.
Bravo has no direct radio interface with the Alpha air vehicle; all air-to-ground data passes through
the Charlie terminal.

**Segment designator:** BRAVO
**Responsible team:** Mission Systems and Intelligence Operations

### Segment Charlie — Satellite Communications Terminal

The Charlie segment is a ground-based satellite modem and encryption gateway. It performs in-line
AES-256-GCM encryption of all traffic transiting the satellite link and relays command uplinks to the
Alpha air vehicle and sensor data downlinks to the Bravo processing station. Charlie constitutes the
Satellite Link Trust Boundary for the weapon system; no unencrypted data crosses this boundary.

**Segment designator:** CHARLIE
**Responsible team:** Communications Systems Engineering

### Segment Delta — Ground Maintenance System

The Delta segment comprises all diagnostic, test, and software-loading equipment used to service,
troubleshoot, calibrate, and update the Alpha air vehicle when it is on the ground. Delta connects to
Alpha via a dedicated maintenance data bus and to Bravo via a local area network for coordinating
software configuration baselines. Delta equipment is physically secured in the maintenance facility and
is never co-located with the Charlie terminal or any live satellite link.

**Segment designator:** DELTA
**Responsible team:** Sustainment and Avionics Maintenance Engineering

## Inter-Segment Radio Link Architecture

All operational communication between the Alpha air vehicle and the ground segments is relayed through
the Charlie satellite terminal over a bidirectional satellite RF link. There is no direct line-of-sight
radio link between Alpha and Bravo or between Alpha and Delta during flight operations.

```
  [ALPHA Air Vehicle]
          |
     Satellite RF Link (encrypted, AES-256-GCM)
          |
  [CHARLIE Sat Comms Terminal]
          |
     Classified Ops Network (HTTPS/TLS 1.3)
          |
  [BRAVO Mission Processing Ground Station]

  [DELTA Ground Maintenance System] ---- Maintenance Bus (MIL-STD-1553 / RS-422) ----> [ALPHA Air Vehicle] (ground only)
  [DELTA Ground Maintenance System] ---- LAN (Ethernet) ----> [BRAVO Ground Station]
```

## Segment Boundaries and Trust Model

| Boundary Name                | From Segment | To Segment | Medium                     | Trust Level Change        |
|------------------------------|--------------|------------|----------------------------|---------------------------|
| Satellite Link Boundary      | ALPHA        | CHARLIE    | Satellite RF (encrypted)   | Untrusted → Encrypted     |
| Ops Network Boundary         | CHARLIE      | BRAVO      | Classified LAN / HTTPS     | Encrypted → Trusted       |
| Maintenance Bus Boundary     | DELTA        | ALPHA      | MIL-STD-1553 / RS-422      | Trusted Maint → Restricted|
| Maintenance LAN Boundary     | DELTA        | BRAVO      | Ethernet LAN               | Trusted Maint → Trusted   |

## Operational Constraints

- The satellite RF link is the single point of presence for all air-to-ground communication during flight.
- Command uplinks from Bravo to Alpha must be routed through Charlie; Bravo has no direct uplink capability.
- Delta maintenance interfaces to Alpha are mechanically and electrically isolated from all RF interfaces.
- Software loads to Alpha are authorised by Bravo and executed by Delta over the maintenance bus.
- Key management for the satellite link is handled by a Key Management Authority external to all four segments.

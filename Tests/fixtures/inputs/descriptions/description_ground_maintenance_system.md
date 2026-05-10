# Delta Ground Maintenance System

The Delta Ground Maintenance System (GMS) is the sustainment segment of the UAS Weapon System. It
comprises all diagnostic computers, software load stations, test interface hardware, and ground support
equipment (GSE) used to service, troubleshoot, calibrate, and update the Alpha UAS air vehicle when it
is on the ground. Delta has no operational role during flight; it is electrically and mechanically
isolated from Alpha's RF interfaces at all times.

## Diagnostic Computer Subsystem

The Diagnostic Computer Subsystem hosts the primary maintenance workstation software and provides the
human-machine interface for all fault isolation, health monitoring, and maintenance data review. It
communicates with Alpha over the maintenance bus and logs all diagnostic sessions to the Maintenance
Data Recorder.

### Maintenance Workstation

The Maintenance Workstation application presents technician operators with built-in test (BIT) results,
fault codes, sensor calibration data, and maintenance history. It accepts commands from authorised
maintenance personnel and issues structured queries to the Test Interface Module.

#### Function: Run Built-In Test

Initiates a full BIT sequence on the connected Alpha air vehicle, collects pass/fail results from all
line-replaceable units (LRUs), and displays results to the operator with fault isolation guidance.

#### Function: Download Flight Data

Retrieves post-flight health and usage monitoring (HUMS) data from the Alpha onboard recorder over the
maintenance bus and stores the data in the Maintenance Data Recorder.

### Maintenance Data Recorder

The Maintenance Data Recorder provides encrypted local storage for all maintenance session logs, BIT
results, and HUMS downloads. Data at rest is encrypted with AES-256. Access requires role-based
authentication.

## Software Load Station Subsystem

The Software Load Station Subsystem manages the storage, integrity verification, and transfer of
authorised software loads to the Alpha air vehicle and to field-replaceable software modules within the
Delta GMS itself.

### Software Load Controller

The Software Load Controller manages the software baseline for all loadable software parts (LSPs) for
the Alpha platform. It coordinates with the Bravo Mission Processing Ground Station to receive approved
software packages and validates cryptographic signatures before allowing a load operation.

#### Function: Receive Software Package

Accepts an authorised software package from Bravo over the maintenance LAN, verifies the digital
signature against the trusted key store, and stages the package for loading.

#### Function: Load Software to Aircraft

Transfers a staged, verified software package to the Alpha air vehicle over the maintenance bus, monitors
load progress, and confirms successful installation via a post-load verification sequence.

### Load Verification Module

The Load Verification Module executes post-load integrity checks on the Alpha air vehicle after each
software load. It reads back installed software part numbers and checksums and compares them against the
expected baseline from the Software Load Controller.

## Test Interface Module Subsystem

The Test Interface Module (TIM) Subsystem provides the physical and logical interface between the Delta
GMS and the Alpha air vehicle's maintenance port. It translates maintenance bus protocols
(MIL-STD-1553 and RS-422) and arbitrates access between the Diagnostic Computer and the Software Load
Station.

### Bus Controller

The Bus Controller manages MIL-STD-1553 bus master operations when Delta is connected to Alpha. It
schedules message transfers and enforces bus access priorities to prevent collision between concurrent
maintenance activities.

#### Function: Issue Bus Command

Transmits a formatted MIL-STD-1553 command word to a target LRU on the Alpha platform and waits for a
status response within the allowed time window.

#### Function: Receive Bus Data

Reads data frames from the MIL-STD-1553 bus in response to a previously issued command and forwards
them to the requesting Delta subsystem.

### RS-422 Serial Interface

The RS-422 Serial Interface provides a dedicated low-speed serial channel for LRUs that do not support
MIL-STD-1553. It handles baud rate negotiation, framing, and parity checking.

## Trust Boundaries

The interface between the Delta GMS and the Alpha air vehicle constitutes the **Maintenance Bus
Boundary**. This boundary is physically enforced by the Test Interface Module connector, which is only
mated when the aircraft is powered off from flight systems or in a dedicated maintenance power mode.
All commands issued across this boundary must be authenticated with a maintenance session token.

The interface between the Delta GMS and the Bravo Mission Processing Ground Station constitutes the
**Maintenance LAN Boundary**. Software packages and configuration data cross this boundary and must
carry a valid digital signature from the authorised software configuration management authority. No
flight-operational data from the Alpha air vehicle is transmitted across this boundary; maintenance
logs are stored locally in the Maintenance Data Recorder.

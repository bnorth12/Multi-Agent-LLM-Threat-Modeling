# Bravo Ground Station

The Bravo Ground Station is a fixed-site mission control facility that processes, stores, and disseminates intelligence products from airborne assets. It handles high-rate sensor data and interfaces with remote operations networks.

## Processing Subsystem

The Processing Subsystem hosts the Mission Computer, which executes payload algorithms and sensor fusion pipelines. Processed outputs are streamed at high rate to the Storage Subsystem over a PCIe internal bus.

### Mission Computer

The Mission Computer component runs the payload algorithms and manages output logging.

#### Function: Execute Payload Algorithm

Runs the sensor fusion pipeline on raw sensor input and generates processed output frames. This function is the origin of all data written to persistent storage.

#### Function: Log Results

Streams processed output frames to the Storage Subsystem at high rate over the Processing to Storage Subsystem Bus (IF-104). This function is the upstream source of the Log Results to Write Encrypted Record interface (IF-105).

## Storage Subsystem

The Storage Subsystem consists of a Solid State Recorder for high-rate data and a Key Management Module (KMM) for encryption key lifecycle management. All data written to persistent storage is encrypted. Key requests are exchanged between the Mission Computer and the KMM over an internal I2C bus.

### Solid State Recorder

The Solid State Recorder component persists sensor frames to non-volatile storage under encryption.

#### Function: Write Encrypted Record

Receives an output frame from the Log Results function, encrypts the frame using a key obtained from the Key Management Module, and commits it to storage.

#### Function: Request Encryption Key

Sends a key request to the Key Management Module over the Key Request Interface (IF-102) and receives the encryption key response.

### Key Management Module

The Key Management Module manages the full lifecycle of encryption keys used for stored data.

#### Function: Issue Encryption Key

Validates an incoming key request from the Solid State Recorder and returns the appropriate encryption key over the Key Request Interface (IF-102).

## Trust Boundaries

Remote operations personnel access the Bravo Ground Station over the Operations Network Boundary via HTTPS (IF-103). This boundary requires certificate-based mutual authentication. All diagnostic data transferred across this boundary must be sanitised to prevent information disclosure.

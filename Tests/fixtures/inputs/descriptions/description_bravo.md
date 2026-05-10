# Bravo Ground Station

The Bravo Ground Station is a fixed-site mission control facility that processes, stores, and disseminates intelligence products from airborne assets. It handles high-rate sensor data and interfaces with remote operations networks.

## Processing Subsystem

The Processing Subsystem hosts the Mission Computer, which executes payload algorithms and sensor fusion pipelines. Processed outputs are streamed at high rate to the Storage Subsystem over a PCIe internal bus.

## Storage Subsystem

The Storage Subsystem consists of a Solid State Recorder for high-rate data and a Key Management Module (KMM) for encryption key lifecycle management. All data written to persistent storage is encrypted. Key requests are exchanged between the Mission Computer and the KMM over an internal I2C bus.

## Trust Boundaries

Remote operations personnel access the Bravo Ground Station over the Operations Network Boundary via HTTPS. This boundary requires certificate-based mutual authentication. All diagnostic data transferred across this boundary must be sanitised to prevent information disclosure.

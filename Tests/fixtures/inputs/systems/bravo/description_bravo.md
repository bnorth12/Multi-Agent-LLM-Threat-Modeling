# Bravo Ground Station

The Bravo Ground Station is a fixed-site mission control facility that processes, stores, and disseminates intelligence products from airborne assets. It also validates and brokers mission plans generated in Charlie before those plans are relayed for Alpha execution.

## Processing Subsystem

The Processing Subsystem hosts the Mission Computer, which executes payload algorithms and sensor fusion pipelines. Processed outputs are streamed at high rate to the Storage Subsystem over a PCIe internal bus.

## Mission Routing Subsystem

The Mission Routing Subsystem hosts the Mission Package Broker. It ingests all-source intelligence and mission plans from Charlie Mission Planning, applies policy validation and release controls, and forwards approved mission packages for Alpha execution. It also receives mission execution feedback from Alpha.

## Storage Subsystem

The Storage Subsystem consists of a Solid State Recorder for high-rate data and a Key Management Module (KMM) for encryption key lifecycle management. All data written to persistent storage is encrypted. Key requests are exchanged between the Mission Computer and the KMM over an internal I2C bus.

## Trust Boundaries

Remote operations personnel and planning services access Bravo over the Operations Network Boundary via HTTPS with mutual authentication. Mission-package data transferred across this boundary is signed, validated, and audited before release.

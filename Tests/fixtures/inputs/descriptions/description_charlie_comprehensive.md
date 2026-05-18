# Charlie Satellite Communications Terminal - Comprehensive Threat Model

## System Overview

The Charlie Satellite Communications Terminal is a ground-based satellite modem and encryption gateway that serves as the mandatory relay for all air-to-ground and ground-to-air traffic between the Alpha UAS air vehicle and Bravo Mission Processing Ground Station. It performs in-line encryption and decryption for all satellite link traffic, enforces session key management and rotation, handles link-level traffic shaping and priority queuing, and logs all communications events for security audit and signal intelligence. The terminal operates 24/7 with high availability requirements.

## Theory of Operation

### What

The Charlie Terminal transforms plaintext operational data flows from Bravo ground station into encrypted satellite link transmissions and vice versa. It receives unencrypted mission commands from Bravo (routed by Dissemination Gateway), encrypts commands using active session key, transmits encrypted commands to satellite uplink modem for RF relay to air vehicle. Simultaneously, it receives encrypted telemetry downlinks from satellite modem, decrypts telemetry using vehicle-specific session key, validates decrypted telemetry structure and authenticity, forwards decrypted telemetry to Bravo processing pipeline. Session keys are rotated every 60 seconds per vehicle; key material originates from secure Key Management Authority and is distributed to Charlie terminal via secure transport. All traffic crossing the satellite link boundary is encrypted; all traffic crossing Bravo operational network boundary is encrypted or authentication-protected.

### When

The system initializes pre-launch: satellite modem acquires lock on visible satellites, RF uplink/downlink carrier acquisition, automatic frequency adjustment. Key material loading occurs at pre-deployment: authorized personnel execute key load procedure (smart card authentication, cryptographic signature validation), keys loaded into secure key storage module. System transitions to operational state when air vehicle powers up: Terminal detects uplink from air vehicle (signal strength monitoring), establishes TLS session with air vehicle, receives initial key material bundle from vehicle Key Store. During continuous operations: uplink commands flow from Bravo through Terminal to satellite modem at command-arrival rate (Ã¢â€°Â¤ 1 command per 10 seconds), downlinks flow from satellite modem through Terminal to Bravo at 256 kbps sustained rate, key rotation triggered every 60 seconds by Terminal timer (no external coordination required), system health status broadcast to Bravo every 10 seconds. During link outage: Terminal detects loss of RF lock (no downlinks received for > 30 seconds), transitions to local autonomous mode (key rotation continues, Terminal buffers uplink commands awaiting link re-establishment), buffers cleared when link re-establishes or 10-minute buffer timeout occurs (oldest commands dropped).

### Why

Satellite link encryption is mandatory to prevent adversary interception and exfiltration of mission commands and sensor telemetry. In-line encryption at gateway (Charlie) prevents plaintext exposure during RF propagation and prevents unauthorized parties at intermediate relay facilities from accessing operational data. Session key rotation every 60 seconds limits exposure window if one key is compromised (60-second recovery). Link-level traffic shaping prevents RF modem overload and ensures command priority (time-critical commands processed first, background sensor telemetry dropped if uplink congested). Comprehensive audit logging enables security investigation of unauthorized access attempts (replay attacks, key compromise) and supports signals intelligence operations (traffic pattern analysis, adversary SIGINT targeting). Redundant gateway instances (if deployed) enable fault tolerance and load sharing across multiple physical locations.

### How

**Step 1 Ã¢â‚¬â€ Pre-Deployment Key Material Loading:** Security Officer inserts secure smart card into Terminal key loader; authenticates using PIN; Terminal displays key material manifest (vehicle_id, key_rotation_schedule, validity_dates); Officer verifies manifest matches deployment orders; Terminal cryptographically signs manifest with smart card private key and stores manifest in tamper-protected audit log; Terminal securely transfers key material from smart card to Key Storage Module via AES-256-KW (key wrap) protocol.

**Step 2 Ã¢â‚¬â€ Mission Initialization:** Air vehicle powers up and acquires GPS/INS lock; Vehicle Key Store initializes and marks keys as valid. Ground operator issues first command ("enable uplink") through Bravo Dissemination Gateway; command routed to Terminal Uplink Command Processor.

**Step 3 Ã¢â‚¬â€ Uplink Command Processing:** Terminal Uplink Command Processor receives command; fetches current uplink key from Key Storage Module for target vehicle; applies AES-256-GCM encryption to command payload; encapsulates encrypted command in satellite uplink frame format; forwards encrypted frame to satellite RF modem via PCIe interface; broadcasts command acknowledgement to Bravo Mission Computer.

**Step 4 Ã¢â‚¬â€ Downlink Reception and Decryption:** Satellite RF modem receives encrypted downlink frame from air vehicle (or relayed through satellite); RF modem demodulates ciphertext and forwards to Downlink Decryption Processor via PCIe DMA; Downlink Processor fetches current downlink key (may differ from uplink key if asymmetric cipher used) from Key Storage Module; decrypts ciphertext using AES-256-GCM; validates GCM authentication tag (rejects frame if tag mismatch); forwards decrypted telemetry to Bravo ground station via secure network tunnel (IPsec VPN or TLS); logs downlink event (timestamp, vehicle_id, packet_count, byte_count, decryption_success_or_failure) to audit processor.

**Step 5 Ã¢â‚¬â€ Session Key Rotation:** Terminal Key Rotation Timer fires every 60 seconds; fetches next key in rotation schedule from Key Storage Module; atomically updates "current active key" and "next key" pointers (no in-flight commands interrupted during rotation); broadcasts key rotation notification to air vehicle via next uplink command (opcode: KEY_ROTATION_ACTIVE, params: [new_key_id, validity_start_time]); logs key rotation event to audit processor.

**Step 6 Ã¢â‚¬â€ Traffic Shaping and Priority Queuing:** If uplink capacity constrained (satellite resources limited or RF power budget exceeded), Terminal Traffic Shaper applies priority rules: time-critical commands (emergency, course correction) transmitted immediately (< 100 ms queue delay); routine commands queued (FIFO); sensor acknowledgements and housekeeping dropped if queue exceeds 8-second buffer. Downstream Bravo systems monitor for dropped frames (telemetry sequence number gaps) and request retransmission if needed.

### Who

### Actors

- **Pre-deployment Security Officer** Ã¢â‚¬â€ loads key material onto Terminal; validates key manifest; no access during operations

- **Ground Operator (Bravo Dissemination Gateway)** Ã¢â‚¬â€ issues commands through secure network tunnel; depends on Terminal for encryption and transmission
- **Terminal System** Ã¢â‚¬â€ automated; performs encryption, key rotation, traffic shaping, audit logging; operates without human intervention

- **Satellite RF Modem** Ã¢â‚¬â€ receives/transmits RF signals; no encryption knowledge (transparent relay); provides RF status signals to Terminal (lock_status, signal_strength, BER Ã¢â‚¬â€ bit error rate)
- **Air Vehicle (Alpha)** Ã¢â‚¬â€ receives encrypted uplink commands; must possess current downlink key to decrypt downlinks; depends on Terminal key rotation notification to stay synchronized

- **Bravo Mission Computer** Ã¢â‚¬â€ receives decrypted telemetry; may verify telemetry authenticity via GCM tag (already validated by Terminal); depends on Terminal audit log for forensic analysis if security incident occurs
- **Key Management Authority (KMA)** Ã¢â‚¬â€ pre-loads key material into Terminal at deployment; updates key material if compromise suspected; security Officer intermediary

- **Audit Processor** Ã¢â‚¬â€ logs all terminal events; forensic analysis of audit trail after security incidents; audit log is forensic evidence (immutable, authenticated)

### Dependencies

- Terminal uplink depends on Key Storage Module for uplink encryption key; if KSM unavailable, Terminal buffers commands for Ã¢â€°Â¤ 10 minutes

- Terminal downlink depends on Key Storage Module for downlink decryption key; if KSM unavailable, Terminal discards downlinks (Bravo alerts operator of "CHARLIE_DECRYPTION_FAILURE")
- Bravo Dissemination Gateway depends on Terminal for encrypted transmission; if Terminal unavailable, Bravo enters "offline" mode (commands buffered, transmitted upon Terminal recovery)

- Air vehicle depends on Terminal for key rotation notifications; if Terminal key rotation stalls for > 2 rotations (120 seconds), vehicle enters failsafe (revert to last-known-good key, halt new command acceptance)

## High-Level Interfaces

### Input Interfaces

- **Unencrypted Uplink Commands from Bravo** Ã¢â‚¬â€ Secure network tunnel (IPsec VPN or TLS) from Bravo Dissemination Gateway carrying plaintext command frames; command format [vehicle_id, opcode, parameters, timestamp, command_sequence_number]; command arrival rate Ã¢â€°Â¤ 1 command per 10 seconds per vehicle; command timeout (expiration) Ã¢â€°Â¤ 5 minutes (old commands automatically dropped); maximum queue depth 100 commands per vehicle

- **Encrypted Downlink Telemetry from Satellite Modem** Ã¢â‚¬â€ PCIe DMA interface from RF modem carrying ciphertext telemetry frames; frame format [vehicle_id, sequence_number, timestamp, ciphertext_payload, gcm_tag]; frame arrival rate 20 Hz per vehicle; maximum aggregate downlink rate 10 Mbps (supports multiple simultaneous air vehicles)
- **Session Key Material** Ã¢â‚¬â€ Secure transport from Key Management Authority (KMA); transported via encrypted USB drive or secure network tunnel; key material format [vehicle_id, key_schedule (array of keys with validity dates/times), key_rotation_period, key_algorithm_params]; key material loaded during pre-deployment phase, refreshed during mission if compromise suspected

### Output Interfaces

- **Encrypted Uplink Commands to Satellite Modem** Ã¢â‚¬â€ PCIe interface to RF modem carrying encrypted command frames; frame format [vehicle_id, sequence_number, timestamp, ciphertext_payload, gcm_tag, link_priority]; frame transmission rate varies (command-arrival-driven); maximum uplink rate limited by RF power budget and satellite transponder capacity (typically 128 kbps shared across all vehicles)

- **Decrypted Downlink Telemetry to Bravo** Ã¢â‚¬â€ Secure network tunnel (IPsec VPN or TLS) carrying plaintext telemetry streams; streams [vehicle_id, sensor_data (video, SIGINT, inertial), command_acknowledgements, system_health]; telemetry rate 256 kbps per vehicle; stream timeout triggers "DOWNLINK_STALE" alert to Bravo
- **System Status and Audit Log** Ã¢â‚¬â€ Periodic status messages to Bravo Mission Computer (every 10 seconds) carrying [terminal_operational_status (nominal/degraded/failed), uplink_queue_depth, downlink_buffer_occupancy, key_rotation_status, audit_event_count]; audit log records (1 per significant event) containing [timestamp, event_type (command_encrypted, downlink_decrypted, key_rotated, tag_validation_failed), vehicle_id, outcome (success/failure), error_detail_if_applicable]

### Internal Processing Interfaces

- **Key Provisioning Request** Ã¢â‚¬â€ Internal RPC from Uplink/Downlink Processors to Key Storage Module requesting current active key for target vehicle; RPC includes [vehicle_id, key_type (uplink|downlink), timestamp]; KSM response includes [key_material, key_id, validity_window]; RPC latency Ã¢â€°Â¤ 10 ms; RPC timeout (no response) triggers processor fallback to cached key for Ã¢â€°Â¤ 30 seconds

- **Traffic Shaper Control** Ã¢â‚¬â€ Internal message queue from Command Processor to Traffic Shaper carrying frame priority level and destination (uplink|audit); priority levels [CRITICAL (emergency), HIGH (course correction), NORMAL (routine), LOW (housekeeping)]; Traffic Shaper scheduler outputs frames in priority order or drops LOW-priority frames if buffer exceeds 8-second latency threshold
- **Audit Logger Interface** Ã¢â‚¬â€ Async append interface from all Terminal processors to Audit Processor; audit messages carry [event_timestamp, processor_id, event_type_enum, vehicle_id, success_flag, optional_detail_string]; audit log stored in Ring Buffer (circular buffer, oldest entries overwritten if capacity exceeded; minimum buffer depth 1 million entries = ~100 hours at typical event rate 10 kHz)

## Component Pieces and Parts

### Uplink Processing Subsystem Components

### Uplink Command Processor

- **Function:** Receives plaintext commands from Bravo via secure network tunnel; performs command validation (opcode recognized, parameters in valid range, command not expired); fetches current uplink key from Key Storage Module; applies AES-256-GCM encryption; encapsulates encrypted command in satellite link frame; queues encrypted frame for transmission to satellite modem

- **Interfaces:** Network socket input from Bravo (TLS or IPsec tunnel); I2C RPC to Key Storage Module (key provisioning); output message queue to Traffic Shaper; event log output to Audit Processor; command timeout watchdog (commands older than 5 minutes auto-dropped)
- **Trust Boundaries:** Command input validation (invalid commands rejected before encryption); key provisioning boundary (KSM authentication required before key release); encryption boundary (command parameters must not contain invalid UTF-8 or oversized structures that could cause parsing errors downstream)

- **Failure Modes:** Command validation failure (unknown opcode or out-of-range parameter); command discarded and VALIDATION_FAILURE logged; invalid key_id received from KSM; command queued for retry after timeout (retry up to 3 times); KSM timeout (no key response within 10 ms); Processor falls back to cached key for Ã¢â€°Â¤ 30 seconds, then enters failsafe

### Traffic Shaper

- **Function:** Manages command transmission priority and rate limiting; accepts encrypted frames from Uplink Command Processor; assigns priority based on command type; maintains separate queues per priority level; forwards frames to satellite modem respecting RF power budget and satellite transponder capacity; drops low-priority frames if backpressure builds

- **Interfaces:** Input message queue from Uplink Command Processor; output to satellite RF modem via PCIe; uplink capacity constraint input from RF modem (available_bandwidth_kbps, estimated_queue_latency_ms); status output to Audit Processor
- **Trust Boundaries:** Uplink capacity boundary (Modem reports available bandwidth; Traffic Shaper must not exceed advertised capacity or RF signal distortion occurs); priority level boundary (mission-critical commands must not be dropped; only routine commands dropped under congestion)

- **Failure Modes:** RF modem capacity exhausted; Traffic Shaper begins queuing frames; if queue latency exceeds 8 seconds, LOW-priority housekeeping frames dropped; if queue latency exceeds 30 seconds, NORMAL-priority frames dropped; HIGH and CRITICAL frames never dropped (buffer overflow would trigger system restart)

### Downlink Processing Subsystem Components

### Downlink Decryption Processor

- **Function:** Receives encrypted telemetry frames from satellite RF modem; performs GCM authentication tag validation; decrypts ciphertext using AES-256-GCM; demultiplexes decrypted payload into constituent data streams (video, SIGINT, inertial, acknowledgements); forwards decrypted streams to Bravo via secure network tunnel; logs all downlink events (success/failure)

- **Interfaces:** PCIe DMA input from RF modem (encrypted frames); I2C RPC to Key Storage Module (key provisioning for decryption); network socket output to Bravo (TLS or IPsec tunnel); event log output to Audit Processor; RF modem interface for status (lock_status, signal_strength, BER)
- **Trust Boundaries:** Ciphertext input boundary (frames with invalid GCM tags are rejected and logged, GCM_TAG_MISMATCH logged); key provisioning boundary (KSM must validate Downlink Processor identity via I2C authentication before releasing decryption key); decrypted data boundary (plaintext telemetry in Processor RAM is protected by process isolation and access control enforcement by OS; telemetry routed immediately to Bravo, not cached)

- **Failure Modes:** GCM tag validation failure (tampering detected); frame dropped and INTEGRITY_VIOLATION logged; key provisioning RPC timeout; Processor falls back to cached key for current frame and next 10 frames (Ã¢â€°Â¤ 500 ms fallback duration), then enters failsafe; RF lock loss (no frames received for > 30 seconds); Processor broadcasts DOWNLINK_LOST alert to Bravo and enters "waiting for link recovery" mode

### Bravo Network Interface

- **Function:** Maintains secure network connection to Bravo Mission Computer; forwards decrypted telemetry streams; receives status/command queries from Bravo; handles connection recovery if network link interrupted

- **Interfaces:** Network socket (Ethernet) to Bravo (TLS or IPsec tunnel); telemetry input from Downlink Decryption Processor; status/command input from Audit Processor and Command Processor; persistent connection state (TCP keepalive every 30 seconds)
- **Trust Boundaries:** Network connection boundary (mutual TLS authentication required; certificate revocation checked every 1 hour); telemetry forwarding boundary (plaintext telemetry transmitted over encrypted tunnel; tunnel integrity must not be compromised)

- **Failure Modes:** Network link failure (no TCP keepalive response for > 60 seconds); Terminal buffers telemetry in local FIFO buffer (capacity 100 MB, Ã¢â€°Ë† 400 seconds at 256 kbps); upon link recovery, cached telemetry transmitted in order; if buffer overflows, oldest telemetry dropped (Bravo detects sequence number gap and requests retransmission if available)

### Key Management Subsystem Components

### Key Storage Module (HSM Ã¢â‚¬â€ Hardware Security Module)

- **Function:** Stores pre-loaded encryption keys and key rotation schedule; provides keys on authenticated request from Command and Decryption processors; enforces key rotation schedule via internal timer; detects physical tampering; logs all key accesses

- **Interfaces:** I2C RPC interface from Uplink/Downlink Processors (key provisioning requests); secure USB or network interface from Key Management Authority (key material upload during pre-deployment); power supply (3.3V) with power-loss detection; physical tamper sensors; audit log interface
- **Trust Boundaries:** Key storage boundary (keys at rest encrypted with HSM root key, derived from PUF Ã¢â‚¬â€ Physically Unclonable Function; root key never exposed); key provision boundary (HSM validates requester ID via I2C authentication before releasing keys); key rotation boundary (HSM enforces rotation schedule autonomously; no manual override without secure authentication)

- **Failure Modes:** Physical tamper detected (enclosure opened or key storage area probed); HSM erases all keys and broadcasts TAMPER_DETECTED fault; key store exhaustion (mission duration exceeds pre-loaded keys); after 120 Ãƒâ€” 60-second rotations = 7200 seconds Ã¢â€°Ë† 2 hours, if < 10 keys remain, HSM broadcasts KEY_STORE_WARNING; I2C link failure (timeout in key provisioning RPC); processors fall back to cached key for Ã¢â€°Â¤ 30 seconds; if link remains failed after 30 seconds, Terminal enters "key_exhausted" failsafe (encrypt using last valid key indefinitely, security degraded but mission continues)

### System Monitoring and Audit Subsystem Components

### Audit Processor

- **Function:** Collects audit events from all Terminal components; validates event format; appends events to circular audit log buffer; periodically transmits audit log snapshots to Bravo for long-term archival; implements log rotation (new log file every 24 hours or when buffer fills)

- **Interfaces:** Async append interface from all processors (Command Processor, Decryption Processor, Traffic Shaper, Key Storage Module); network socket to Bravo (encrypted connection) for audit log snapshots; local circular buffer for temporary audit log storage (minimum 1 million events = Ã¢â€°Ë† 100 hours at 10 kHz event rate)
- **Trust Boundaries:** Audit log integrity boundary (logs cryptographically signed with Terminal private key; Bravo can verify logs were not modified by validating signature); log forwarding boundary (audit logs contain no plaintext keys or command payloads; only metadata (event_type, vehicle_id, success/failure, timestamp))

- **Failure Modes:** Audit buffer overflow (event rate exceeds buffer drain rate); oldest events overwritten (loss of forensic history); Processor signals AUDIT_BUFFER_FULL warning to Bravo; Bravo should perform emergency audit log download; I2C link to Bravo fails; Processor buffers audit logs locally and replays upon link recovery (oldest logs may be lost if local buffer overflows before recovery)

## Trust Boundaries and Data Flow Validation

### Explicit Trust Boundaries

1. **Bravo-Terminal Command Boundary** Ã¢â‚¬â€ Secure network tunnel (TLS or IPsec) carrying plaintext command frames. Terminal validates command format and opcode before encryption. Invalid commands rejected with VALIDATION_FAILURE audit log entry.

1. **Terminal-Satellite Uplink Boundary** Ã¢â‚¬â€ Encrypted command frames transmitted via RF. Ciphertext and GCM tag transmitted; air vehicle performs GCM validation upon receipt. Replay attacks prevented by command sequence number validation.

1. **Satellite-Terminal Downlink Boundary** Ã¢â‚¬â€ Encrypted telemetry frames received from satellite modem. Terminal validates GCM tag; rejected frames (tag mismatch) trigger INTEGRITY_VIOLATION audit entry and frame discard.

1. **Terminal-Bravo Telemetry Boundary** Ã¢â‚¬â€ Decrypted telemetry forwarded to Bravo via secure network tunnel. Bravo may perform secondary GCM validation if symmetric key-sharing arrangement exists (advanced deployment mode).

1. **Key Material Boundary** Ã¢â‚¬â€ Pre-loaded keys from Key Management Authority protected by secure transport (encrypted USB or secure network tunnel). Upon Terminal load, keys transferred to Hardware Security Module via AES-256-KW key wrap protocol.

### Data Flow Sensitivity Levels

- **Plaintext Commands (Bravo Ã¢â€ â€™ Terminal)** Ã¢â‚¬â€ Confidential (transmitted over encrypted tunnel); integrity-critical (invalid commands rejected before encryption)

- **Encrypted Uplink Commands (Terminal Ã¢â€ â€™ Satellite)** Ã¢â‚¬â€ Secret (encryption required); replay-sensitive (sequence number validation enforced); intercepted ciphertext is security-effective only if session key is compromised
- **Encrypted Downlink Telemetry (Satellite Ã¢â€ â€™ Terminal)** Ã¢â‚¬â€ Highly classified (vehicle sensor data); authentication-critical (GCM tag validation prevents tampering); decrypted telemetry is plaintext in RAM but immediately forwarded to Bravo

- **Audit Logs** Ã¢â‚¬â€ Unclassified but sensitive (contains traffic pattern metadata); forensic-critical (immutable, signed logs required for security investigation); archived by Bravo for 7-year retention

## Operational Constraints

1. **Uplink Capacity** Ã¢â‚¬â€ Limited by RF power budget and satellite transponder capacity; typical 128 kbps shared across all vehicles. Command rate-limiting enforced: Ã¢â€°Â¤ 1 command per 10 seconds per vehicle. Commands buffered if capacity exceeded; queue timeout 5 minutes (old commands dropped).

1. **Downlink Capacity** Ã¢â‚¬â€ 256 kbps per vehicle (typical). Multiple vehicles supported up to aggregate 10 Mbps. If downlink congested, lower-priority telemetry (housekeeping) dropped in preference to high-priority telemetry (video, SIGINT).

1. **Key Rotation Frequency** Ã¢â‚¬â€ Every 60 seconds per vehicle. Key Storage Module must maintain Ã¢â€°Â¥ 120 keys per vehicle (covers 2-hour missions). If key store depleted, Terminal falls back to last valid key (security degraded, audit warning issued).

1. **Processing Latency** Ã¢â‚¬â€ Uplink command: Reception to encryption Ã¢â€°Â¤ 50 ms. Downlink decryption: Reception to forwarding to Bravo Ã¢â€°Â¤ 100 ms. Audit event logging: Ã¢â€°Â¤ 10 ms after event occurrence.

1. **High-Availability Requirements** Ã¢â‚¬â€ Terminal must operate 24/7 with Ã¢â€°Â¤ 99 seconds total unplanned downtime per month (Ã¢â€°Ë† 99.99% availability). Failover to hot-standby Terminal instance if primary fails. Key material and audit logs replicated to standby in real-time.

## Threat Model Scope

This description models Charlie Terminal as a critical-infrastructure encryption gateway and relay. Threats include: RF eavesdropping (interception of encrypted frames; security depends on key confidentiality), RF jamming (denial-of-service on uplink or downlink), session key compromise (adversary obtains key material from Key Storage Module and decrypts cached telemetry), replay attacks (adversary captures encrypted uplink frame and retransmits; prevented by command sequence number), GCM tag forgery (adversary modifies encrypted telemetry and regenerates valid GCM tag; prevented if GCM authentication enforced), physical intrusion (adversary opens Hardware Security Module and extracts keys via side-channel analysis), and software exploit (adversary injects malicious code into Terminal firmware to exfiltrate keys or redirect telemetry). All data crossing trust boundaries must be encrypted, authenticated, and validated against logical consistency checks.

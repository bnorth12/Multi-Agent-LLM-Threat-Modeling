# Avionics Data Network - Comprehensive Threat Model

## System Overview

The Avionics Data Network is a distributed real-time system integrating navigation, guidance, flight control, vehicle management, and pilot display functions. Four subsystems operate in closed-loop feedback to execute autonomous and pilot-commanded flight modes while maintaining aircraft stability and situational awareness.

## Theory of Operation

### What

The Avionics Data Network transforms inertial sensor measurements and GPS position fixes into flight control commands and pilot display outputs. It processes navigation data from INS gyros/accelerometers and GPS, computes lateral/vertical guidance from waypoint plans, executes closed-loop servo control to move flight surfaces, captures feedback from actuators, and presents integrated flight path markers and health data to the cockpit display. All processing is deterministic and time-synchronized across four interconnected subsystems.

### When

The system operates continuously during flight from engine start through landing. Navigation Subsystem initialization occurs first (GPS acquisition, INS alignment). Flight Control Subsystem initializes next (servo deflection calibration, control law load). Vehicle Management and Display subsystems initialize last (graphics pipeline startup). Once airborne, all four subsystems operate in real-time synchrony: inertial measurements at 50 Hz Ã¢â€ â€™ guidance updates at 10 Hz Ã¢â€ â€™ control law execution at 400 Hz Ã¢â€ â€™ servo commands at 400 Hz Ã¢â€ â€™ feedback loop closure at 100 Hz Ã¢â€ â€™ display refresh at 30 Hz.

### Why

Aircraft stability and autonomous mission execution depend on continuous deterministic fusion of navigation inputs with closed-loop control feedback. Pilot safety depends on accurate real-time display of flight path, altitude, and system health. Trust boundaries between guidance, control, and actuation must be enforced to prevent single-function failures from cascading into loss of control. All data must be time-synchronized and validated against physical range limits and rate limits (airspeed, altitude, g-loading) before use in control calculations or pilot display.

### How

**Step 1 Ã¢â‚¬â€ Navigation Initialization and Measurement Capture:** GPS Receiver acquires satellite lock and outputs position/velocity/time fixes at 1 Hz over ARINC-429. INS Unit captures gyro rates and accelerometer data at 50 Hz and outputs attitude reference and inertial rates over MIL-STD-1553. Flight Director consumes these inputs continuously.

**Step 2 Ã¢â‚¬â€ Guidance Computation:** Flight Director runs at 10 Hz: fetches current position fix and inertial attitude, loads active waypoint plan, computes required roll/pitch/heading to fly from current position to next waypoint, outputs lateral and vertical guidance setpoints over ARINC-664 to Flight Control Computer.

**Step 3 Ã¢â‚¬â€ Control Law Execution and Servo Command Generation:** Flight Control Computer runs closed-loop control laws at 400 Hz: reads guidance setpoints (10 Hz), reads inertial rates from INS (50 Hz), computes aileron/elevator/rudder commands based on error between desired and actual attitude, outputs discrete servo commands over hardwired interface to Servo Actuator Cluster.

**Step 4 Ã¢â‚¬â€ Servo Feedback and Actuation:** Servo Actuator Cluster physically moves flight surfaces in response to digital commands, captures surface position and rate feedback over analog interfaces, returns feedback to Flight Control Computer at 100 Hz. Closed-loop control law adjusts commands based on feedback.

**Step 5 Ã¢â‚¬â€ Vehicle Management and State Aggregation:** Vehicle Management Computer runs at 20 Hz: polls Flight Control Computer for mode/fault/servo health, aggregates telemetry, computes display-ready video frames, broadcasts display frames to Primary Flight Display over ARINC-818 at 30 Hz, broadcasts system health snapshots back to Flight Director.

**Step 6 Ã¢â‚¬â€ Pilot Display Rendering:** Primary Flight Display renders video frames at 30 Hz with attitude indicator, altitude tape, flight path marker, and annunciations. All display updates use Vehicle Management Computer's aggregated health data.

### Who

### Actors

- **Pilot** Ã¢â‚¬â€ user of display and control inputs; depends on accurate flight path marker and mode annunciations

- **Flight Director** Ã¢â‚¬â€ guidance producer; consumes GPS/INS data; emits lateral/vertical setpoints
- **Flight Control Computer** Ã¢â‚¬â€ control law executor; consumes guidance setpoints and inertial feedback; emits servo commands

- **Servo Actuator Cluster** Ã¢â‚¬â€ physical actuator; responds to digital commands; provides analog position/rate feedback
- **Vehicle Management Computer** Ã¢â‚¬â€ data aggregator and display producer; concentrates FCC state and health; emits display video

- **GPS Receiver** Ã¢â‚¬â€ position source; emits position/velocity/time; no dependencies
- **INS Unit** Ã¢â‚¬â€ inertial reference; emits gyro rates and accelerometers; no dependencies

- **Primary Flight Display** Ã¢â‚¬â€ cockpit output; renders received video frames; emits user inputs for pilot control

### Dependencies

- Flight Director depends on continuous GPS fixes and INS attitude reference

- Flight Control Computer depends on Flight Director setpoints and INS inertial rates
- Servo Actuator Cluster depends on Flight Control Computer digital commands; provides feedback via analog lines

- Vehicle Management Computer depends on Flight Control Computer state and health data
- Primary Flight Display depends on Vehicle Management Computer video streams

## High-Level Interfaces

### Input Interfaces

- **GPS Position Feed** Ã¢â‚¬â€ RFC 4150 ARINC-429 word stream carrying position_lat, position_lon, altitude_msl, velocity_north, velocity_east, velocity_down, gps_time, position_status (fixed/float/no_lock); 1 Hz update rate; integrity constraint: position accuracy Ã¢â€°Â¤ 100 m CEP in nominal GPS conditions

- **Inertial Reference Feed** Ã¢â‚¬â€ MIL-STD-1553 deterministic word stream carrying pitch_rate, roll_rate, yaw_rate, pitch_accel, roll_accel, yaw_accel, reference_state (valid/invalid/aligning); 50 Hz update rate; integrity constraint: rate measurement accuracy Ã¢â€°Â¤ 0.1 deg/s, accel accuracy Ã¢â€°Â¤ 10 mG
- **Waypoint Plan Upload** Ã¢â‚¬â€ pilot input stream (via Primary Flight Display) selecting mission route; input validation: plan size Ã¢â€°Â¤ 256 waypoints, each waypoint within aircraft operating envelope (altitude, airspeed)

- **Servo Feedback Signals** Ã¢â‚¬â€ analog electrical signals from Servo Actuator Cluster carrying surface_position (0-5 V = 0-100% deflection), surface_rate (Ã¢Ë†â€™5 to +5 V = Ã¢Ë†â€™100 to +100 deg/s), actuator_health (discrete 0/1 status); feedback rate 100 Hz; integrity constraint: position transducer accuracy Ã¢â€°Â¤ 2% full scale

### Output Interfaces

- **Servo Command Bus** Ã¢â‚¬â€ hardwired discrete digital command lines from Flight Control Computer to Servo Actuator Cluster carrying aileron_cmd (digital word), elevator_cmd (digital word), rudder_cmd (digital word), trim_tab_cmd (digital word); 400 Hz transmit rate; output range Ã¢Ë†â€™100 to +100 command units (maps to Ã¢Ë†â€™25 to +25 degrees surface deflection)

- **Display Video Bus** Ã¢â‚¬â€ ARINC-818 deterministic video stream from Vehicle Management Computer to Primary Flight Display carrying video_frame_raw (progressive scan raster), annunciations (fault/warn/caution/advisory discrete bits), flight_path_marker (vector), mode_indication (enum); 30 Hz frame rate; video resolution 1024Ãƒâ€”768 minimum; color depth 24-bit RGB
- **System Health Broadcast** Ã¢â‚¬â€ ARINC-664 periodic message from Vehicle Management Computer to Flight Director carrying system_health (good/degraded/failed), network_status (all_up/partial_loss/link_down), time_sync_offset (milliseconds), nav_filter_confidence (0-100%); 2 Hz message rate; broadcast to all subsystems on ARINC-664 network

### Internal Processing Interfaces

- **Guidance Setpoint Exchange** Ã¢â‚¬â€ ARINC-664 deterministic word stream from Flight Director to Flight Control Computer carrying lateral_setpoint (degrees of roll), vertical_setpoint (degrees of pitch), throttle_setpoint (percent), mode_state (enum); 10 Hz update rate; range validation: lateral Ã¢Ë†Ë† [Ã¢Ë†â€™90Ã‚Â°, +90Ã‚Â°], vertical Ã¢Ë†Ë† [Ã¢Ë†â€™90Ã‚Â°, +90Ã‚Â°]

- **Inertial Rate Feedback** Ã¢â‚¬â€ internal MIL-STD-1553 loop-back from INS Unit to Flight Control Computer (in addition to Flight Director consumption) carrying gyro_rates (3-axis) and accel (3-axis); 50 Hz; enables closed-loop rate damping in control law
- **FCC State Poll** Ã¢â‚¬â€ ARINC-664 solicited query from Vehicle Management Computer to Flight Control Computer requesting fcc_mode (active mode enum), fault_flags (bit vector), servo_health_summary (bit vector); 20 Hz poll rate; response latency Ã¢â€°Â¤ 50 ms

- **LRU Health Exchange** Ã¢â‚¬â€ internal interconnect from Servo Actuator Cluster to Flight Control Computer returning surface_position (continuous feedback loop at 100 Hz) and discrete health bits (servo_fault, actuator_jam, pressure_low); enables servo health monitoring

## Component Pieces and Parts

### Navigation and Guidance Subsystem Components

### GPS Receiver

- **Function:** Acquires satellite ephemeris and pseudo-range measurements; computes position fix and velocity vector; validates solution integrity and reports confidence level

- **Interfaces:** Satellite RF antenna (input); ARINC-429 word stream to Flight Director (output, 1 Hz); internal serial link to Flight Director for configuration and status polling
- **Trust Boundaries:** None internal; RF antenna boundary is outside avionics scope

- **Failure Modes:** No satellite lock, position jump > 1 km, velocity jump > 50 m/s, time of week mismatch, antenna spoofing

### INS Unit (Inertial Measurement Unit)

- **Function:** Captures accelerometer and gyroscope measurements from integrated MEMS or ring-laser sensors; applies calibration constants; outputs attitude reference and inertial rates; manages alignment sequence on startup

- **Interfaces:** Physical vibration environment (input); MIL-STD-1553 inertial reference word stream to Flight Director and Flight Control Computer (output, 50 Hz); discrete alignment_ready signal to Flight Director
- **Trust Boundaries:** None internal; physical environment sensing boundary is outside avionics scope

- **Failure Modes:** Sensor bias drift, scale factor error, misalignment, temperature drift, power loss during alignment

### Flight Director

- **Function:** Fetches active waypoint plan; polls current GPS position and INS attitude every 100 ms; computes guidance errors (track error, altitude error, heading error); runs guidance law; outputs setpoints to Flight Control Computer every 100 ms

- **Interfaces:** ARINC-429 GPS position input (1 Hz); MIL-STD-1553 INS attitude input (50 Hz); ARINC-664 waypoint plan upload (pilot input via Primary Flight Display, async); ARINC-664 guidance setpoint output to Flight Control Computer (10 Hz); ARINC-664 health input from Vehicle Management Computer (2 Hz); internal memory and persistent storage for mission plan (non-volatile)
- **Trust Boundaries:** Guidance-Control Partition Ã¢â‚¬â€ setpoint outputs to FCC must be validated against physical envelope

- **Failure Modes:** Waypoint plan corruption, guidance law NaN/Inf, setpoint out of envelope, GPS/INS data stale, alignment sequence timeout

### Flight Control Subsystem Components

### Flight Control Computer

- **Function:** Fetches guidance setpoints and inertial rates every 2.5 ms (400 Hz rate); runs closed-loop control laws; computes servo command corrections based on error between actual and desired attitude; outputs discrete servo commands; monitors servo health feedback; reports state/faults to Vehicle Management Computer

- **Interfaces:** ARINC-664 guidance input from Flight Director (10 Hz); MIL-STD-1553 inertial rates from INS (50 Hz); discrete servo commands to Servo Actuator Cluster (400 Hz); analog feedback from servo actuators (100 Hz); ARINC-664 state/fault output to Vehicle Management Computer (polled at 20 Hz); internal watchdog timer and power-loss detection
- **Trust Boundaries:** Control-Actuation Partition Ã¢â‚¬â€ servo commands must be rate-limited and range-checked; feedback loop must detect servo saturation or jam

- **Failure Modes:** Guidance setpoint out of range (range check rejects), inertial rate stale (uses last valid), control law divergence (rate limiting prevents saturation), servo command loss (discrete line failure detected by FCC monitor circuit), servo feedback loss (open circuit or short detected)

### Servo Actuator Cluster

- **Function:** Receives discrete digital servo commands from FCC; converts commands to electro-hydraulic pilot pressures; moves flight surfaces (ailerons, elevator, rudder, trim tabs); captures surface position via potentiometer transducers; streams position and rate feedback over analog lines

- **Interfaces:** Discrete digital command lines from Flight Control Computer (400 Hz); analog feedback outputs to FCC (surface position, surface rate, health discrete); electro-hydraulic fluid supply (input); mechanical linkages to flight surfaces (output)
- **Trust Boundaries:** Digital-Actuation Partition Ã¢â‚¬â€ command inputs must be validated by FCC watchdog; feedback sensors must be independent from actuator control circuit

- **Failure Modes:** Command line open or short circuit, hydraulic supply pressure loss, servo jam, potentiometer drift or failure, feedback sensor failure

### Vehicle Management and Display Subsystem Components

### Vehicle Management Computer

- **Function:** Continuously polls Flight Control Computer for mode/fault/servo health data; aggregates health status from all subsystems; composes display-ready video frames with attitude, altitude, flight path marker, and annunciations; broadcasts periodic health snapshots to Flight Director and FCC; manages time synchronization across all subsystems

- **Interfaces:** ARINC-664 FCC state poll input (20 Hz solicited query); ARINC-664 health broadcast output to FCC/FD (2 Hz); ARINC-818 video output to Primary Flight Display (30 Hz); internal video compositing pipeline and frame buffer memory
- **Trust Boundaries:** None explicit internal; display output boundary is driver-specific (ARINC-818)

- **Failure Modes:** FCC polling timeout (uses last valid state), health broadcast loss (display shows "STALE" indicator), video frame buffer corruption (video output glitch), time synchronization loss (local clock drift)

### Primary Flight Display

- **Function:** Receives ARINC-818 video frames from Vehicle Management Computer at 30 Hz; renders attitude, altitude tapes, flight path marker, and mode annunciations on cockpit screen; captures pilot inputs (mode select, autopilot engagement, etc.) and forwards to Flight Director via Primary Flight Display controller

- **Interfaces:** ARINC-818 video input from VMC (30 Hz); physical CRT/LCD display panel (output); pilot control inputs (buttons, knobs, touchscreen) routed via discrete wiring and serial links to Flight Director
- **Trust Boundaries:** Cockpit-Avionics Boundary Ã¢â‚¬â€ pilot inputs must be debounced and validated before transmission to Flight Director; display output must not be affected by pilot control input events

- **Failure Modes:** Video loss (blank screen or last-frame-hold), display panel failure (pixel failure, brightness loss), pilot input debounce failure (spurious commands), serial link corruption

## Trust Boundaries and Data Flow Validation

### Explicit Trust Boundaries

1. **Guidance-Control Partition** Ã¢â‚¬â€ Separates guidance computation (Flight Director) from control law execution (FCC). All guidance setpoints crossing this boundary must be validated for physical envelope compliance: roll Ã¢Ë†Ë† [Ã¢Ë†â€™90Ã‚Â°, +90Ã‚Â°], pitch Ã¢Ë†Ë† [Ã¢Ë†â€™90Ã‚Â°, +90Ã‚Â°], altitude Ã¢Ë†Ë† [500 ft, 35,000 ft], airspeed Ã¢Ë†Ë† [50 kt, 250 kt].

1. **Control-Actuation Partition** Ã¢â‚¬â€ Separates control law execution (FCC) from electro-hydraulic actuation (Servo Cluster). All servo commands must be rate-limited (max 50Ã‚Â°/sec) and range-checked (Ã¢Ë†â€™100 to +100 command units). Feedback loop monitors for servo saturation, jam, or pressure loss.

1. **Actuation-Sensing Partition** Ã¢â‚¬â€ Separates analog sensor feedback (Servo Cluster) from digital processing (FCC). Feedback transducers must be independent from control circuit; potentiometer accuracy Ã¢â€°Â¤ 2% full scale; feedback loss detected within 10 ms.

1. **Cockpit-Avionics Boundary** Ã¢â‚¬â€ Separates pilot inputs from internal guidance/control functions. All pilot commands (mode select, autopilot engagement, route modification) must be debounced (20 ms hold) and validated before transmission to Flight Director.

### Data Flow Sensitivity Levels

- **GPS/INS Data** Ã¢â‚¬â€ Flight-critical (integrity required); position/velocity/attitude errors propagate directly into control law errors; requires time synchronization (< 10 ms skew) and range-limit validation

- **Guidance Setpoints** Ã¢â‚¬â€ Safety-critical (envelope must be validated); out-of-envelope setpoints could cause loss of control; FCC must reject setpoints outside physical limits
- **Servo Feedback** Ã¢â‚¬â€ Control-critical (closed-loop stability depends on feedback integrity); feedback transducers must be robust against vibration, temperature, and electro-magnetic interference

- **Display Video** Ã¢â‚¬â€ Pilot-critical (situational awareness); video loss requires clear "STALE" annunciation; glitches must not exceed 200 ms (imperceptible to pilot eye); frame drops must not exceed 1 per 30-second window

## Operational Constraints

1. **Real-Time Determinism** Ã¢â‚¬â€ All subsystems must execute with bounded latency and jitter: GPS polling Ã¢â€°Â¤ 1 Hz, INS updates Ã¢â€°Â¤ 50 Hz, guidance updates Ã¢â€°Â¤ 10 Hz, control law Ã¢â€°Â¤ 2.5 ms (400 Hz), servo feedback Ã¢â€°Â¤ 10 ms (100 Hz), display refresh Ã¢â€°Â¤ 33 ms (30 Hz).

1. **Time Synchronization** Ã¢â‚¬â€ All subsystems must maintain time offset Ã¢â€°Â¤ 10 ms relative to master time source (GPS 1PPS or atomic clock); time jumps > 100 ms trigger "TIME_SYNC_LOSS" fault.

1. **Fail-Safe Behavior** Ã¢â‚¬â€ Any subsystem detecting a critical fault (sensor loss, computation error, communication loss) must transition to safe state within 1 second: guidance Ã¢â€ â€™ straight and level hold, control Ã¢â€ â€™ pitch/roll trim, display Ã¢â€ â€™ "FAULT" annunciation.

1. **Power Loss Tolerance** Ã¢â‚¬â€ All subsystems must complete graceful shutdown within 500 ms of power loss; persistent data (mission plan, calibration, event log) must be committed to non-volatile storage within 100 ms.

## Threat Model Scope

This description models the avionics system as a complete real-time distributed system. Threats include: navigation spoofing (GPS jamming/false ephemeris), guidance setpoint injection (LLM-based waypoint corruption), control law divergence (numerical instability or parameter tampering), servo command interception (flight surface unauthorized deflection), feedback sensor tampering (attitude/rate false data), display injection (false annunciations or flight path marker), and time synchronization attacks (systematic clock offset inducing attitude error). All data flows crossing trust boundaries must be validated against physical constraints and time synchronization requirements.

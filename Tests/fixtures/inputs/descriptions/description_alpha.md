# Alpha UAV System

The Alpha UAV System is an unmanned aerial vehicle designed for intelligence, surveillance, and reconnaissance (ISR) missions. It operates in contested radio-frequency environments and must maintain command link integrity at all times.

## Navigation Subsystem

The Navigation Subsystem fuses GPS and IMU data to provide a continuous position and attitude estimate. Position fixes are generated at 10 Hz and forwarded to the Command and Control Subsystem over an internal UDP bus.

### GPS Receiver

The GPS Receiver component acquires satellite signals and outputs timestamped position fixes to the navigation bus.

#### Function: Acquire Satellite Signal

Searches for and locks onto GPS satellite signals. Produces a valid position lock before enabling position fix output.

#### Function: Output Position Fix

Formats a timestamped position fix and publishes it to the navigation bus at 10 Hz. This function is the upstream source for the GPS Position Interface (IF-001).

### Inertial Measurement Unit

The IMU component measures angular rate and linear acceleration and packages sensor frames for downstream consumers.

#### Function: Measure Inertial State

Samples gyroscope and accelerometer data, packages a sensor frame, and delivers it to the Command Processor over the IMU Telemetry Interface (IF-002).

## Command and Control Subsystem

The Command and Control Subsystem receives operator uplink messages over an encrypted TLS channel from the Ground Control Station (GCS). The Command Processor validates message integrity before passing commands to the autopilot. All uplink sessions require mutual TLS authentication.

### Command Processor

The Command Processor component hosts the command validation and routing logic.

#### Function: Validate Command Message

Checks integrity and authentication tokens of received operator uplink commands. Rejects any message that fails authentication or has a replayed session nonce.

#### Function: Route Command

Routes validated commands to the appropriate subsystem handler. Receives position context from the Output Position Fix function via the internal function-level interface (IF-005) to enforce geofence constraints before routing.

## Trust Boundaries

The external radio link between the GCS and the Command Processor crosses a trust boundary (IF-003). All data crossing this boundary must be authenticated and encrypted. Replay attacks must be mitigated via session nonces.

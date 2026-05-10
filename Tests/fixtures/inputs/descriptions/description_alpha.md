# Alpha UAV System

The Alpha UAV System is an unmanned aerial vehicle designed for intelligence, surveillance, and reconnaissance (ISR) missions. It operates in contested radio-frequency environments and must maintain command link integrity at all times.

## Navigation Subsystem

The Navigation Subsystem fuses GPS and IMU data to provide a continuous position and attitude estimate. Position fixes are generated at 10 Hz and forwarded to the Command and Control Subsystem over an internal UDP bus.

## Command and Control Subsystem

The Command and Control Subsystem receives operator uplink messages over an encrypted TLS channel from the Ground Control Station (GCS). The Command Processor validates message integrity before passing commands to the autopilot. All uplink sessions require mutual TLS authentication.

## Trust Boundaries

The external radio link between the GCS and the Command Processor crosses a trust boundary. All data crossing this boundary must be authenticated and encrypted. Replay attacks must be mitigated via session nonces.

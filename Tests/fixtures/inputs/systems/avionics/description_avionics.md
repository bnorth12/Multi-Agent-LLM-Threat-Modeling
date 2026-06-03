# Avionics Data Network

This aircraft avionics architecture combines four subsystems: navigation and guidance, fly-by-wire flight control, vehicle management, and cockpit display. The system supports high-integrity guidance and stability functions while presenting pilot-critical situational awareness data.

## Subsystem: Navigation and Guidance (SS-NAV-01)

The navigation subsystem contains a GPS Receiver (C-GPS-01) and an INS Unit (C-INS-01) with three gyros and three accelerometers. A Flight Director (C-FD-01) consumes position fixes and inertial reference data to compute lateral and vertical route-following guidance from waypoint plans.

Data flows originating here:

- **DF-201 GPS Position Feed** — C-GPS-01 → C-FD-01 over ARINC-429 carrying position_fix, velocity, gps_time. No trust boundary crossing.
- **DF-202 Inertial Reference Feed** — C-INS-01 → C-FCC-01 over MIL-STD-1553 carrying gyro_rates, accel_axes, attitude_ref. No trust boundary crossing.

## Subsystem: Fly-By-Wire Flight Control (SS-FCS-01)

The flight control subsystem contains a Flight Control Computer (C-FCC-01) and a Servo Actuator Cluster (C-SERVO-01). C-FCC-01 executes closed-loop control laws and issues discrete commands to servo actuators. Servo position and rate feedback are returned into the control loops.

Data flows in this subsystem:

- **DF-203 Guidance Command Bus** — C-FD-01 → C-FCC-01 over ARINC-664 carrying lateral_setpoint, vertical_setpoint, mode_state. **Trust boundary crossing: Guidance-Control Partition.**
- **DF-204 Actuator Command Bus** — C-FCC-01 → C-SERVO-01 over Discrete interface carrying aileron_cmd, elevator_cmd, rudder_cmd. **Trust boundary crossing: Digital-Actuation Boundary.**
- **DF-205 Servo Feedback Bus** — C-SERVO-01 → C-FCC-01 over Analog interface carrying surface_position, surface_rate, actuator_health. **Trust boundary crossing: Actuation-Sensing Boundary.**

## Subsystem: Vehicle Management (SS-VMC-01)

The vehicle management subsystem contains a Vehicle Management Computer (C-VMC-01) that concentrates avionics data from the flight control computer and composes display feeds for the cockpit. It also broadcasts health and time-synchronisation data back to the flight director.

Data flows in this subsystem:

- **DF-206 FCC State Bus** — C-FCC-01 → C-VMC-01 over ARINC-664 carrying fcc_mode, fault_flags, servo_summary. No trust boundary crossing.
- **DF-207 Display Video Bus** — C-VMC-01 → C-PFD-01 over ARINC-818 carrying video_frame, annunciations, flight_path_marker. No trust boundary crossing.
- **DF-208 Health Snapshot Bus** — C-VMC-01 → C-FD-01 over ARINC-664 carrying system_health, network_status, time_sync. No trust boundary crossing.

## Subsystem: Flight Display (SS-DISP-01)

The display subsystem contains a Primary Flight Display (C-PFD-01) that renders pilot-facing graphics, annunciations, and flight path markers received from the Vehicle Management Computer.

## Trust Boundaries

Three explicit trust boundaries exist in this architecture:

1. **Guidance-Control Partition** — separates guidance computation (SS-NAV-01 / C-FD-01) from flight control law execution (SS-FCS-01 / C-FCC-01). Crossed by DF-203.
1. **Digital-Actuation Boundary** — separates digital command generation (C-FCC-01) from electro-hydraulic actuation hardware (C-SERVO-01). Crossed by DF-204.
1. **Actuation-Sensing Boundary** — separates analog sensor feedback (C-SERVO-01) from digital control processing (C-FCC-01). Crossed by DF-205.

All data crossing these boundaries must be validated against timing constraints, range limits, and integrity monitors before use in safety-critical control or guidance calculations.

## Network and Interface Standards

- **ARINC-429** — low-bandwidth navigation words (position, time).
- **MIL-STD-1553** — deterministic inertial reference exchange in control contexts.
- **ARINC-664** — switched deterministic avionics network traffic between guidance, control, and vehicle management computers.
- **Discrete / Analog** — interfaces between control computers and actuator hardware.
- **ARINC-818** — high-bandwidth video and ancillary data from VMC to flight displays.

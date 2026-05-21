# Alpha UAV System

The Alpha UAV System is an unmanned air vehicle designed for strike, SEAD, DEAD, and ISR missions. It also supports peacetime ISR missions such as remote wildfire detection. Alpha operates in contested RF environments and maintains command-link integrity through Charlie and Bravo relay paths.

## Navigation Subsystem

The Navigation Subsystem fuses GPS, IMU, and EGI data to provide continuous position, timing, and attitude estimates for mission execution.

## Command and Control Subsystem

The Command and Control Subsystem receives relayed operator and mission-package updates over encrypted channels. The Command Processor validates message integrity and authorization before dispatching validated plans to the onboard mission computer.

## Mission Management Subsystem

The Mission Management Subsystem hosts the Alpha Mission Computer. It manages mission sensors, communication radios, data links, and EGI-informed route execution. It executes mission packages containing waypoints, flight plans, communications schedules and frequencies, route plans, targeting and weapon release data, keep-out and threat-avoidance areas, and ISR sensor coverage plans.

## Trust Boundaries

The external relay path between Bravo and Alpha crosses the satellite-link trust boundary. All data crossing this boundary must be authenticated and encrypted, with replay protection and mission-package signature validation.

# Essential Flight Services

## Scope

Foundational aircraft services that must be available to safely sustain flight.

## L1 Service Groups

1. Propulsion
1. Vehicle Systems (utilities)
1. Data Integrity and Domain Isolation

## Vehicle Systems Utility Grouping

Most aircraft utilities are grouped under `Vehicle Systems` for architectural baseline purposes. In this decomposition, Vehicle Systems includes:

1. Power Generation and Distribution
1. Pneumatic and Environmental Services
1. Hydraulic Services
1. Aircraft Health and Condition Management

## Current Files

- `propulsion.md`
- `electrical_power_generation_and_distribution.md`
- `pneumatic_and_environmental_services.md`
- `hydraulic_services.md`
- `aircraft_health_and_condition_management.md`
- `data_integrity_and_domain_isolation.md`
- `vehicle_systems_grouping.md`

## Platform Placement

- Flight Controls: sustaining services that preserve safe control authority and availability.
- Vehicle Management: primary placement for utilities, health monitoring, and cross-domain integrity enforcement.
- Mission Systems and Passenger Systems: interface through controlled boundaries only.

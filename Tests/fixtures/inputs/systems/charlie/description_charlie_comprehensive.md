# Charlie Satellite Communications Terminal - Comprehensive Threat Model

## System Role

Charlie is both the mandatory encrypted relay segment and the mission-planning generation segment for the UAS Weapon System.

## Relay Role

Charlie performs:

- Encrypted command uplink relay to Alpha
- Encrypted telemetry downlink relay from Alpha to Bravo
- Session-key lifecycle enforcement and traffic shaping

## Mission Planning Role

Charlie hosts the Mission Planning Computer, which builds executable mission packages from:

- All-source intelligence
- Flight-planning resources (airspace, terrain, weather, constraints)
- Targeting and weapon data
- Communications frequency and schedule plans
- Keep-out and threat-avoidance areas
- ISR sensor planning and coverage goals

Generated plans are sent to Bravo for policy validation and release, then relayed for Alpha execution.

## Mission Types Supported

- Strike
- SEAD
- DEAD
- ISR (including peacetime wildfire ISR)

## Trust Boundaries

- Satellite link boundary for Alpha relay traffic
- Operations network boundary for Bravo mission-plan exchange
- Planning intelligence boundary for all-source planning inputs

## Threat Modeling Context

Charlie is modeled as both cryptographic relay and plan-generation source. Future mission-criticality controls can score planning integrity, relay assurance, and key-rotation health.

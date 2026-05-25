# Air-Ground Operational Communications

## Purpose

Support safety-critical and mission-critical communication between flight crew and external operational authorities.

## L2 Subfunctions

1. Voice Communication Management
1. Message Prioritization and Routing
1. Communication Availability and Fallback Management
1. Communication Logging and Audit Trail
1. Manage Surveillance Broadcast Exchange (`ADS-B In` and `ADS-B Out`)

## L3 Examples

- `ADS-B Out` position/intent broadcast management.
- `ADS-B In` traffic and situational awareness data reception.
- Broadcast data integrity, plausibility checks, and conflict handling.

## Identification/Surveillance Mode Variants

- Military-oriented implementations may include IFF modes 1 through 5.
- Commercial-oriented implementations commonly include transponder mode C (altitude reporting), `ADS-B Out`, and `ADS-B In`.
- Some commercial environments may include UAT-based ADS-B services.

## Threat-Relevant Considerations

- Message authenticity and continuity are critical to operational safety.
- Priority inversion can delay urgent instructions.
- Logging integrity affects post-event investigation and compliance.

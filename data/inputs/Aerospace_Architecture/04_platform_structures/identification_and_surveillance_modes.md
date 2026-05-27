# Identification and Surveillance Modes

## Purpose

Capture platform-specific identification and surveillance mode references used in architecture and threat-analysis contexts.

## Military Baseline

- Military identification commonly references IFF modes 1 through 5.
- Military implementations may integrate additional mission-network identification workflows under Mission Systems.

## Commercial Baseline

- Commercial surveillance commonly includes transponder mode C (altitude reporting).
- Commercial environments commonly use `ADS-B Out` and `ADS-B In`.
- Some environments may include UAT-based ADS-B services depending on region and operational context.

## Architecture Placement Guidance

- Military-specific identification/surveillance behaviors are typically grouped under Mission Systems communications.
- Commercial identification/surveillance and operational communication are typically grouped under Vehicle Management communications.

## Threat-Relevant Considerations

- False identity/surveillance data can corrupt traffic awareness and decision support.
- Mode or source confusion between military and civil contexts can create operational hazards.
- Data-origin integrity and plausibility checking should be explicit in both platform variants.

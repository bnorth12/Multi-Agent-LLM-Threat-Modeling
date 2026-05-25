# Navigation Sensor Management

## Purpose

Manage navigation sensor configuration, integrity checks, and fusion inputs used for positioning and guidance.

## L2 Subfunctions

1. Manage Sensor Source Selection
1. Validate Sensor Health and Integrity
1. Detect Spoofing/Jamming Indicators
1. Publish Position and Uncertainty Estimates

## Threat-Relevant Considerations

- Spoofed sensor inputs can poison guidance and route decisions.
- Sensor-source switching logic is high impact when GNSS or radio aids degrade.
- Integrity-flag suppression can hide unsafe confidence loss.

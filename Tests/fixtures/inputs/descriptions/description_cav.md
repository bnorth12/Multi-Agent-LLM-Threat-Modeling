# CAV Validation Scenario (Charlie + Avionics)

This scenario combines the Charlie satellite communications context with an
avionics mission context for live LLM browser validation.

## Charlie Communications Segment

- Ground terminal includes an Encryption Gateway subsystem and Traffic Shaping subsystem.
- Key Distribution Module rotates keys and signals activation to Bulk Encryption Module.
- Satellite link and operations network boundaries are explicit trust boundaries.

## Avionics Mission Segment

- Flight control, navigation, and telemetry components exchange data over constrained interfaces.
- Mission data integrity and command/authentication controls are required for uplink/downlink paths.
- Safety-critical command paths must be isolated from non-critical telemetry channels.

## Validation Intent

Use this markdown narrative with `icd_charlie_v1.xlsx` during a live browser run.
The run should produce non-zero token usage for live stages and preserve uploaded
markdown content context in prompts and generated artifacts.

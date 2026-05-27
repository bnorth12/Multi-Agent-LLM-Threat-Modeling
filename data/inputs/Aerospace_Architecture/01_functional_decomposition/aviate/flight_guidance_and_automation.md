# Flight Guidance and Automation

## Purpose

Provide trajectory-following and pilot-assistance behaviors with explicit control-authority boundaries.

## Control-Authority Variants

### Fly-by-Wire (FBW) Integrated Control

- Automation and pilot inputs are mediated through control laws.
- High authority over control surfaces through flight-control computers.
- Usually integrated with envelope protection and mode-managed handling qualities.

### Autopilot with Limited Control Authority

- Autopilot provides guidance-following assistance within bounded authority.
- Pilot retains direct override and primary control priority.
- Authority limits and disconnect logic are explicit safety controls.

## L2 Subfunctions

1. Manage Guidance Modes
1. Track Lateral/Vertical Commands
1. Manage Autopilot Engagement and Disengagement
1. Enforce Authority Limits and Override Rules
1. Manage Reversion and Degraded Control Modes
1. Annunciate Automation State

## L3 Examples

- Determine authority state across pilot, autopilot, and mission-advisory inputs.
- Validate authority-transition preconditions before capture, transfer, or disconnect.
- Execute authority transfer with deterministic annunciation and override priority.
- Detect ambiguous or conflicting authority state.
- Trigger degraded-mode entry and controlled reversion when automation integrity is lost.
- Verify reversion completeness before normal mode restoration.

## Threat-Relevant Considerations

- Guidance-mode spoofing or false annunciation can induce hazardous pilot action.
- Unauthorized autopilot engagement/disengagement can disrupt trajectory safety.
- Authority-limit corruption can transform assistive automation into unsafe control behavior.

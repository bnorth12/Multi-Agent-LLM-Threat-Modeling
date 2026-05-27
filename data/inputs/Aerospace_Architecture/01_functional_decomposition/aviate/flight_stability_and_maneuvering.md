# Flight Stability and Maneuvering

## Purpose

Maintain aircraft attitude, control response, and maneuver execution within flight envelope constraints.

## L2 Subfunctions

1. Sense Aircraft State
1. Compute Control Laws
1. Command Control Surfaces and Effectors
1. Enforce Envelope Protection
1. Provide Handling-Quality Management

## L3 Examples

- Attitude/rate sensing and validation.
- Control-law mode management (normal, alternate, direct).
- Effector command allocation and monitor.
- Limit protection for angle, speed, load factor, and bank.

## Threat-Relevant Considerations

- Invalid sensor state propagation can destabilize control loops.
- Mode confusion between manual and augmented control can create unsafe commands.
- Envelope-protection bypass or corruption can increase loss-of-control risk.

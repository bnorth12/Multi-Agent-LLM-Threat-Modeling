# Guidance and Trajectory Management

## Purpose

Generate lateral and vertical intent that can be executed by pilot or automation.

## L2 Subfunctions

1. Compute Trajectory Intent
1. Apply Performance and Constraint Models
1. Publish Guidance Targets
1. Monitor Trajectory Conformance

## Threat-Relevant Considerations

- Constraint data manipulation can create unstable or unsafe routes.
- Guidance-target integrity is critical where automation tracks computed intent.
- Conformance-monitor corruption can hide divergence.

# Sensor Correlation and Fusion

## Purpose

Correlate and fuse multi-sensor inputs into coherent tracks, detections, or situational products.

## L2 Subfunctions

1. Normalize Multi-Sensor Inputs
1. Correlate Observations Across Sources
1. Generate Fused Tracks and Confidence Metrics
1. Resolve Conflicts and Ambiguities
1. Perform Multispectral Sensor Fusion

## L3 Correlation/Fusion Scope

- Correlate radar, hyperspectral, `WAMI`, `IRST`, `EO/IR`, and warning-system observations.
- Execute multispectral fusion for track confirmation and classification confidence improvement.
- Fuse mission data-link sourced tracks with onboard observations where policy permits.

## Threat-Relevant Considerations

- Input poisoning can bias correlation outcomes.
- Confidence-metric manipulation can overstate uncertain products.
- Conflict-resolution logic is a high-impact integrity boundary.

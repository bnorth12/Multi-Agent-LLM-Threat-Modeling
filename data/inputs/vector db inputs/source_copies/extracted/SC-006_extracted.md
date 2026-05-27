# SC-006 Extracted

- source_ref: SC-006
- normalized_title: RFC 9147 DTLS 1.3 Security-Critical Assumptions
- category: standards
- readiness: high

## Extracted Content Blocks

1. DTLS 1.3 extends TLS 1.3 security with datagram-specific reliability and anti-replay controls.
1. Epoch and key update handling are central to resisting reordering and stale-packet acceptance.
1. ACK and retransmission behavior introduce additional state-machine complexity that should be modeled as attack surface.
1. Operational deployments must tune replay windows and timeout behavior for constrained or lossy networks.

## Caveats

Captured from RFC Editor mirror text due datatracker access failure.

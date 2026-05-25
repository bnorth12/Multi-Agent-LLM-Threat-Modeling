# SC-005 Extracted

- source_ref: SC-005
- normalized_title: RFC 8446 TLS 1.3 Security-Critical Assumptions
- category: standards
- readiness: high

## Extracted Content Blocks

1. TLS 1.3 key schedule is HKDF-based with strict traffic-secret transitions and key update guidance.
1. 0-RTT is explicitly replay-sensitive; applications must only send replay-safe operations in early data.
1. Record protocol mandates AEAD protections, per-record nonce rules, and strict alert/error handling semantics.
1. Implementations should enforce limits on key usage and trigger rekey before safety margins erode.

## Caveats

Captured from RFC Editor mirror text equivalent to canonical RFC content.

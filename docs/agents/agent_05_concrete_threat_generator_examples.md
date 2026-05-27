# Agent 05 Concrete Threat Generator Examples

Purpose: hold reference schema and exemplar threat objects for prompt calibration and analyst review.

## Threat Object Template

```json
{
  "name": "ARINC 429 Navigation Data Spoofing",
  "description": "Adversary injects crafted ARINC 429 frames to corrupt FMC navigation inputs. Likelihood rationale: broadcast-style bus exposure and weak source authentication can enable spoof injection. Impact rationale: falsified navigation data can drive mission-path deviation and safety-relevant downstream control error.",
  "mitre_attack_technique": [
    "ATT&CK:T0856 - Spoof Reporting Message"
  ],
  "capec_id": "CAPEC-148 - Content Spoofing",
  "cwe_id": "CWE-290 - Authentication Bypass by Spoofing",
  "likelihood": 3,
  "impact": 5,
  "mitigations_technical": [],
  "mitigations_administrative": []
}
```

## Example Qualifying Data Flow

```json
{
  "id": "DF-001",
  "name": "GPS to FMC",
  "protocol": "ARINC 429",
  "stride": {
    "S": 3,
    "T": 4,
    "R": 2,
    "I": 2,
    "D": 4,
    "E": 1
  },
  "threats": [
    {
      "name": "ARINC 429 Navigation Data Spoofing",
      "description": "Adversary injects crafted ARINC 429 frames to corrupt FMC navigation inputs. Likelihood rationale: broadcast-style bus exposure and weak source authentication can enable spoof injection. Impact rationale: falsified navigation data can drive mission-path deviation and safety-relevant downstream control error.",
      "mitre_attack_technique": [
        "ATT&CK:T0856 - Spoof Reporting Message"
      ],
      "capec_id": "CAPEC-148 - Content Spoofing",
      "cwe_id": "CWE-290 - Authentication Bypass by Spoofing",
      "likelihood": 3,
      "impact": 5,
      "mitigations_technical": [],
      "mitigations_administrative": []
    }
  ]
}
```

## Notes

- Generate threats only when at least one STRIDE category score is >= 3.
- Keep taxonomy fields in ID plus name format.
- Preserve full canonical graph shape in runtime outputs.

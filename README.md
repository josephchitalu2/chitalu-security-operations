# Chitalu Security Operations

**Chitalu Software Solutions**

A planned security operations product integrating endpoint and network telemetry, incident investigation and controlled response. The initial repository contains architecture and release requirements; no sensors, detections or response actions have been deployed.

## Direction

- Wazuh-based endpoint/log visibility and integration where appropriate.
- Suricata-based network IDS/IPS telemetry where traffic access is available.
- Original event normalization, correlation, incident workflow and business reporting.
- Audited, permission-controlled response actions with a recovery path.
- A separate isolated malware and reverse-engineering lab for deeper investigation.

See [architecture](docs/ARCHITECTURE.md), [release requirements](docs/RELEASE_REQUIREMENTS.md) and [upstream references](docs/REFERENCES.md).

This design does not claim a mature EDR product, universal attack detection or deployed protection. Real validation and operational support are part of the full release scope.

## Maintenance

[Verification](docs/TESTING.md) · [Contributing](CONTRIBUTING.md) · [Security reporting](SECURITY.md)

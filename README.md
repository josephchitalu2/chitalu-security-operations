# Chitalu Security Operations

**Chitalu Software Solutions**

A security operations project for turning endpoint and network events into
reviewable cases. The first working feature replays fictional sign-in events
and links each case to the failures that triggered it.

## Run the sign-in detection demo

From the repository root, with Python 3.10 or later:

```bash
python3 -m secops.replay fixtures/sign_in_demo.jsonl
```

The sample produces one case for `demo-student` on `demo-workstation-01`,
with the three source event IDs. It also reports one duplicate and one malformed
record. The demo uses the Python standard library and reads a local file.
See the [exercise](docs/FIRST_DETECTION.md) for the event format, rule and sample
result.

## Use the detector from Codex

The optional local MCP server exposes the bundled replay and a tool for
small synthetic JSON Lines inputs. See the [MCP setup](docs/MCP.md) to
register it with Codex and run a tool call. The CLI above remains usable
with no additional packages.

## Direction

- Wazuh-based endpoint/log visibility and integration where appropriate.
- Suricata-based network IDS/IPS telemetry where traffic access is available.
- Original event normalization, correlation, incident workflow and business reporting.
- Audited, permission-controlled response actions with a recovery path.
- A separate isolated malware and reverse-engineering lab for deeper investigation.

See the [architecture](docs/ARCHITECTURE.md), [release requirements](docs/RELEASE_REQUIREMENTS.md) and [upstream references](docs/REFERENCES.md).
The replay is a batch exercise for synthetic data. Live collection, an incident
workspace and automated response are still planned.

## Maintenance

[Verification](docs/TESTING.md) · [Contributing](CONTRIBUTING.md) · [Security reporting](SECURITY.md)

# Security Operations Architecture

## Layers

| Component | Purpose |
|---|---|
| Endpoint agents and configured system logs | Collect authorized endpoint observations |
| Network sensor | Inspect traffic from a suitable capture or inline point |
| Ingestion adapters | Authenticate sources, validate schemas and track source health |
| Normalization | Map timestamps, assets, event types, principals and source evidence into a common schema |
| Correlation | Link related events, deduplicate repeats and produce explainable cases |
| Incident workspace | Search, timelines, notes, severity, assignment and evidence references |
| Response workflow | Restrict and audit approved actions; capture outcome and rollback |
| Business reporting | Explain affected assets, unresolved risks and completed work |

## Engine integrations

Wazuh is a candidate for log analysis, inventory, file-integrity monitoring and configured active response. Suricata is a candidate for network IDS, IPS and network security monitoring. Verify supported versions and interfaces during implementation; preserve upstream licensing and attribution.

A web dashboard does not obtain endpoint visibility without telemetry sources. A remote network sensor cannot automatically see traffic inside a business LAN. Traffic capture and IPS enforcement need an explicitly designed placement. Treat encrypted traffic visibility as a design constraint, not a guarantee of full payload inspection.

These long-running collection and indexing components require appropriate infrastructure; a static website deployment alone is not a security operations backend.

## Original engineering scope

Implement authenticated ingestion, source health, deduplication, schema validation, correlation rules, searchable timelines, case ownership, audit history, notification policies and business reporting. Document rule logic, test positive and negative fixtures and track false positives.

If serving multiple businesses, enforce tenant separation in storage, queries, notifications and administrative access. Secrets, real evidence and private customer logs must stay outside the source repository.

## Response controls

Begin with visibility and case generation. Enable blocking or endpoint response only after validation, defined authority, approvals, an audit record, safe timeouts and recovery tests. Changing a system should be an explicit state transition with a recorded outcome, not an untracked side effect of an alert.

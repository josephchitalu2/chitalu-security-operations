# First detection exercise: repeated sign-in failures

This is a proposed acceptance exercise for the detection pipeline. There is no
collector, rule engine, incident workspace or automated response in this repo yet.
Use fictional identities and synthetic events.

## Proposed rule

Create one review case when three distinct sign-in failures for the same
`asset_id` and `account_id` occur within a five-minute window. Use event time,
keep timestamps in UTC, and retain the source event IDs so a reviewer can see why
the rule fired. Treat the case as a reason to investigate.

| Input to exercise | Expected result |
| --- | --- |
| Three distinct failures at 10:00, 10:01 and 10:04 UTC for the same account and asset | One case with all three event IDs. |
| Two distinct failures and a duplicate of the second event | No case; deduplicate before counting. |
| Three failures divided across two different accounts | No case; group by both account and asset. |
| Three failures at 10:00, 10:01 and 10:06 UTC | No case within five minutes. |
| Event with no source event ID or invalid timestamp | Reject or quarantine it with a reason; it does not count. |

## What to build and verify first

1. Define a normalized event and a fixture file.
2. Build a replay that takes that file and emits a case record with the matched event IDs.
3. Add the positive and negative cases above. Replay the same input twice to check
   that repeated ingestion does not create another case.
4. Check that a reviewer can trace each case to the original synthetic events.

Do the first run with synthetic fixtures and without a live sensor or response
action. Connect authorized telemetry only after the replay works. The
[architecture](ARCHITECTURE.md) explains where Wazuh and Suricata could fit; the
[release requirements](RELEASE_REQUIREMENTS.md) cover later integration and response.

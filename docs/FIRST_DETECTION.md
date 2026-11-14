# First detection exercise: repeated sign-in failures

Run the replay from the repository root with Python 3.10 or later:

```bash
python3 -m secops.replay fixtures/sign_in_demo.jsonl
```

The demo emits JSON with one review case, five accepted events, one duplicate
and one rejected record. Open [the fixture](../fixtures/sign_in_demo.jsonl)
and find `demo-01`, `demo-02` and `demo-03`: these are the case's evidence.
The first is at 10:00 UTC and the third is at 10:04 UTC. One record uses a
`+02:00` offset; the replay converts it to UTC before sorting the events.

## Rule

Create a review case when three distinct sign-in failures for the same asset
and account occur within five minutes, inclusive. Count by event time, even
when file order differs. A success does not count as a failure or reset the
window. Consecutive matching windows for one asset and account produce one
case with the first three matching event IDs. Once a window no longer meets
the rule, a later matching window can open another case.

The case carries the rule ID, asset and account IDs, first failure time,
threshold time and source event IDs. Replaying the same evidence produces the
same case ID, so a downstream consumer can deduplicate it. A case is a reason
to review the evidence; this demo does not infer compromise.

| Synthetic input | Expected result |
| --- | --- |
| Three failures at 10:00, 10:01 and 10:04 UTC for one asset and account | One case with all three source event IDs. |
| Two distinct failures and a copy of the second event | No case; the copy is counted as a duplicate. |
| Three failures divided between different accounts or different assets | No case; the failures must match both IDs. |
| Three failures at 10:00, 10:01 and 10:05 UTC | One case; exactly five minutes qualifies. |
| Three failures at 10:00, 10:01 and 10:06 UTC | No case within five minutes. |
| A missing event ID, invalid timestamp or malformed JSON | A line number and reason in `rejected_records`; the row does not count. |

## Event format

Use UTF-8 JSON Lines: one object per line. Each object needs an `event_id`
unique across the input, a `timestamp` with an explicit offset or `Z`, an
`asset_id`, an `account_id` and an `event_type` of `sign_in_failure` or
`sign_in_success`. The three identifiers are case sensitive, printable and
limited to 128 characters, with no surrounding whitespace. Blank lines and
extra object fields are ignored. Exact duplicates of a normalized event are
counted once. If valid rows reuse an ID for different events, all valid rows
with that ID are rejected.

Valid rows still replay when other records are rejected. Read the
`rejected_records` field for data quality issues. An unreadable file exits
with an error and does not emit a report.

## Code map and scope

[`secops/replay.py`](../secops/replay.py) validates and deduplicates the events
and prints the result. [`secops/detection.py`](../secops/detection.py) groups
failures by account and asset, sorts them by event time and builds the cases.
The replay loads the fixture into memory and does not store cases between runs.
Use fictional identities and synthetic events. There is no live sensor or
response action in this exercise. See [testing](TESTING.md) to verify the
cases and [architecture](ARCHITECTURE.md) for the planned pipeline.

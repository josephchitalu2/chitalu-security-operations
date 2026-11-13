"""Verify the replay against synthetic examples and boundary cases."""

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from secops.replay import replay


ROOT = Path(__file__).resolve().parents[1]


def failure(event_id: str, time: str, **changes) -> str:
    return json.dumps({
        "event_id": event_id,
        "timestamp": f"2026-11-13T{time}Z",
        "asset_id": "demo-laptop",
        "account_id": "demo-learner",
        "event_type": "sign_in_failure",
        **changes,
    })


class ReplayTests(unittest.TestCase):
    def test_three_distinct_failures_use_utc_event_order(self):
        records = [
            failure("three", "10:04:00"),
            failure("one", "10:00:00"),
            failure("two", "12:01:00", timestamp="2026-11-13T12:01:00+02:00"),
        ]
        report = replay(records)
        self.assertEqual(report["accepted_events"], 3)
        self.assertEqual(report["rejected_records"], [])
        self.assertEqual(len(report["cases"]), 1)
        case = report["cases"][0]
        self.assertEqual(case["event_ids"], ["one", "two", "three"])
        self.assertEqual(case["first_failure_utc"], "2026-11-13T10:00:00Z")
        self.assertEqual(case["threshold_reached_utc"], "2026-11-13T10:04:00Z")
        self.assertEqual(replay(reversed(records)), report)

    def test_duplicate_with_equivalent_timestamp_does_not_count(self):
        report = replay([
            failure("one", "10:00:00"),
            failure("two", "10:01:00"),
            failure("two", "12:01:00", timestamp="2026-11-13T12:01:00+02:00"),
        ])
        self.assertEqual(report["accepted_events"], 2)
        self.assertEqual(report["duplicate_events"], 1)
        self.assertEqual(report["cases"], [])

    def test_conflicting_event_ids_are_all_excluded(self):
        report = replay([
            failure("one", "10:00:00"),
            failure("conflict", "10:01:00"),
            failure("three", "10:02:00"),
            failure("conflict", "10:03:00"),
        ])
        self.assertEqual(report["accepted_events"], 2)
        self.assertEqual(report["duplicate_events"], 0)
        self.assertEqual(report["cases"], [])
        self.assertEqual(report["rejected_records"], [
            {"line": 2, "reason": "event_id identifies conflicting records"},
            {"line": 4, "reason": "event_id identifies conflicting records"},
        ])

    def test_both_account_and_asset_are_required_to_match(self):
        for changes in ({"account_id": "demo-other"}, {"asset_id": "demo-desktop"}):
            with self.subTest(changes=changes):
                report = replay([
                    failure("one", "10:00:00"),
                    failure("two", "10:01:00"),
                    failure("three", "10:02:00", **changes),
                ])
                self.assertEqual(report["cases"], [])

    def test_five_minutes_is_inclusive(self):
        for final_time, expected in [("10:05:00", 1), ("10:05:00.000001", 0), ("10:06:00", 0)]:
            with self.subTest(final_time=final_time):
                report = replay([
                    failure("one", "10:00:00"),
                    failure("two", "10:01:00"),
                    failure("three", final_time),
                ])
                self.assertEqual(len(report["cases"]), expected)

    def test_success_is_accepted_but_does_not_count(self):
        report = replay([
            failure("one", "10:00:00"),
            failure("two", "10:01:00", event_type="sign_in_success"),
            failure("three", "10:02:00"),
        ])
        self.assertEqual(report["accepted_events"], 3)
        self.assertEqual(report["cases"], [])

    def test_consecutive_matching_windows_yield_one_case_then_a_separate_burst(self):
        report = replay([
            failure("one", "10:00:00"),
            failure("two", "10:01:00"),
            failure("three", "10:02:00"),
            failure("four", "10:04:00"),
            failure("five", "10:06:00"),
            failure("six", "10:12:00"),
            failure("seven", "10:13:00"),
            failure("eight", "10:14:00"),
        ])
        cases = report["cases"]
        self.assertEqual([c["event_ids"] for c in cases], [
            ["one", "two", "three"],
            ["six", "seven", "eight"],
        ])
        self.assertNotEqual(cases[0]["case_id"], cases[1]["case_id"])

    def test_invalid_rows_have_line_numbers_and_do_not_stop_replay(self):
        invalid = [
            failure(None, "10:01:00"),
            failure("bad-time", "10:01:00", timestamp="2026-11-13T10:01:00"),
            failure("bad-date", "10:01:00", timestamp="2026-11-31T10:01:00Z"),
            failure("bad-type", "10:01:00", event_type=["sign_in_failure"]),
            failure("bad-json-constant", "10:01:00", score=float("nan")),
            failure("bad-account", "10:01:00", account_id="  "),
            '{"event_id":"duplicate","event_id":"duplicate"}',
            '{"not-json":',
            '["not an object"]',
        ]
        report = replay(["", failure("one", "10:00:00"), *invalid, failure("two", "10:02:00")])
        self.assertEqual(report["accepted_events"], 2)
        self.assertEqual(report["cases"], [])
        self.assertEqual([r["line"] for r in report["rejected_records"]], list(range(3, 12)))
        self.assertIn("event_id", report["rejected_records"][0]["reason"])
        self.assertIn("timestamp", report["rejected_records"][1]["reason"])

    def test_cli_replay_is_repeatable_and_cases_trace_to_fixture(self):
        path = ROOT / "fixtures" / "sign_in_demo.jsonl"
        command = [sys.executable, "-m", "secops.replay", str(path)]
        def run():
            return subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True, timeout=5)

        first, second = run(), run()
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, "")
        report = json.loads(first.stdout)
        self.assertEqual(report["accepted_events"], 5)
        self.assertEqual(report["duplicate_events"], 1)
        self.assertEqual(len(report["cases"]), 1)
        self.assertEqual(report["rejected_records"][0]["line"], 7)
        fixture_rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        ids = report["cases"][0]["event_ids"]
        self.assertEqual(ids, ["demo-01", "demo-02", "demo-03"])
        self.assertLessEqual(set(ids), {row.get("event_id") for row in fixture_rows})

    def test_unreadable_fixture_exits_without_a_report(self):
        with TemporaryDirectory() as folder:
            missing = Path(folder) / "missing.jsonl"
            result = subprocess.run(
                [sys.executable, "-m", "secops.replay", str(missing)],
                cwd=ROOT, capture_output=True, text=True, timeout=5,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("Could not read fixture", result.stderr)


if __name__ == "__main__":
    unittest.main()

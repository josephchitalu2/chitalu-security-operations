"""Read a local JSON Lines fixture and print a deterministic case report."""

import argparse
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Iterable

from .detection import SignInEvent, detect


_TIMESTAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?"
    r"(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)",
    re.ASCII,
)
_EVENT_TYPES = ("sign_in_failure", "sign_in_success")


def _json_object(fields: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in fields:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _timestamp(value: object) -> datetime:
    reason = "timestamp must be a valid date and time with an explicit UTC offset"
    if not isinstance(value, str) or not _TIMESTAMP.fullmatch(value):
        raise ValueError(reason)
    fmt = "%Y-%m-%dT%H:%M:%S" + (".%f" if "." in value else "") + "%z"
    try:
        return datetime.strptime(value, fmt).astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise ValueError(reason) from None


def _identifier(record: dict[str, object], key: str) -> str:
    value = record.get(key)
    if (not isinstance(value, str) or not 1 <= len(value) <= 128
            or value != value.strip() or not value.isprintable()):
        raise ValueError(f"{key} must be a nonblank, printable string of at most 128 characters")
    return value


def _event(line: str) -> SignInEvent:
    try:
        record = json.loads(line, object_pairs_hook=_json_object, parse_constant=_invalid_constant)
    except (ValueError, RecursionError):
        raise ValueError("invalid JSON or duplicate object key") from None
    if not isinstance(record, dict):
        raise ValueError("each record must be a JSON object")
    event_type = record.get("event_type")
    if not isinstance(event_type, str) or event_type not in _EVENT_TYPES:
        raise ValueError("event_type must be sign_in_failure or sign_in_success")
    return SignInEvent(
        event_id=_identifier(record, "event_id"),
        timestamp=_timestamp(record.get("timestamp")),
        asset_id=_identifier(record, "asset_id"),
        account_id=_identifier(record, "account_id"),
        event_type=event_type,
    )


def _invalid_constant(value: str) -> None:
    raise ValueError(f"{value} is not a JSON constant")


def replay(lines: Iterable[str]) -> dict[str, object]:
    candidates: dict[str, list[tuple[int, SignInEvent]]] = defaultdict(list)
    rejected: list[tuple[int, str]] = []
    for line_no, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            event = _event(line)
        except ValueError as error:
            rejected.append((line_no, str(error)))
        else:
            candidates[event.event_id].append((line_no, event))

    accepted: list[SignInEvent] = []
    duplicates = 0
    for records in candidates.values():
        first = records[0][1]
        if any(event != first for _, event in records):
            rejected.extend((line, "event_id identifies conflicting records") for line, _ in records)
        else:
            accepted.append(first)
            duplicates += len(records) - 1

    return {
        "accepted_events": len(accepted),
        "duplicate_events": duplicates,
        "rejected_records": [{"line": line, "reason": reason} for line, reason in sorted(rejected)],
        "cases": [{**asdict(case), "event_ids": list(case.event_ids)} for case in detect(accepted)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a synthetic sign-in JSONL file and print review cases.")
    parser.add_argument("input", type=Path, help="UTF-8 JSON Lines fixture")
    args = parser.parse_args()
    try:
        with args.input.open(encoding="utf-8") as stream:
            result = replay(stream)
    except (OSError, UnicodeError) as error:
        parser.exit(1, f"Could not read fixture: {error}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

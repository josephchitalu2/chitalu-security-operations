"""Correlate normalized sign-in events into review cases."""

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256
import json
from typing import Iterable


RULE_ID = "repeated-sign-in-failures-v1"
THRESHOLD = 3
WINDOW = timedelta(minutes=5)


@dataclass(frozen=True)
class SignInEvent:
    event_id: str
    timestamp: datetime
    asset_id: str
    account_id: str
    event_type: str


@dataclass(frozen=True)
class ReviewCase:
    case_id: str
    rule_id: str
    asset_id: str
    account_id: str
    first_failure_utc: str
    threshold_reached_utc: str
    event_ids: tuple[str, ...]


def utc_string(timestamp: datetime) -> str:
    return timestamp.isoformat().replace("+00:00", "Z")


def _case(events: deque[SignInEvent]) -> ReviewCase:
    first, last = events[0], events[-1]
    ids = tuple(event.event_id for event in events)
    material = json.dumps([RULE_ID, last.asset_id, last.account_id, ids], separators=(",", ":"))
    return ReviewCase(
        case_id="case-" + sha256(material.encode("utf-8")).hexdigest()[:24],
        rule_id=RULE_ID,
        asset_id=last.asset_id,
        account_id=last.account_id,
        first_failure_utc=utc_string(first.timestamp),
        threshold_reached_utc=utc_string(last.timestamp),
        event_ids=ids,
    )


def detect(events: Iterable[SignInEvent]) -> list[ReviewCase]:
    """Use validated, deduplicated events and preserve the first matching window."""
    failures: dict[tuple[str, str], list[SignInEvent]] = defaultdict(list)
    for event in events:
        if event.event_type == "sign_in_failure":
            failures[event.asset_id, event.account_id].append(event)

    matches: list[tuple[datetime, ReviewCase]] = []
    for group in failures.values():
        recent: deque[SignInEvent] = deque(maxlen=THRESHOLD)
        was_matching = False
        for event in sorted(group, key=lambda item: (item.timestamp, item.event_id)):
            recent.append(event)
            matching = len(recent) == THRESHOLD and event.timestamp - recent[0].timestamp <= WINDOW
            if matching and not was_matching:
                matches.append((event.timestamp, _case(recent)))
            was_matching = matching

    return [case for _, case in sorted(matches, key=lambda item: (item[0], item[1].case_id))]

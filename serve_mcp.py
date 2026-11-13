"""Serve the Security Operations sign-in replay over local MCP stdio."""

import os
from pathlib import Path
from typing import Annotated

from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from secops.detection import ReviewCase
from secops.replay import replay


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "sign_in_demo.jsonl"
MAX_BYTES = 32_768
MAX_ROWS = 100


class RejectedRecord(BaseModel):
    line: int
    reason: str


class ReplayReport(BaseModel):
    accepted_events: int
    duplicate_events: int
    rejected_records: list[RejectedRecord]
    cases: list[ReviewCase]


def create_server():
    # The SDK reads these settings on import. This demo needs neither telemetry nor .env files.
    os.environ["MCP_USE_ANONYMIZED_TELEMETRY"] = "false"
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    from mcp_use.server import MCPServer

    server = MCPServer(
        name="chitalu-secops",
        version="0.1.0",
        instructions=(
            "Replay fictional sign-in events for the Chitalu Security Operations lab. "
            "Cases are evidence for review, not a finding of compromise. "
            "Use replay_sign_in_demo for a ready-made example; never send real credentials or logs."
        ),
    )
    read_only = ToolAnnotations(
        readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False,
    )

    @server.tool(annotations=read_only, structured_output=True)
    def replay_sign_in_demo() -> ReplayReport:
        """Replay the bundled fictional fixture and return cases with their source event IDs."""
        with FIXTURE.open(encoding="utf-8") as stream:
            return ReplayReport.model_validate(replay(stream))

    @server.tool(annotations=read_only, structured_output=True)
    def replay_synthetic_sign_ins(
        events_jsonl: Annotated[str, Field(
            min_length=1,
            max_length=MAX_BYTES,
            description=(
                "One fictional JSON event per line. Each event has event_id, timestamp with "
                "a UTC offset, asset_id, account_id, and event_type "
                "(sign_in_failure or sign_in_success). Maximum 100 lines and 32 KiB."
            ),
        )],
    ) -> ReplayReport:
        """Review a small synthetic replay supplied as text. Never reads caller-supplied files."""
        try:
            byte_count = len(events_jsonl.encode("utf-8"))
        except UnicodeEncodeError:
            raise ValueError("Send valid UTF-8 text") from None
        if byte_count > MAX_BYTES:
            raise ValueError("Send at most 32 KiB of synthetic JSON Lines")
        lines = events_jsonl.split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        if len(lines) > MAX_ROWS:
            raise ValueError("Send at most 100 lines of synthetic events")
        return ReplayReport.model_validate(replay(lines))

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")

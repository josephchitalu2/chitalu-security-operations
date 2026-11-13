"""Exercise the optional MCP transport with an actual client subprocess."""

import asyncio
import json
from pathlib import Path
import sys
import unittest

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ModuleNotFoundError as exc:
    if exc.name != "mcp":
        raise
    raise unittest.SkipTest("Install requirements-mcp.txt to run the MCP checks") from exc

from secops.replay import replay


ROOT = Path(__file__).resolve().parents[1]


class MCPServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_tools_return_evidence_and_reject_file_paths_and_large_inputs(self):
        # Run outside the repository to verify that absolute paths work in Codex.
        launch = StdioServerParameters(
            command=sys.executable,
            args=[str(ROOT / "serve_mcp.py")],
            cwd=str(ROOT.parent),
        )
        async with asyncio.timeout(20):
            async with stdio_client(launch) as (reader, writer), ClientSession(reader, writer) as client:
                initialized = await client.initialize()
                self.assertEqual(initialized.serverInfo.name, "chitalu-secops")
                tools = {tool.name: tool for tool in (await client.list_tools()).tools}
                self.assertEqual(set(tools), {"replay_sign_in_demo", "replay_synthetic_sign_ins"})
                for tool in tools.values():
                    self.assertTrue(tool.annotations.readOnlyHint)
                    self.assertFalse(tool.annotations.openWorldHint)

                with (ROOT / "fixtures" / "sign_in_demo.jsonl").open(encoding="utf-8") as fixture:
                    source = fixture.read()
                expected = replay(source.splitlines())
                demo = await client.call_tool("replay_sign_in_demo", {})
                self.assertFalse(demo.isError)
                self.assertEqual(demo.structuredContent, expected)
                self.assertEqual(expected["cases"][0]["event_ids"], ["demo-01", "demo-02", "demo-03"])

                custom = await client.call_tool("replay_synthetic_sign_ins", {"events_jsonl": source})
                self.assertFalse(custom.isError)
                self.assertEqual(custom.structuredContent, expected)

                file_arg = await client.call_tool("replay_synthetic_sign_ins", {"path": "/etc/passwd"})
                self.assertTrue(file_arg.isError)
                as_text = await client.call_tool("replay_synthetic_sign_ins", {"events_jsonl": "/etc/passwd"})
                self.assertFalse(as_text.isError)
                self.assertEqual(as_text.structuredContent["accepted_events"], 0)
                self.assertEqual(as_text.structuredContent["cases"], [])
                self.assertNotIn("/etc/passwd", json.dumps(as_text.structuredContent))

                for value in ("{}\n" * 101, "é" * 16_385, "x" * 32_769):
                    too_large = await client.call_tool("replay_synthetic_sign_ins", {"events_jsonl": value})
                    self.assertTrue(too_large.isError)

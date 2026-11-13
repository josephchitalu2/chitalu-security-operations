# Local Security Operations MCP server

Codex can ask the sign-in detector for review cases through Model Context
Protocol (MCP). This server uses the Python [mcp-use framework](https://manufact.com/mcp-use)
and reuses the same [replay rules](FIRST_DETECTION.md) as the CLI.

## Install and connect

Use Python 3.11 or later and the [Codex CLI](https://learn.chatgpt.com/docs/cli).
Run these commands from the repository root:

```bash
python3 -m venv .venv-mcp &&
.venv-mcp/bin/python -m pip install --only-binary=:all: -r requirements-mcp.txt &&
codex mcp add chitalu-secops -- "$PWD/.venv-mcp/bin/python" "$PWD/serve_mcp.py" &&
codex mcp get chitalu-secops
```

Start a new `codex` session and type `/mcp` to check that `chitalu-secops`
is listed. Try: “Use the chitalu-secops MCP tool to replay the demo and show
the three event IDs behind the case.” Expect one case with `demo-01`,
`demo-02` and `demo-03`, one duplicate and one rejected record.
Codex starts the server for you. Its configuration points to absolute paths,
so register it again if you move this checkout. To remove the registration,
run `codex mcp remove chitalu-secops`.

## What the tools can access

| Tool | Input | Result |
| --- | --- | --- |
| `replay_sign_in_demo` | None; it reads the bundled fictional fixture. | Review cases and counts for accepted, duplicate and rejected records. |
| `replay_synthetic_sign_ins` | Fictional event records as JSON Lines text, up to 100 lines and 32 KiB. | The same report for the supplied events. |

The tools do not read arbitrary paths or run response actions. The server
uses local stdio, opens no network port, disables SDK telemetry, and needs no
MCP API key or hosting account. Use fictional events: inputs and outputs can
still enter your AI client's session. Run [the tests](TESTING.md) to verify the
integration.

[Manufact Cloud](https://docs.manufact.com/) is a separate hosting option.
Use the local demo to verify the tools before adapting them to an authenticated
remote transport. The [Manufact Cloud MCP server](https://docs.manufact.com/mcp)
is for managing that hosting account and does not run this detector.

# Verification

Requires Python 3.10+; no third-party dependencies for these checks. Run from the repository root:

```bash
python3 scripts/check_docs.py
python3 -m unittest discover -s tests -p test_replay.py -v
python3 -m secops.replay fixtures/sign_in_demo.jsonl
```

The docs checker verifies relative Markdown links. The replay tests cover
time zones and event order, duplicates, conflicting IDs, account and asset
grouping, the five-minute boundary, malformed records, repeatable output and
evidence traceability. The [first detection exercise](FIRST_DETECTION.md)
explains how to read the sample result.

The optional [MCP server](MCP.md) requires Python 3.11 or later. After installing
`requirements-mcp.txt` in a virtual environment, run:

```bash
.venv-mcp/bin/python -m unittest discover -s tests -v
```

The transport test starts the server in a separate process, discovers both
tools, compares their results with the CLI replay, and checks the input limits
and rejection of file path arguments. GitHub Actions runs these checks on
pull requests and pushes to `main`. They use synthetic data.

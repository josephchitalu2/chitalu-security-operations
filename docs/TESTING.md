# Verification

Requires Python 3.10+; no third-party dependencies for these checks. Run from the repository root:

```bash
python3 scripts/check_docs.py
```

The checker verifies relative Markdown links. No sensors, detection rules or response actions have been implemented here. The [first detection exercise](FIRST_DETECTION.md) defines the positive and negative cases for a synthetic event replay.

GitHub Actions runs the checker on pushes to `main` and on pull requests. When detection is implemented, record rule results, duplicate handling and evidence traceability separately from documentation checks.

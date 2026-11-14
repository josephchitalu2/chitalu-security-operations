# Verification

Requires Python 3.10+; no third-party dependencies for these checks. Run from the repository root:

```bash
python3 scripts/check_docs.py
python3 -m unittest discover -s tests -v
python3 -m secops.replay fixtures/sign_in_demo.jsonl
```

The docs checker verifies relative Markdown links. The replay tests cover
time zones and event order, duplicates, conflicting IDs, account and asset
grouping, the five-minute boundary, malformed records, repeatable output and
evidence traceability. The [first detection exercise](FIRST_DETECTION.md)
explains how to read the sample result.

GitHub Actions runs the link checker and the replay tests on pushes to `main`
and on pull requests. The suite uses synthetic data and does not validate live
sensor collection or response.

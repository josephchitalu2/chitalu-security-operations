# Verification

Requires Python 3.10+; no third-party dependencies for these checks. Run from the repository root:

```bash
python3 scripts/check_docs.py
```

This repository currently contains a design baseline. The documentation checker is not an application test; there are no implemented business endpoints or deployed security sensors to verify yet.

GitHub Actions runs the available checks on pushes and pull requests. Record actual browser, environment, service-integration and recovery tests when those features exist. Do not interpret passing link checks as production or security verification.

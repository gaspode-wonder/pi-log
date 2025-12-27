# pi‑log Application Validation Procedure

This document defines the **authoritative procedure** for validating pi‑log application behavior locally and in CI. Its purpose is to ensure that all changes are reproducible, reviewable, and safe before deployment or downstream consumption.
---
## Goals
- Ensure application behavior is deterministic and reproducible
- Eliminate environment‑specific assumptions
- Align local development with CI execution
- Provide a clear, repeatable validation checklist for maintainers
- Establish CI as an automated mirror of trusted local behavior
---
## Local Validation Procedure (Authoritative)
This procedure **must be completed locally** before relying on CI results or merging changes.
1. Confirm Branch and Working Tree
```bash
git status
```
Expected:
- On the intended feature or integration branch
- Working tree clean
This ensures the validation reflects committed code only.
---
2. Activate the Virtual Environment
```bash
source .venv/bin/activate
```
Confirm:
```bash
which python
```
Expected:
- Python executable resolves inside `.venv`
This guarantees dependency isolation and prevents system‑level leakage.
---
3. Install Dependencies (CI‑Parity Step)
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
This mirrors the CI environment exactly and ensures no undeclared dependencies exist.
---
4. Run the Full Test Suite from Repository Root
```bash
pytest
```
Expected baseline output (as of 12/27/25):
```
51 passed, 17 warnings in ~1.4s
```
This output becomes the **gold standard** for correctness.
Notes:
- Tests must be run from the repository root
- IDE runners or partial test execution are not authoritative
- Warnings are permitted but must be consistent
- Failures are not permitted
---
5. Declare Local Validation Complete
Local validation is considered complete when:
- All tests pass
- Output structure matches prior known‑good runs
- No environment‑specific behavior is observed
Only after this point should CI results be trusted.
---
## CI Automation (Enforced Mirror)
Local validation is **automated and enforced** via GitHub Actions.
### Application CI Responsibilities
The Application CI workflow performs the following steps automatically:
1. Spins up a clean Ubuntu environment
2. Checks out the repository
3. Sets up Python 3.11
4. Installs dependencies from requirements.txt
5. Executes pytest from the repository root
6. Publishes raw pytest output for inspection
This workflow intentionally mirrors the local validation procedure without abstraction, suppression, or optimization.
---
## CI Trust Contract
CI is considered trustworthy when:
- CI test results match local validation results
- Test counts and warnings are consistent
- Failures are reproducible locally
Once this contract is satisfied, CI becomes the **authoritative merge gate**.
---
## What This Procedure Explicitly Does _Not_ Cover
The following are intentionally out of scope for Phase‑1 validation:
- Coverage thresholds
- Test segmentation
- Deployment automation
- Ansible validation
- Consumer integration (LogExp)
These concerns are layered on only after application behavior is locked down.
---
## Summary
-    Local validation defines correctness
-    CI enforces correctness
-    Both run the same commands
-    Both produce observable, comparable output
-    No hidden steps, no special cases
This procedure ensures pi‑log remains a stable, reproducible producer before downstream systems depend on it.
---
## Why This Matters
This document is the **behavioral contract** between:
- Developers
- CI
- Future maintainers
- Downstream consumers
It turns “iT wOrKs On My MaCHiNe” into **documented, automated truth**.
---

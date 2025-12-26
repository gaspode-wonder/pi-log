# Advance the Roadmap — CI & Automation

## Purpose

Advance the project from locally validated development to a fully automated,
reproducible workflow where every change is verified before merge or deployment.

This phase assumes:
- Unit tests are passing
- Integration tests are passing
- Component contracts are documented
- Pre-commit hooks are stable and enforced locally

---

## Phase 1: Baseline Continuous Integration

### Objective

Ensure that every push and pull request runs the same checks developers run locally.

### Required Checks

- Pre-commit hooks
- Unit tests
- Integration tests

### CI Responsibilities

- Fail fast on formatting or lint violations
- Fail fast on test regressions
- Produce deterministic, repeatable results
- Require no manual verification before merge

### Minimal CI Workflow (GitHub Actions)

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run pre-commit
        run: pre-commit run --all-files

      - name: Run tests
        run: pytest -vv
```
## Phase 2: Test Segmentation

### Objective

Improve feedback speed and diagnostic clarity by separating test concerns into
independent CI jobs.

### Segmented Test Jobs

- Unit tests
- Integration tests

Each job should:
- Install dependencies independently
- Run only its assigned test subset
- Report results separately

### Benefits

- Faster failure detection
- Clear ownership of failures
- Parallel execution
- Reduced cognitive load during debugging

---

## Phase 3: Coverage Reporting (Optional)

### Objective

Prevent silent erosion of test coverage over time while allowing refactors to
proceed safely.

### Local Usage

Coverage should be run locally during development to identify untested paths
and guide improvements.

### CI Integration Options

- Upload coverage artifacts
- Display coverage summaries in CI output
- Enforce minimum coverage thresholds once stabilized

### Guidance

Coverage should be:
- Informational first
- Enforced only after the test suite has matured
- Used to guide improvements, not punish refactors

---

## Phase 4: Deployment Gates

### Objective

Ensure production deployments are intentional, repeatable, and safe.

### Preconditions for Deployment

- CI is fully green
- No uncommitted changes
- A version tag exists for the release

### Optional Enhancements

- Manual approval steps
- Environment-specific secrets
- Automated release notes
- Deployment audit logging

---

## Long-Term Outcomes

When this roadmap is complete:

- Developers trust CI results
- Refactors are low-risk
- Onboarding is faster
- Production incidents decrease
- Manual verification steps disappear

CI becomes a guardrail rather than a bottleneck.

---

## Summary

This roadmap advances the project from:

- Tests passing locally

to:

- Every change automatically validated

Each phase builds on the previous one and can be adopted incrementally without
disrupting active development.

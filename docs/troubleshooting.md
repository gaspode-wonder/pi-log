# pi-log Troubleshooting Guide

This document provides a comprehensive troubleshooting reference for shell behavior, pyenv initialization, interpreter discovery, and pre-commit hook failures.

---

# 1. Shell Verification

### Check active shell:
```
echo $SHELL
```

Expected:
```
/bin/zsh
```

If incorrect:
- Command Palette → Terminal: Select Default Profile → zsh
- Restart VS Code

---

# 2. pyenv Initialization

### Verify pyenv is active:
```
which python3.10
```

Expected:
```
~/.pyenv/shims/python3.10
```

If missing:
Add to `.zshrc`:
```
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Restart VS Code.

---

# 3. Virtual Environment Consistency

### Project runtime:
```
python3.9 -m venv .venv
```

### Pre-commit interpreter:
```
default_language_version:
  python: python3.10
```

---

# 4. pre-commit Hook Environment

### Rebuild hook envs:
```
pre-commit clean
pre-commit install
pre-commit run --all-files
```

### Common failure:
- pip conflict involving ansible-lint

### Fix:
- Remove all `additional_dependencies`
- Pin only via `rev:`

---

# 5. Known Failure Modes

## Failure Mode 1 — VS Code launches bash
**Symptoms:**
- `echo $SHELL` → `/bin/bash`
- pyenv not loading

**Resolution:**
- Select zsh as default profile
- Clear VS Code terminal state

---

## Failure Mode 2 — pyenv not initializing
**Symptoms:**
- `which python3.10` returns nothing

**Resolution:**
- Ensure `.zshrc` contains pyenv initialization

---

## Failure Mode 3 — ansible-lint version conflict
**Symptoms:**
- pip reports conflicting versions

**Resolution:**
- Remove `additional_dependencies`

---

# 6. Environment Parity Checklist

- [ ] VS Code uses zsh
- [ ] pyenv initializes
- [ ] python3.10 available
- [ ] pre-commit installs cleanly
- [ ] ansible-lint runs without conflict
- [ ] `.venv` uses Python 3.9
- [ ] Pi deployment unaffected

---

# 7. Diagnostic Commands

```
echo $SHELL
which python3.10
env | sort
pre-commit clean
pre-commit install
```

---

# 8. Appendix: Flowcharts and Diagrams

See:
- `docs/diagrams/sequence.md`
- `docs/diagrams/system-overview.md`

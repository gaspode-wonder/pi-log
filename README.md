# pi-log

[![CI](https://github.com/gaspode-wonder/pi-log/actions/workflows/ci.yml/badge.svg)](https://github.com/gaspode-wonder/pi-log/actions/workflows/ci.yml)
[![Release](https://github.com/gaspode-wonder/pi-log/actions/workflows/release.yml/badge.svg)](https://github.com/gaspode-wonder/pi-log/actions/workflows/release.yml)

pi-log is a Raspberry Pi–based serial ingestion service for the LogExp radiation
monitoring system. It reads CSV-formatted data from a MightyOhm Geiger Counter,
stores readings locally for durability, and forwards them to the LogExp web API.

The project emphasizes deterministic behavior, clear component boundaries,
testability, and reproducible deployment.

---

## Project Overview

This repository contains:

- A serial reader for the MightyOhm Geiger Counter
- A local SQLite database for durable storage
- A push client that forwards readings to the LogExp web API
- A systemd service for reliable, unattended operation
- Documentation and setup scripts

The Pi reads CSV-formatted lines from the Geiger counter in the following form:
```t
CPS, #####, CPM, #####, uSv/hr, ###.##, SLOW|FAST|INST
```
Each reading is stored locally and pushed to the LogExp server with retry logic.

---

## Features

- Serial ingestion from `/dev/ttyUSB0`
- CSV parsing (CPS, CPM, uSv/hr, mode)
- Local SQLite durability
- Push-first sync model with retry handling
- systemd integration
- Minimal runtime dependencies

---

## Development and CI Model

Development follows a standard Git workflow.

Changes are made directly in the repository, validated locally, and enforced
through automated testing and continuous integration. Patch-based workflows are
not used.

Continuous integration is responsible for:

- Running Python unit and integration tests
- Enforcing formatting and linting rules
- Validating behavior against documented contracts

CI is treated as a guardrail to ensure refactors and enhancements remain safe and
reviewable.

---

## Repository Structure
```tree
pi-log/
├── Makefile
├── README.md
├── geiger_pi_reader.py
├── requirements.txt
├── systemd/
│   └── geiger.service
├── scripts/
│   ├── setup.sh
│   ├── enable.sh
│   └── migrate.sh
├── db/
│   └── schema.sql
├── config/
│   └── example.env
├── tests/
│   ├── unit/
│   ├── integration/
│   └── ui/
└── docs/
    ├── architecture.md
    ├── api.md
    ├── ingestion-flow.md
    ├── troubleshooting.md
    └── deployment.md
```
---

## Installation

Run the setup script:
```bash
sudo bash scripts/setup.sh
```

This will:

- Install Python dependencies
- Create required directories
- Install the systemd service
- Enable and start the service

---

## Environment Variables

Copy `config/example.env` to `/etc/default/geiger` and adjust as needed:
```bash
GEIGER_SERIAL_PORT=/dev/ttyUSB0
GEIGER_DB_PATH=/var/lib/geiger/geiger.db
LOGEXP_BASE_URL=https://your-logexp-host
LOGEXP_API_TOKEN=CHANGE_ME
```

---

## Service Management
```bash
sudo systemctl status geiger
sudo systemctl restart geiger
sudo systemctl stop geiger
```
---

## Data Format

Each reading stored in SQLite includes:

- timestamp (ISO8601)
- cps (int)
- cpm (int)
- usv (float)
- mode (string)
- pushed (0/1)

---

## Documentation

The `docs/` directory contains architecture, operational, and troubleshooting
resources intended for future maintainers.

### Architecture
- [System Architecture](docs/architecture.md)
- [System Overview Diagram](docs/diagrams/system-overview.md)
- [Shell/pyenv/pre-commit Sequence Diagram](docs/diagrams/sequence.md)

### Development & Validation

All application changes must pass the documented local validation procedure
before relying on CI or merging.

See: [Application Validation Procedure](docs/development.md)

The same steps are enforced automatically via GitHub Actions.

### Troubleshooting
- [Troubleshooting Guide](docs/troubleshooting.md)
- Known failure modes
- Diagnostic checklists
- Environment validation steps

These documents are written to support reproducible development on macOS and
deployment on Raspberry Pi systems.

---

## Import Path Fix for Raspberry Pi 3

Raspberry Pi 3 devices running Python 3.11 require an explicit `.pth` file
inside the virtual environment to ensure the `app` package is importable
when launched under systemd.

Create the file:

    /opt/pi-log/.venv/lib/python3.11/site-packages/pi_log_path.pth

With the following content:

    /opt/pi-log

This ensures that `python -m app.ingestion_loop` works consistently under
systemd, regardless of environment propagation quirks on Pi 3 hardware.

---

## License

MIT

# pi-log

Raspberry Pi ingestion pipeline for the LogExp radiation monitoring system.

This repository contains:

- A serial reader for the MightyOhm Geiger Counter  
- A local SQLite database for durable storage  
- A push client that forwards readings to the LogExp web API  
- A systemd service for reliable operation  
- Documentation and setup scripts  

The Pi reads CSV‑formatted lines from the Geiger counter:

```
CPS, #####, CPM, #####, uSv/hr, ###.##, SLOW|FAST|INST
```

Each reading is stored locally and pushed to the LogExp server.

---

## Features

- Serial ingestion from `/dev/ttyUSB0`
- CSV parsing (CPS, CPM, uSv/hr, mode)
- Local SQLite durability
- Push‑first sync model with retry logic
- systemd integration
- Minimal dependencies

---

## Repository Structure

```
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
│   │   ├── test_parser.py
│   │   ├── test_storage.py
│   │   ├── test_push_client.py
│   │   └── test_serial_reader.py
│   ├── integration/
│   │   ├── test_parser_db.py
│   │   ├── test_db_push.py
│   │   └── test_full_pipeline.py
│   └── ui/
│       ├── test_logexp_display.py
│       └── test_cli_output.py
└── docs/
    ├── architecture.md
    ├── api.md
    └── troubleshooting.md
```

---

## Installation

Run the setup script:

```
sudo bash scripts/setup.sh
```

This will:

- Install Python dependencies  
- Create required directories  
- Install the systemd service  
- Enable and start the service  

---

## Environment Variables

Copy `config/example.env` to `/etc/default/geiger`:

```
GEIGER_SERIAL_PORT=/dev/ttyUSB0
GEIGER_DB_PATH=/var/lib/geiger/geiger.db
LOGEXP_BASE_URL=https://your-logexp-host
LOGEXP_API_TOKEN=CHANGE_ME
```

---

## Service Management

```
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

## License

MIT



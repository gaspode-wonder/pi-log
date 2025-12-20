# Architecture Overview

This document describes the ingestion architecture for the pi-log Raspberry Pi pipeline.

---

## Data Flow

```
MightyOhm Geiger Counter → Raspberry Pi → SQLite → Push API → LogExp Web App → Postgres
```

The Geiger counter outputs CSV lines:

```
CPS, #####, CPM, #####, uSv/hr, ###.##, SLOW|FAST|INST
```

The Pi parses these fields and stores them locally before pushing to the LogExp server.

---

## Components

### 1. Serial Reader
- Reads `/dev/ttyUSB0`
- Parses CSV fields
- Inserts rows into SQLite

### 2. SQLite Database
Schema:

```
id INTEGER PRIMARY KEY
timestamp TEXT
cps INTEGER
cpm INTEGER
usv REAL
mode TEXT
pushed INTEGER
```

### 3. Push Client
- Selects rows where `pushed = 0`
- Sends them to `/api/geiger/push`
- Marks rows as pushed on success

### 4. systemd Service
Ensures:
- Auto‑start on boot
- Auto‑restart on failure
- No TTY or job‑control issues

### 5. LogExp Web App
- Receives push payloads
- Inserts into Postgres
- Optional pull fallback

---

## Diagram (Mermaid)

```mermaid
flowchart LR
    GC[MightyOhm Geiger Counter\nCSV Output]
    PI[Raspberry Pi 3\nSerial Reader + SQLite\nPush Client]
    DBPi[(SQLite DB\nreadings)]
    WEB[LogExp Web App\n(Flask in Docker)]
    DBWeb[(Postgres\ngeiger_readings)]

    GC --> |CPS,CPM,uSv,MODE| PI
    PI --> |INSERT| DBPi
    PI --> |POST /api/geiger/push| WEB
    WEB --> |INSERT| DBWeb

    subgraph Raspberry Pi
        PI
        DBPi
    end

    subgraph Server
        WEB
        DBWeb
    end
```

---

## Reliability Model

- Local durability ensures no data loss during network outages  
- Push‑first model minimizes latency  
- Pull fallback ensures eventual consistency  
- systemd ensures continuous operation  

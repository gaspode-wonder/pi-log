# Release Plan — pi-log

Semantic versioning:

```
MAJOR.MINOR.PATCH
```

---

## v1.0.0 — MVP Release

### Included
- Serial reader
- CSV parser (CPS, CPM, uSv/hr, mode)
- SQLite storage
- Push client
- systemd service
- Basic documentation
- Architecture diagram

### Requirements
- LogExp server must expose `/api/geiger/push`

---

## v1.1.0 — Pull Fallback

### Additions
- Optional Pi HTTP server exposing `/api/readings`
- LogExp pull‑fallback logic
- Health endpoint on Pi

---

## v1.2.0 — Monitoring & Metrics

### Additions
- Pi health dashboard in LogExp
- Queue depth reporting
- Push latency metrics

---

## v2.0.0 — Optional Postgres on Pi

### Breaking Changes
- Replace SQLite with Postgres
- New schema migration
- Updated environment variables

---

## v3.0.0 — Multi‑Sensor Support

### Additions
- Multiple Geiger counters per Pi
- Device identification
- Multi‑stream ingestion

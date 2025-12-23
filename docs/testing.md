# Testing Strategy for `pi-log`
This document outlines the complete testing approach for the `pi-log` ingestion pipeline, including **unit tests**, **integration tests**, and **UI tests**. The strategy is designed for full Test‑Driven Development (TDD) and can be executed entirely on macOS before the Raspberry Pi is online.

---

# 1. Unit Tests
Unit tests validate isolated components with no I/O or hardware dependencies.

## 1.1. CSV Parser Tests
Test parsing of MightyOhm CSV lines:

```
CPS, #####, CPM, #####, uSv/hr, ###.##, SLOW|FAST|INST
```

### Assertions
- Correct extraction of `cps`, `cpm`, `usv`, `mode`
- Numeric conversion (int/float)
- Whitespace tolerance
- Handling malformed lines
- Handling missing fields

---

## 1.2. SQLite Storage Tests
Use a temporary SQLite database (`tempfile.NamedTemporaryFile`).

### Assertions
- Schema creation
- Insert operations
- Selecting unpushed rows
- Marking rows as pushed
- Ordering by ID
- Timestamp format

---

## 1.3. Push Client Tests (Mock HTTP)
Use `responses` or `pytest-httpserver`.

### Assertions
- Correct JSON payload
- Authorization header present
- Handling of HTTP 200, 400, 500
- Retry logic
- Backoff behavior
- Correct marking of pushed rows

---

## 1.4. Serial Reader Tests (Mock Serial Port)
Mock `serial.Serial` to avoid hardware dependency.

### Assertions
- Lines are read from the mock serial port
- Parser is invoked
- DB insert is triggered
- Timeout handling
- Handling malformed lines

---

# 2. Integration Tests
Integration tests validate multiple components working together, still without real hardware.

## 2.1. Parser + DB
Feed CSV → parser → DB insert.

### Assertions
- Parsed values match DB values
- Timestamps stored correctly

---

## 2.2. DB + Push Client
Insert rows → run push client → mock server receives payload.

### Assertions
- Correct JSON structure
- Correct number of rows pushed
- Rows marked as pushed

---

## 2.3. Serial Reader + Parser + DB
Mock serial port to emit CSV lines.

### Assertions
- Parser receives correct lines
- DB rows created
- No crashes on malformed lines

---

## 2.4. Full Pipeline (Mocked)
```
CSV → parser → SQLite → push client → mock server
```

### Assertions
- End‑to‑end correctness
- No data loss
- Correct ordering
- Correct timestamps

---

# 3. UI Tests
UI tests validate the user‑facing surfaces that depend on `pi-log`.

## 3.1. LogExp Web App UI
Test that the LogExp UI correctly displays ingested readings.

### Assertions
- CPM/uSv/hr values appear correctly
- Charts update correctly
- Missing data handled gracefully

---

## 3.2. Pi Health Dashboard (Future)
If implemented later.

### Assertions
- Queue depth displayed
- Last push time displayed
- Error states visible

---

## 3.3. CLI Output (Optional)
If `pi-log` includes a CLI mode.

### Assertions
- Human‑readable output
- Error messages
- Logging format

---

# 4. Test Directory Structure

```
pi-log/
├── geiger_pi_reader.py
├── db/
│   └── schema.sql
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
```

---

# 5. Test Execution Workflow

### Unit tests (fastest)
```
pytest tests/unit
```

### Integration tests
```
pytest tests/integration
```

### UI tests
```
pytest tests/ui
```

### Full suite (CI)
```
pytest
```

---

# 6. What Can Be Tested on macOS Today

✅ CSV parser
✅ SQLite storage
✅ Push client
✅ Serial reader (mocked)
✅ Full pipeline (mocked)
✅ LogExp UI (local server)
✅ Real serial ingestion using your macOS TTY

You can build **100% of the test suite** before the Raspberry Pi arrives.

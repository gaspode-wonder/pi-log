import pytest
from pi_log.csv_parser import parse_geiger_csv


def test_valid_csv_line():
    line = "CPS, 14, CPM, 120, uSv/hr, 0.12, SLOW"
    result = parse_geiger_csv(line)
    assert result == {
        "cps": 14,
        "cpm": 120,
        "usv": 0.12,
        "mode": "SLOW",
    }


def test_valid_modes():
    for mode in ["SLOW", "FAST", "INST"]:
        line = f"CPS, 1, CPM, 2, uSv/hr, 0.01, {mode}"
        result = parse_geiger_csv(line)
        assert result["mode"] == mode


def test_invalid_mode():
    line = "CPS, 1, CPM, 2, uSv/hr, 0.01, UNKNOWN"
    assert parse_geiger_csv(line) is None


def test_malformed_line_missing_fields():
    line = "CPS, 14, CPM, 120"
    assert parse_geiger_csv(line) is None


def test_non_numeric_values():
    line = "CPS, X, CPM, Y, uSv/hr, Z, SLOW"
    assert parse_geiger_csv(line) is None


def test_extra_whitespace():
    line = "  CPS ,   14 , CPM , 120 , uSv/hr , 0.12 , SLOW   "
    result = parse_geiger_csv(line)
    assert result["cps"] == 14
    assert result["cpm"] == 120
    assert result["usv"] == 0.12
    assert result["mode"] == "SLOW"


def test_non_string_input():
    assert parse_geiger_csv(None) is None
    assert parse_geiger_csv(123) is None

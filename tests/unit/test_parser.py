import pytest

from app.csv_parser import parse_geiger_csv


def test_parse_valid_line():
    line = "CPS, 9, CPM, 90, uSv/hr, 0.09, FAST"
    result = parse_geiger_csv(line)
    assert result is not None
    assert result["cps"] == 9
    assert result["cpm"] == 90
    assert result["usv"] == 0.09
    assert result["mode"] == "FAST"
    assert result["raw"] == line


@pytest.mark.parametrize("bad_input", [None, 123, "", "   "])
def test_non_string_or_empty_input_returns_none(bad_input):
    assert parse_geiger_csv(bad_input) is None


def test_malformed_line_returns_none():
    line = "not,a,valid,csv"
    assert parse_geiger_csv(line) is None


def test_partial_line_returns_none():
    line = "CPS, 9, CPM, 90"
    assert parse_geiger_csv(line) is None

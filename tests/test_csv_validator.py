"""Unit tests for the CSV validator utility."""
import io

import pandas as pd

from app.utils.csv_validator import validate_csv


def _make_csv(**overrides) -> bytes:
    data = {
        "date": ["2023-01-01"],
        "cloud_provider": ["AWS"],
        "account_id": ["acct-001"],
        "service": ["EC2"],
        "net_cost": [100.0],
    }
    data.update(overrides)
    return pd.DataFrame(data).to_csv(index=False).encode()


def test_valid_csv():
    result = validate_csv(_make_csv(), "billing.csv")
    assert result.valid is True
    assert result.row_count == 1
    assert result.errors == []


def test_missing_required_column():
    csv_bytes = pd.DataFrame({"date": ["2023-01-01"], "cloud_provider": ["AWS"]}).to_csv(index=False).encode()
    result = validate_csv(csv_bytes, "billing.csv")
    assert result.valid is False
    assert any("Missing required columns" in e for e in result.errors)


def test_invalid_provider():
    result = validate_csv(_make_csv(cloud_provider=["Oracle"]), "billing.csv")
    assert result.valid is False
    assert any("cloud_provider" in e for e in result.errors)


def test_invalid_date():
    result = validate_csv(_make_csv(date=["not-a-date"]), "billing.csv")
    assert result.valid is False
    assert any("date" in e for e in result.errors)


def test_non_numeric_cost():
    result = validate_csv(_make_csv(net_cost=["free"]), "billing.csv")
    assert result.valid is False
    assert any("net_cost" in e for e in result.errors)


def test_wrong_extension():
    result = validate_csv(_make_csv(), "billing.xlsx")
    assert result.valid is False
    assert any(".csv" in e for e in result.errors)


def test_empty_csv():
    result = validate_csv(b"", "billing.csv")
    assert result.valid is False


def test_file_too_large():
    big = b"x" * (51 * 1024 * 1024)
    result = validate_csv(big, "billing.csv")
    assert result.valid is False
    assert any("50 MB" in e for e in result.errors)

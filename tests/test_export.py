import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from dashboard_scraper.export import flatten_record, header_order, write_csv


def test_flatten_record_simple():
    """Test flattening a simple flat record."""
    rec = {"user_id": "123", "email": "test@example.com", "value": 42}
    flat = flatten_record(rec)
    assert flat == {"user_id": "123", "email": "test@example.com", "value": 42}


def test_flatten_record_nested():
    """Test flattening nested dictionaries."""
    rec = {
        "user": {"id": "123", "email": "test@example.com"},
        "metric": "tool_usage",
        "value": 42,
    }
    flat = flatten_record(rec)
    assert flat == {
        "user.id": "123",
        "user.email": "test@example.com",
        "metric": "tool_usage",
        "value": 42,
    }


def test_flatten_record_with_list():
    """Test that lists are serialized as JSON strings."""
    rec = {"user_id": "123", "tags": ["tag1", "tag2"], "value": 42}
    flat = flatten_record(rec)
    assert flat["user_id"] == "123"
    assert flat["value"] == 42
    assert flat["tags"] == json.dumps(["tag1", "tag2"])


def test_header_order():
    """Test that priority fields come first."""
    keys = ["value", "metric", "user_id", "timestamp", "extra_field", "date"]
    ordered = header_order(keys)
    # Priority: timestamp, date, user_id, email, metric, value
    # Expected: timestamp, date, user_id, metric, value, extra_field
    assert ordered[:4] == ["timestamp", "date", "user_id", "metric"]
    assert "value" in ordered
    assert "extra_field" in ordered


def test_write_csv_basic():
    """Test writing a simple CSV."""
    rows = [
        {"timestamp": "2025-10-22T00:00:00+00:00", "user_id": "123", "value": 42},
        {"timestamp": "2025-10-22T01:00:00+00:00", "user_id": "456", "value": 17},
    ]
    with TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        out_path = write_csv(rows, out_dir, "test.csv")
        assert out_path.exists()
        with open(out_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            assert len(data) == 2
            assert data[0]["user_id"] == "123"
            assert data[0]["value"] == "42"
            assert data[1]["user_id"] == "456"


def test_write_csv_nested():
    """Test writing CSV with nested data."""
    rows = [
        {
            "timestamp": "2025-10-22T00:00:00+00:00",
            "user": {"id": "123", "email": "test@example.com"},
            "value": 42,
        }
    ]
    with TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        out_path = write_csv(rows, out_dir, "nested.csv")
        with open(out_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            assert len(data) == 1
            assert data[0]["user.id"] == "123"
            assert data[0]["user.email"] == "test@example.com"
            assert data[0]["value"] == "42"


def test_write_csv_empty():
    """Test writing an empty CSV."""
    rows = []
    with TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        out_path = write_csv(rows, out_dir, "empty.csv")
        assert out_path.exists()
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Should have no header or rows
            assert content == ""


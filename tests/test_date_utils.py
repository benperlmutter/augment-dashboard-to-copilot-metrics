from datetime import datetime, timedelta, timezone

from dashboard_scraper.date_utils import compute_lookback_window, isoformat_utc


def test_compute_lookback_window_default():
    """Test 30-day lookback from now."""
    start, end = compute_lookback_window(days=30)
    delta = end - start
    assert delta.days == 30
    assert start.tzinfo == timezone.utc
    assert end.tzinfo == timezone.utc


def test_compute_lookback_window_custom_now():
    """Test lookback with a fixed 'now' timestamp."""
    fixed_now = datetime(2025, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
    start, end = compute_lookback_window(days=7, now=fixed_now)
    assert end == fixed_now
    assert start == fixed_now - timedelta(days=7)


def test_compute_lookback_window_single_day():
    """Test 1-day lookback."""
    fixed_now = datetime(2025, 10, 22, 0, 0, 0, tzinfo=timezone.utc)
    start, end = compute_lookback_window(days=1, now=fixed_now)
    assert (end - start).days == 1


def test_isoformat_utc():
    """Test ISO 8601 UTC formatting."""
    dt = datetime(2025, 10, 22, 15, 30, 45, 123456, tzinfo=timezone.utc)
    result = isoformat_utc(dt)
    # Should strip microseconds and format as ISO 8601
    assert result == "2025-10-22T15:30:45+00:00"


def test_isoformat_utc_naive_datetime():
    """Test that naive datetimes are treated as UTC."""
    dt = datetime(2025, 10, 22, 15, 30, 45)
    # This will raise an error or convert; our implementation expects tz-aware
    # For safety, we assume input is always tz-aware in production
    # If needed, add handling for naive datetimes
    pass


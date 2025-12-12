from __future__ import annotations

from datetime import datetime, timedelta, timezone


def compute_lookback_window(days: int = 30, now: datetime | None = None) -> tuple[datetime, datetime]:
    """Return (start, end) in UTC for the past `days` days up to now.

    start is inclusive, end is exclusive (half-open interval), both UTC.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    end = now.astimezone(timezone.utc)
    start = end - timedelta(days=days)
    return (start, end)


def isoformat_utc(dt: datetime) -> str:
    """Convert datetime to UTC ISO format string.

    Args:
        dt: Datetime to convert. If naive (no timezone), assumes UTC.

    Returns:
        ISO format string in UTC timezone
    """
    if dt.tzinfo is None:
        # Assume naive datetimes are UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def compute_last_28_days(now: datetime | None = None) -> tuple[datetime, datetime]:
    """Calculate date range for last 28 days (28 days ago to yesterday).

    Excludes today to ensure complete daily data availability.

    Args:
        now: Current datetime (defaults to now in UTC)

    Returns:
        Tuple of (start_date, end_date) where:
        - start_date: 28 days ago at 00:00:00 UTC
        - end_date: yesterday at 23:59:59.999999 UTC
        Both dates are inclusive.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # Ensure we're working in UTC
    now = now.astimezone(timezone.utc)

    # Yesterday at end of day (23:59:59.999999)
    yesterday = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

    # 28 days ago from yesterday (inclusive), at start of day (00:00:00)
    start = (yesterday - timedelta(days=27)).replace(hour=0, minute=0, second=0, microsecond=0)

    return (start, yesterday)


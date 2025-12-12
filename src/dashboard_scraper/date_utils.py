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


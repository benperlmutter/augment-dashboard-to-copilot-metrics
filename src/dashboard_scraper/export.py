from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .date_utils import isoformat_utc

logger = logging.getLogger(__name__)


def _flatten(prefix: str, value: Any, out: Dict[str, Any]) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            _flatten(f"{prefix}.{k}" if prefix else k, v, out)
    elif isinstance(value, list):
        # represent lists as JSON strings to keep CSV shape stable
        out[prefix] = json.dumps(value, ensure_ascii=False)
    else:
        out[prefix] = value


def flatten_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    _flatten("", rec, out)
    return out


def header_order(keys: List[str]) -> List[str]:
    # Prioritize dashboard table columns in the exact order from the dashboard
    priority = [
        "User",
        "First Seen",
        "Last Seen",
        "Active Days",
        "Completions",
        "Accepted Completions",
        "Accept Rate",
        "Chat Messages",
        "Agent Messages",
        "Remote Agent Messages",
        "Interactive CLI Agent Messages",
        "Non-Interactive CLI Agent Messages",
        "Tool Uses",
        "Total Modified Lines of Code",
        "Completion Lines of Code",
        "Instruction Lines of Code",
        "Agent Lines of Code",
        "Remote Agent Lines of Code",
        "CLI Agent Lines of Code",
        # Summary metrics
        "Metric Type",
        "Value",
        "User Messages",
        "Tool Calls",
        "Lines of Code",
    ]
    ordered = [k for k in priority if k in keys]
    rest = [k for k in keys if k not in ordered]
    return ordered + sorted(rest)


def _generate_filename(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
    """
    Generate a filename based on the date range.

    Args:
        start_date: Start of the date range
        end_date: End of the date range

    Returns:
        Filename in format: metrics_YYYYMMDD.csv or metrics_YYYYMMDD_to_YYYYMMDD.csv
    """
    if start_date is None or end_date is None:
        # Fallback to current date
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"metrics_{today}.csv"

    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    # If same day, use single date format
    if start_str == end_str:
        return f"metrics_{start_str}.csv"

    # Otherwise use range format
    return f"metrics_{start_str}_to_{end_str}.csv"


def write_csv(
    rows: Iterable[Dict[str, Any]],
    out_dir: Path,
    filename: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Path:
    flat_rows: List[Dict[str, Any]] = []
    for r in rows:
        # Check if the record is already formatted (has "User" or "Metric Type" keys)
        # If so, don't flatten it
        if "User" in r or "Metric Type" in r:
            flat_rows.append(r)
        else:
            # Flatten nested structures for other data
            fr = flatten_record(r)
            # try normalize timestamp fields if present
            for ts_key in ("timestamp", "date"):
                if ts_key in fr and isinstance(fr[ts_key], (int, float)):
                    fr[ts_key] = isoformat_utc(datetime.utcfromtimestamp(fr[ts_key]).replace(tzinfo=None))
            flat_rows.append(fr)

    # Handle empty data case
    if not flat_rows:
        logger.warning("No data to export")
        out_dir.mkdir(parents=True, exist_ok=True)
        if not filename:
            filename = _generate_filename(start_date, end_date)
        out_path = out_dir / filename
        # Create empty file
        out_path.touch()
        return out_path

    # union of keys
    keys: List[str] = []
    for r in flat_rows:
        for k in r.keys():
            if k not in keys:
                keys.append(k)
    cols = header_order(keys)

    out_dir.mkdir(parents=True, exist_ok=True)
    if not filename:
        filename = _generate_filename(start_date, end_date)
    out_path = out_dir / filename

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in flat_rows:
            w.writerow(r)
    return out_path


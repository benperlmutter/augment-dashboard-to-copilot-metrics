from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Iterator

from .client import DashboardClient
from .config import Settings
from .export import write_csv

logger = logging.getLogger(__name__)


def _generate_date_range(start: datetime, end: datetime) -> List[datetime]:
    """
    Generate list of dates from start to end (inclusive).

    Args:
        start: Start date
        end: End date

    Returns:
        List of datetime objects, one for each day
    """
    dates = []
    # Preserve timezone while normalizing to start of day
    current = start.replace(hour=0, minute=0, second=0, microsecond=0)
    if current.tzinfo is None and start.tzinfo is not None:
        current = current.replace(tzinfo=start.tzinfo)

    end_date = end.replace(hour=0, minute=0, second=0, microsecond=0)
    if end_date.tzinfo is None and end.tzinfo is not None:
        end_date = end_date.replace(tzinfo=end.tzinfo)

    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)

    return dates


def _create_daily_export_dir(export_dir: Path, start: datetime, end: datetime) -> Path:
    """
    Create directory for daily CSV exports.

    Args:
        export_dir: Base export directory
        start: Start date
        end: End date

    Returns:
        Path to the daily exports directory
    """
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    daily_dir = export_dir / f"daily_exports_{start_str}_to_{end_str}"
    daily_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Created daily export directory: %s", daily_dir)
    return daily_dir


def _fetch_single_day_metrics(
    client: DashboardClient,
    date: datetime,
    day_num: int,
    total_days: int
) -> List[Dict[str, Any]] | None:
    """
    Fetch metrics for a single day.

    CRITICAL: This function tests the API parameter format to determine
    if we need to use same-day or next-day for endDate.

    API Parameter Format Testing:
    - Option 1: startDate=2024-11-14, endDate=2024-11-14 (same day)
    - Option 2: startDate=2024-11-14, endDate=2024-11-15 (next day)

    Based on testing with existing code, the API appears to use inclusive
    date ranges, so we'll start with Option 1 (same day for both).

    Args:
        client: DashboardClient instance
        date: The date to fetch metrics for
        day_num: Current day number (for progress logging)
        total_days: Total number of days being processed

    Returns:
        List of metric records for this day, or None if an error occurred.
        An empty list indicates a successful fetch with zero records.
    """
    # Start of day (00:00:00)
    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)

    # End of day (23:59:59.999999)
    day_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

    logger.info("Processing day %d of %d: %s", day_num, total_days, date.date())
    print(f"📅 Processing day {day_num} of {total_days}: {date.date()}")

    try:
        # Fetch metrics for this single day
        # The API uses inclusive date ranges, so we use the same day for both start and end
        records = list(client.iter_metrics(day_start, day_end))

        logger.info("Fetched %d records for %s", len(records), date.date())
        print(f"   ✅ Fetched {len(records)} records")

        return records

    except Exception as e:
        logger.error("Failed to fetch metrics for %s: %s", date.date(), e)
        print(f"   ❌ Error: {e}")
        return None



def _write_daily_csv(
    records: List[Dict[str, Any]],
    daily_dir: Path,
    date: datetime
) -> Path:
    """
    Write daily metrics to a CSV file.

    Args:
        records: List of metric records for the day
        daily_dir: Directory to write CSV files to
        date: The date for this data

    Returns:
        Path to the written CSV file
    """
    date_str = date.strftime("%Y-%m-%d")
    filename = f"augment_metrics_{date_str}.csv"

    # Use the existing write_csv function
    csv_path = write_csv(
        records,
        daily_dir,
        filename=filename,
        start_date=date,
        end_date=date
    )

    logger.info("Wrote daily CSV: %s", csv_path)
    print(f"   📄 Wrote CSV: {csv_path.name}")

    return csv_path


def process_last_28_days(
    client: DashboardClient,
    settings: Settings,
    start: datetime,
    end: datetime
) -> None:
    """
    Process metrics for the last 28 days and generate Copilot-compatible output.
<<<<<<< HEAD

=======
    
>>>>>>> origin/main
    This function:
    1. Fetches daily metrics for each of the 28 days
    2. Generates individual CSV files for each day
    3. Creates a consolidated JSON file in Copilot's per-user format
<<<<<<< HEAD

=======
    
>>>>>>> origin/main
    Args:
        client: DashboardClient instance for API calls
        settings: Settings instance for configuration
        start: Start date (28 days ago at 00:00:00)
        end: End date (yesterday at 23:59:59)
    """
    logger.info("Starting 28-day metrics processing")
    logger.info("Date range: %s to %s", start.date(), end.date())
<<<<<<< HEAD

    print("\n" + "=" * 80)
    print("🚀 Starting 28-day metrics processing")
    print("=" * 80)
    print(f"Date range: {start.date()} to {end.date()}")
    print()

    # Generate list of dates to process
    dates = _generate_date_range(start, end)
    total_days = len(dates)

    logger.info("Processing %d days", total_days)
    print(f"Total days to process: {total_days}")
    print()

    # Create output directory for daily CSV files
    daily_dir = _create_daily_export_dir(settings.export_dir_path(), start, end)
    print(f"Output directory: {daily_dir}")
    print()

    # Track results
    daily_data: Dict[str, List[Dict[str, Any]]] = {}
    csv_files: List[Path] = []
    successful_days = 0
    failed_days = 0

    # Fetch metrics for each day and write CSV files
    for i, date in enumerate(dates, 1):
        records = _fetch_single_day_metrics(client, date, i, total_days)

        if records is not None:
            # Successfully fetched (may be empty list if no data for this day)
            date_key = date.strftime("%Y-%m-%d")
            daily_data[date_key] = records

            # Write daily CSV file
            csv_path = _write_daily_csv(records, daily_dir, date)
            csv_files.append(csv_path)

            successful_days += 1
        else:
            # Error occurred during fetch
            failed_days += 1

    # Summary
    print()
    print("=" * 80)
    print("📊 Processing Summary")
    print("=" * 80)
    print(f"Total days processed: {total_days}")
    print(f"Successful: {successful_days}")
    print(f"Failed: {failed_days}")
    print(f"CSV files generated: {len(csv_files)}")
    print()

    if successful_days == 0:
        logger.error("No data fetched for any day")
        print("❌ No data fetched. Please check your authentication and try again.")
        return

    # List generated CSV files
    print("Generated CSV files:")
    for csv_file in csv_files:
        print(f"  - {csv_file}")
    print()

    # TODO: Milestone 4 - Generate Copilot JSON

    logger.info("28-day processing complete: %d successful, %d failed", successful_days, failed_days)
    print("✅ Daily CSV files generated successfully!")
    print(f"📁 Output directory: {daily_dir}")
    print()
    print("⚠️  Copilot JSON generation will be implemented in Milestone 4")


from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone

from .client import DashboardClient
from .config import load_settings
from .cookie_auth import CookieAuth, interactive_cookie_setup
from .date_utils import compute_lookback_window
from .export import write_csv
from .http import HTTPClient, AuthenticationExpiredError
from .logging_config import setup_logging


def parse_date(date_str: str) -> datetime:
    """
    Parse date string in MM-DD-YYYY format to datetime at start of day (00:00:00 UTC).

    Args:
        date_str: Date in MM-DD-YYYY format (e.g., "10-20-2025")

    Returns:
        Datetime at start of day in UTC
    """
    try:
        dt = datetime.strptime(date_str, "%m-%d-%Y")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected MM-DD-YYYY (e.g., 10-20-2025)")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Dashboard metrics scraper with cookie-based authentication",
        epilog="""
Examples:
  # Default: last 30 days
  python -m dashboard_scraper

  # Single date: metrics for that 24-hour period (or up to now if today)
  python -m dashboard_scraper 10-22-2025

  # Date range: metrics from start date 00:00 to end date 23:59:59
  python -m dashboard_scraper 10-20-2025 10-21-2025

Authentication:
  # Manual cookie setup (interactive)
  python -m dashboard_scraper --auth
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("dates", nargs="*", help="Date(s) in MM-DD-YYYY format. One date = single day, two dates = range")
    p.add_argument("--out", help="Output filename (CSV)")
    p.add_argument("--auth", action="store_true", help="Set up cookie-based authentication (interactive)")
    p.add_argument("--log-level", default=None, help="Override log level (INFO/DEBUG/...)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    s = load_settings()
    setup_logging(args.log_level or s.log_level)

    logger = logging.getLogger(__name__)

    # Handle manual authentication setup
    if args.auth:
        logger.info("Setting up cookie-based authentication")
        interactive_cookie_setup(s.cookie_file_path())
        return

    # Set up HTTP client with cookie authentication
    logger.info("Using cookie-based authentication")
    cookie_auth = CookieAuth(s.cookie_file_path())
    if not cookie_auth.has_cookies():
        logger.error("No cookies found. Run with --auth to set up cookies.")
        print("❌ No cookies found.")
        print("\nTo authenticate, run:")
        print("  python -m dashboard_scraper --auth")
        return

    http = HTTPClient(s, cookie_auth=cookie_auth)

    client = DashboardClient(s, http)

    # Parse date arguments and fetch metrics
    try:
        if args.dates:
            if len(args.dates) == 1:
                # Single date: get metrics for that 24-hour period (or up to now if today)
                start = parse_date(args.dates[0])
                now = datetime.now(timezone.utc)

                # End of day is 23:59:59.999999
                end_of_day = start.replace(hour=23, minute=59, second=59, microsecond=999999)

                # If the date is today, use current time instead of end of day
                if start.date() == now.date():
                    end = now
                    logger.info("Fetching metrics for today (%s) up to now", start.date())
                else:
                    end = end_of_day
                    logger.info("Fetching metrics for %s (full 24-hour period)", start.date())

            elif len(args.dates) == 2:
                # Date range: from start date 00:00:00 to end date 23:59:59
                start = parse_date(args.dates[0])
                end_date = parse_date(args.dates[1])
                end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                logger.info("Fetching metrics from %s to %s", start.date(), end.date())
            else:
                logger.error("Too many date arguments. Expected 0, 1, or 2 dates.")
                print("❌ Error: Provide either 0 dates (default 30 days), 1 date (single day), or 2 dates (range)")
                print("   Format: MM-DD-YYYY (e.g., 10-20-2025)")
                return
        else:
            # Default: use lookback window from config
            start, end = compute_lookback_window(s.lookback_days)
            logger.info("Fetching metrics for last %d days", s.lookback_days)

        logger.info("Date range: %s to %s", start, end)

        rows = client.iter_metrics(start, end)
        out_path = write_csv(rows, s.export_dir_path(), args.out, start_date=start, end_date=end)
        print(f"✅ Metrics exported to: {out_path}")

    except AuthenticationExpiredError as e:
        logger.error("Authentication failed: %s", e)
        print(f"\n❌ {e}")
        print("\nPlease re-authenticate:")
        print("  python -m dashboard_scraper --auth")
        sys.exit(1)
    except Exception as e:
        logger.error("Error during scraping: %s", e, exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


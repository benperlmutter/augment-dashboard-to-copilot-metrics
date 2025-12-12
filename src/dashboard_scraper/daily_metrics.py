from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from .client import DashboardClient
from .config import Settings

logger = logging.getLogger(__name__)


def process_last_28_days(
    client: DashboardClient,
    settings: Settings,
    start: datetime,
    end: datetime
) -> None:
    """
    Process metrics for the last 28 days and generate Copilot-compatible output.
    
    This function:
    1. Fetches daily metrics for each of the 28 days
    2. Generates individual CSV files for each day
    3. Creates a consolidated JSON file in Copilot's per-user format
    
    Args:
        client: DashboardClient instance for API calls
        settings: Settings instance for configuration
        start: Start date (28 days ago at 00:00:00)
        end: End date (yesterday at 23:59:59)
    """
    logger.info("Starting 28-day metrics processing")
    logger.info("Date range: %s to %s", start.date(), end.date())
    
    # TODO: Implement daily metrics processing
    # This will be implemented in Milestone 2
    print("⚠️  --last-28-days feature is under development")
    print(f"   Would process: {start.date()} to {end.date()}")


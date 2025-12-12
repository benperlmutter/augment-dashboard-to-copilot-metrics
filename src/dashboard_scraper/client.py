from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Iterator, List
from urllib.parse import quote
import json

from .config import Settings
from .http import HTTPClient

logger = logging.getLogger(__name__)


class DashboardClient:
    def __init__(self, settings: Settings, http: HTTPClient) -> None:
        self.s = settings
        self.http = http

    def _format_date_param(self, dt: datetime) -> str:
        """
        Format datetime as URL-encoded JSON for the API.
        API expects: {"year":2025,"month":10,"day":22} (no spaces)
        """
        date_obj = {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day
        }
        # Use separators to remove spaces from JSON
        return quote(json.dumps(date_obj, separators=(',', ':')))

    def _build_url(self, endpoint: str, start: datetime, end: datetime) -> str:
        """Build the full URL with date parameters."""
        base_url = self.s.metrics_api_base_url
        start_param = self._format_date_param(start)
        end_param = self._format_date_param(end)
        return f"{base_url}{endpoint}?startDate={start_param}&endDate={end_param}"

    def fetch_endpoint(self, endpoint: str, start: datetime, end: datetime) -> Dict[str, Any]:
        """
        Fetch data from a specific endpoint.

        Args:
            endpoint: The API endpoint path (e.g., "/api/user-feature-stats")
            start: Start date
            end: End date

        Returns:
            The JSON response from the API
        """
        url = self._build_url(endpoint, start, end)
        logger.info("Fetching %s", url)
        resp = self.http.request("GET", url)
        data = resp.json()
        logger.info("Fetched data from %s", endpoint)
        return data

    def _format_user_stats(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format user stats record to match dashboard table format.
        """
        # Extract date from ISO timestamp (e.g., "2024-08-14T21:07:24.808438Z" -> "2024-08-14")
        first_seen = record.get("firstSeen", "")
        last_seen = record.get("lastSeen", "")

        if first_seen:
            first_seen = first_seen.split("T")[0]
        if last_seen:
            last_seen = last_seen.split("T")[0]

        # Handle accept rate with defensive None check
        acceptance_rate = record.get("acceptanceRatePercentage", 0)
        if acceptance_rate is None:
            acceptance_rate = 0

        return {
            "User": record.get("userEmail", ""),
            "First Seen": first_seen,
            "Last Seen": last_seen,
            "Active Days": record.get("totalActiveDays", 0),
            "Completions": record.get("totalCompletionsInTimePeriod", 0),
            "Accepted Completions": record.get("acceptedCompletionsInTimePeriod", 0),
            "Accept Rate": f"{acceptance_rate:.2f}%",
            "Chat Messages": record.get("totalChatMessagesInTimePeriod", 0),
            "Agent Messages": record.get("totalAgentChatMessagesInTimePeriod", 0),
            "Remote Agent Messages": record.get("totalRemoteAgentMessagesInTimePeriod", 0),
            "Interactive CLI Agent Messages": record.get("totalInteractiveCliAgentMessagesInTimePeriod", 0),
            "Non-Interactive CLI Agent Messages": record.get("totalNoninteractiveCliAgentMessagesInTimePeriod", 0),
            "Tool Uses": record.get("totalToolUsesInTimePeriod", 0),
            "Total Modified Lines of Code": record.get("totalModifiedLinesOfCode", 0),
            "Completion Lines of Code": record.get("completionLinesOfCode", 0),
            "Instruction Lines of Code": record.get("instructionLinesOfCode", 0),
            "Agent Lines of Code": record.get("agentLinesOfCode", 0),
            "Remote Agent Lines of Code": record.get("remoteAgentLinesOfCode", 0),
            "CLI Agent Lines of Code": record.get("cliAgentLinesOfCode", 0),
        }

    def iter_metrics(self, start: datetime, end: datetime) -> Iterator[Dict[str, Any]]:
        """
        Fetch metrics from all configured endpoints.
        Yields records formatted for CSV export.

        Args:
            start: Start date
            end: End date

        Yields:
            Individual metric records formatted for the dashboard table
        """
        endpoints = self.s.get_endpoints_to_scrape()

        for name, endpoint in endpoints:
            logger.info("Scraping %s from %s", name, endpoint)
            try:
                data = self.fetch_endpoint(endpoint, start, end)

                # Handle different response formats based on endpoint
                if name == "user_stats":
                    # User stats has userFeatureStats array
                    records = data.get("userFeatureStats", [])
                    for record in records:
                        yield self._format_user_stats(record)
                    logger.info("Fetched %d user records", len(records))

                elif name == "tenant_stats":
                    # Tenant stats is a single summary object
                    summary = {
                        "Metric Type": "Tenant Summary",
                        "User Messages": data.get("userMessages", 0),
                        "Tool Calls": data.get("toolCalls", 0),
                        "Lines of Code": data.get("linesOfCode", 0),
                    }
                    yield summary
                    logger.info("Fetched tenant summary")

                elif name == "tenant_mau":
                    # MAU is a single value
                    mau = {
                        "Metric Type": "Monthly Active Users",
                        "Value": data.get("monthlyActiveUsers", 0),
                    }
                    yield mau
                    logger.info("Fetched MAU: %d", data.get("monthlyActiveUsers", 0))

                else:
                    # Fallback for unknown endpoints
                    if isinstance(data, list):
                        records = data
                    elif isinstance(data, dict):
                        records = data.get("data", data.get("results", data.get("items", [data])))
                        if not isinstance(records, list):
                            records = [data]
                    else:
                        records = [data]

                    for record in records:
                        if isinstance(record, dict):
                            record["_source"] = name
                            record["_endpoint"] = endpoint
                        yield record
                    logger.info("Fetched %d records from %s", len(records), name)

            except Exception as e:
                logger.error("Failed to fetch %s: %s", name, e)
                # Continue with other endpoints even if one fails
                continue


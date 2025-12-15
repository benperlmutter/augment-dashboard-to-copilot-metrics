"""
Convert Augment CSV metrics to GitHub Copilot Metrics API format.

This module implements the mapping defined in CSV_TO_JSON_MAPPING.md to convert
Augment's per-user metrics into the GitHub Copilot per-user JSON format.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def generate_user_id(user_email: str) -> int:
    """
    Generate a numeric user ID from email address.
    
    Uses MD5 hash of email to create a consistent numeric ID.
    
    Args:
        user_email: User's email address
    
    Returns:
        Numeric user ID
    """
    return int(hashlib.md5(user_email.encode()).hexdigest()[:8], 16)


def convert_csv_row_to_copilot_json(
    row: Dict[str, Any],
    report_start_day: str,
    report_end_day: str,
    enterprise_id: str = "283613"
) -> Dict[str, Any]:
    """
    Convert a single CSV row to Copilot JSON format.
    
    Implements the mapping from CSV_TO_JSON_MAPPING.md.
    
    Args:
        row: Dictionary representing a CSV row
        report_start_day: Start date in YYYY-MM-DD format
        report_end_day: End date in YYYY-MM-DD format
        enterprise_id: Enterprise ID (default: "283613")
    
    Returns:
        Dictionary in Copilot per-user JSON format
    """
    user_email = row.get("User", "")
    
    # Parse numeric values, defaulting to 0 if missing or invalid
    def parse_int(value: Any) -> int:
        try:
            if isinstance(value, str):
                # Remove % sign if present
                value = value.replace("%", "")
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    # Extract metrics from CSV
    completions = parse_int(row.get("Completions", 0))
    accepted_completions = parse_int(row.get("Accepted Completions", 0))
    chat_messages = parse_int(row.get("Chat Messages", 0))
    agent_messages = parse_int(row.get("Agent Messages", 0))
    remote_agent_messages = parse_int(row.get("Remote Agent Messages", 0))
    interactive_cli_agent_messages = parse_int(row.get("Interactive CLI Agent Messages", 0))
    non_interactive_cli_agent_messages = parse_int(row.get("Non-Interactive CLI Agent Messages", 0))
    
    total_modified_loc = parse_int(row.get("Total Modified Lines of Code", 0))
    completion_loc = parse_int(row.get("Completion Lines of Code", 0))
    agent_loc = parse_int(row.get("Agent Lines of Code", 0))
    remote_agent_loc = parse_int(row.get("Remote Agent Lines of Code", 0))
    cli_agent_loc = parse_int(row.get("CLI Agent Lines of Code", 0))
    
    # Calculate totals
    total_agent_messages = (
        agent_messages + 
        remote_agent_messages + 
        interactive_cli_agent_messages + 
        non_interactive_cli_agent_messages
    )
    
    total_agent_loc = agent_loc + remote_agent_loc + cli_agent_loc
    
    total_user_interactions = chat_messages + total_agent_messages
    
    # Build Copilot JSON record
    record = {
        "report_start_day": report_start_day,
        "report_end_day": report_end_day,
        "day": report_end_day,  # Use end date as reporting day
        "enterprise_id": enterprise_id,
        "user_id": generate_user_id(user_email),
        "user_login": user_email,
        
        # Activity counts
        "user_initiated_interaction_count": total_user_interactions,
        "code_generation_activity_count": completions,
        "code_acceptance_activity_count": accepted_completions,
        
        # Feature breakdown
        "totals_by_feature": [
            {
                "feature": "code_completion",
                "user_initiated_interaction_count": 0,
                "code_generation_activity_count": completions,
                "code_acceptance_activity_count": accepted_completions,
                "loc_suggested_to_add_sum": completion_loc,
                "loc_suggested_to_delete_sum": 0,
                "loc_added_sum": completion_loc,
                "loc_deleted_sum": 0
            },
            {
                "feature": "chat_panel",
                "user_initiated_interaction_count": chat_messages,
                "code_generation_activity_count": 0,
                "code_acceptance_activity_count": 0,
                "loc_suggested_to_add_sum": 0,
                "loc_suggested_to_delete_sum": 0,
                "loc_added_sum": 0,
                "loc_deleted_sum": 0
            },
            {
                "feature": "agent_edit",
                "user_initiated_interaction_count": total_agent_messages,
                "code_generation_activity_count": 0,
                "code_acceptance_activity_count": 0,
                "loc_suggested_to_add_sum": 0,
                "loc_suggested_to_delete_sum": 0,
                "loc_added_sum": total_agent_loc,
                "loc_deleted_sum": 0
            }
        ],
        
        # Boolean flags
        "used_agent": total_agent_messages > 0,
        "used_chat": chat_messages > 0,
        
        # Lines of code (root level)
        "loc_suggested_to_add_sum": completion_loc,
        "loc_suggested_to_delete_sum": 0,
        "loc_added_sum": total_modified_loc,
        "loc_deleted_sum": 0
    }
    
    return record


def convert_csv_to_copilot_json(
    csv_path: Path,
    output_path: Path,
    report_start_day: str,
    report_end_day: str,
    enterprise_id: str = "283613"
) -> int:
    """
    Convert an Augment CSV file to Copilot JSON format.

    Args:
        csv_path: Path to input CSV file
        output_path: Path to output JSON file
        report_start_day: Start date in YYYY-MM-DD format
        report_end_day: End date in YYYY-MM-DD format
        enterprise_id: Enterprise ID (default: "283613")

    Returns:
        Number of records converted
    """
    import csv

    records = []

    logger.info("Converting CSV to Copilot JSON: %s -> %s", csv_path, output_path)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip empty or invalid rows
            user = row.get("User", "").strip()
            if not user:
                continue

            # Skip rows with zero active days (optional)
            active_days = row.get("Active Days", "0")
            try:
                if int(active_days) == 0:
                    logger.debug("Skipping user %s with 0 active days", user)
                    continue
            except (ValueError, TypeError):
                pass

            # Convert row to Copilot format
            record = convert_csv_row_to_copilot_json(
                row,
                report_start_day,
                report_end_day,
                enterprise_id
            )

            records.append(record)

    # Write JSON output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)

    logger.info("Converted %d records to %s", len(records), output_path)

    return len(records)


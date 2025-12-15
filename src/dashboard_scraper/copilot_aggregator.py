"""
Aggregate multiple daily Copilot JSON files into a single consolidated file.

This module combines per-user metrics across multiple days into a single
aggregated JSON file matching the GitHub Copilot Metrics API format.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def aggregate_daily_json_files(
    json_files: List[Path],
    output_path: Path,
    report_start_day: str,
    report_end_day: str
) -> int:
    """
    Aggregate multiple daily Copilot JSON files into a single consolidated file.
    
    This function:
    1. Reads all daily JSON files
    2. Groups records by user_login
    3. Sums metrics across all days for each user
    4. Writes a single aggregated JSON file
    
    Args:
        json_files: List of paths to daily JSON files
        output_path: Path to write aggregated JSON file
        report_start_day: Start date in YYYY-MM-DD format
        report_end_day: End date in YYYY-MM-DD format
    
    Returns:
        Number of unique users in aggregated output
    """
    logger.info("Aggregating %d daily JSON files", len(json_files))
    
    # Dictionary to accumulate metrics per user
    user_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "user_initiated_interaction_count": 0,
        "code_generation_activity_count": 0,
        "code_acceptance_activity_count": 0,
        "loc_suggested_to_add_sum": 0,
        "loc_suggested_to_delete_sum": 0,
        "loc_added_sum": 0,
        "loc_deleted_sum": 0,
        "used_agent": False,
        "used_chat": False,
        "totals_by_feature": defaultdict(lambda: {
            "user_initiated_interaction_count": 0,
            "code_generation_activity_count": 0,
            "code_acceptance_activity_count": 0,
            "loc_suggested_to_add_sum": 0,
            "loc_suggested_to_delete_sum": 0,
            "loc_added_sum": 0,
            "loc_deleted_sum": 0,
        })
    })
    
    # Read and aggregate all daily files
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                daily_records = json.load(f)
            
            for record in daily_records:
                user_login = record["user_login"]
                user_id = record["user_id"]
                enterprise_id = record["enterprise_id"]
                
                # Initialize user if first time seeing them
                if "user_login" not in user_metrics[user_login]:
                    user_metrics[user_login]["user_login"] = user_login
                    user_metrics[user_login]["user_id"] = user_id
                    user_metrics[user_login]["enterprise_id"] = enterprise_id
                
                # Aggregate top-level metrics
                user_metrics[user_login]["user_initiated_interaction_count"] += record.get("user_initiated_interaction_count", 0)
                user_metrics[user_login]["code_generation_activity_count"] += record.get("code_generation_activity_count", 0)
                user_metrics[user_login]["code_acceptance_activity_count"] += record.get("code_acceptance_activity_count", 0)
                user_metrics[user_login]["loc_suggested_to_add_sum"] += record.get("loc_suggested_to_add_sum", 0)
                user_metrics[user_login]["loc_suggested_to_delete_sum"] += record.get("loc_suggested_to_delete_sum", 0)
                user_metrics[user_login]["loc_added_sum"] += record.get("loc_added_sum", 0)
                user_metrics[user_login]["loc_deleted_sum"] += record.get("loc_deleted_sum", 0)
                
                # Aggregate boolean flags (OR operation)
                user_metrics[user_login]["used_agent"] = user_metrics[user_login]["used_agent"] or record.get("used_agent", False)
                user_metrics[user_login]["used_chat"] = user_metrics[user_login]["used_chat"] or record.get("used_chat", False)
                
                # Aggregate totals_by_feature
                for feature_record in record.get("totals_by_feature", []):
                    feature = feature_record["feature"]
                    feature_metrics = user_metrics[user_login]["totals_by_feature"][feature]
                    
                    feature_metrics["user_initiated_interaction_count"] += feature_record.get("user_initiated_interaction_count", 0)
                    feature_metrics["code_generation_activity_count"] += feature_record.get("code_generation_activity_count", 0)
                    feature_metrics["code_acceptance_activity_count"] += feature_record.get("code_acceptance_activity_count", 0)
                    feature_metrics["loc_suggested_to_add_sum"] += feature_record.get("loc_suggested_to_add_sum", 0)
                    feature_metrics["loc_suggested_to_delete_sum"] += feature_record.get("loc_suggested_to_delete_sum", 0)
                    feature_metrics["loc_added_sum"] += feature_record.get("loc_added_sum", 0)
                    feature_metrics["loc_deleted_sum"] += feature_record.get("loc_deleted_sum", 0)
        
        except Exception as e:
            logger.error("Failed to read %s: %s", json_file, e)
            continue
    
    # Convert aggregated data to output format
    aggregated_records = []
    
    for user_login, metrics in user_metrics.items():
        # Convert totals_by_feature from dict to list
        totals_by_feature = [
            {"feature": feature, **feature_metrics}
            for feature, feature_metrics in metrics["totals_by_feature"].items()
        ]
        
        record = {
            "report_start_day": report_start_day,
            "report_end_day": report_end_day,
            "day": report_end_day,  # Use end date as reporting day
            "enterprise_id": metrics["enterprise_id"],
            "user_id": metrics["user_id"],
            "user_login": user_login,
            "user_initiated_interaction_count": metrics["user_initiated_interaction_count"],
            "code_generation_activity_count": metrics["code_generation_activity_count"],
            "code_acceptance_activity_count": metrics["code_acceptance_activity_count"],
            "totals_by_feature": totals_by_feature,
            "used_agent": metrics["used_agent"],
            "used_chat": metrics["used_chat"],
            "loc_suggested_to_add_sum": metrics["loc_suggested_to_add_sum"],
            "loc_suggested_to_delete_sum": metrics["loc_suggested_to_delete_sum"],
            "loc_added_sum": metrics["loc_added_sum"],
            "loc_deleted_sum": metrics["loc_deleted_sum"],
        }
        
        aggregated_records.append(record)
    
    # Write aggregated JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(aggregated_records, f, indent=2)
    
    logger.info("Aggregated %d users to %s", len(aggregated_records), output_path)
    
    return len(aggregated_records)


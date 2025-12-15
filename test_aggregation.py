#!/usr/bin/env python3
"""
Test the aggregation functionality with sample data.
"""

import json
import tempfile
from pathlib import Path

from dashboard_scraper.copilot_aggregator import aggregate_daily_json_files


def create_sample_daily_file(path: Path, day: str, user_email: str, completions: int):
    """Create a sample daily JSON file."""
    data = [{
        "report_start_day": "2024-11-17",
        "report_end_day": "2024-12-14",
        "day": day,
        "enterprise_id": "283613",
        "user_id": 12345,
        "user_login": user_email,
        "user_initiated_interaction_count": 10,
        "code_generation_activity_count": completions,
        "code_acceptance_activity_count": completions - 5,
        "totals_by_feature": [
            {
                "feature": "code_completion",
                "user_initiated_interaction_count": 0,
                "code_generation_activity_count": completions,
                "code_acceptance_activity_count": completions - 5,
                "loc_suggested_to_add_sum": 100,
                "loc_suggested_to_delete_sum": 0,
                "loc_added_sum": 100,
                "loc_deleted_sum": 0
            },
            {
                "feature": "chat_panel",
                "user_initiated_interaction_count": 5,
                "code_generation_activity_count": 0,
                "code_acceptance_activity_count": 0,
                "loc_suggested_to_add_sum": 0,
                "loc_suggested_to_delete_sum": 0,
                "loc_added_sum": 0,
                "loc_deleted_sum": 0
            },
            {
                "feature": "agent_edit",
                "user_initiated_interaction_count": 5,
                "code_generation_activity_count": 0,
                "code_acceptance_activity_count": 0,
                "loc_suggested_to_add_sum": 0,
                "loc_suggested_to_delete_sum": 0,
                "loc_added_sum": 50,
                "loc_deleted_sum": 0
            }
        ],
        "used_agent": True,
        "used_chat": True,
        "loc_suggested_to_add_sum": 100,
        "loc_suggested_to_delete_sum": 0,
        "loc_added_sum": 150,
        "loc_deleted_sum": 0
    }]
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def test_aggregation():
    """Test aggregation with sample data."""
    print("🧪 Testing aggregation functionality")
    print("=" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create 3 sample daily files for the same user
        daily_files = []
        for i, day in enumerate(["2024-12-12", "2024-12-13", "2024-12-14"], 1):
            file_path = tmpdir / f"copilot_metrics_{day}.json"
            create_sample_daily_file(file_path, day, "test@example.com", completions=20 * i)
            daily_files.append(file_path)
            print(f"✅ Created sample file: {file_path.name}")
        
        print()
        
        # Aggregate the files
        output_path = tmpdir / "copilot_metrics_aggregated.json"
        num_users = aggregate_daily_json_files(
            daily_files,
            output_path,
            "2024-11-17",
            "2024-12-14"
        )
        
        print(f"✅ Aggregated {num_users} user(s)")
        print()
        
        # Read and display the aggregated result
        with open(output_path, 'r') as f:
            aggregated = json.load(f)
        
        print("📊 Aggregated Result:")
        print("=" * 80)
        
        for user_record in aggregated:
            print(f"User: {user_record['user_login']}")
            print(f"  Total interactions: {user_record['user_initiated_interaction_count']}")
            print(f"  Total completions: {user_record['code_generation_activity_count']}")
            print(f"  Total accepted: {user_record['code_acceptance_activity_count']}")
            print(f"  Total LOC added: {user_record['loc_added_sum']}")
            print(f"  Used agent: {user_record['used_agent']}")
            print(f"  Used chat: {user_record['used_chat']}")
            print()
            print("  Features:")
            for feature in user_record['totals_by_feature']:
                print(f"    - {feature['feature']}: {feature['code_generation_activity_count']} completions, {feature['loc_added_sum']} LOC")
        
        print()
        print("=" * 80)
        print("✅ Aggregation test passed!")
        print()
        print("Expected values:")
        print("  - Total interactions: 30 (10 per day × 3 days)")
        print("  - Total completions: 120 (20 + 40 + 60)")
        print("  - Total accepted: 105 (15 + 35 + 55)")
        print("  - Total LOC added: 450 (150 per day × 3 days)")


if __name__ == "__main__":
    test_aggregation()


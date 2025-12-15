#!/usr/bin/env python3
"""
Quick installation test script.
Run this to verify all modules can be imported and basic functionality works.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from dashboard_scraper.client import DashboardClient
        print("  ✅ dashboard_scraper.client")
    except ImportError as e:
        print(f"  ❌ dashboard_scraper.client: {e}")
        return False
    
    try:
        from dashboard_scraper.config import Settings, load_settings
        print("  ✅ dashboard_scraper.config")
    except ImportError as e:
        print(f"  ❌ dashboard_scraper.config: {e}")
        return False
    
    try:
        from dashboard_scraper.copilot_converter import convert_csv_to_copilot_json
        print("  ✅ dashboard_scraper.copilot_converter")
    except ImportError as e:
        print(f"  ❌ dashboard_scraper.copilot_converter: {e}")
        return False
    
    try:
        from dashboard_scraper.daily_metrics import process_last_28_days
        print("  ✅ dashboard_scraper.daily_metrics")
    except ImportError as e:
        print(f"  ❌ dashboard_scraper.daily_metrics: {e}")
        return False
    
    try:
        from dashboard_scraper.date_utils import compute_last_28_days
        print("  ✅ dashboard_scraper.date_utils")
    except ImportError as e:
        print(f"  ❌ dashboard_scraper.date_utils: {e}")
        return False
    
    return True


def test_date_calculation():
    """Test that date calculation works."""
    print("\nTesting date calculation...")
    
    try:
        from dashboard_scraper.date_utils import compute_last_28_days
        start, end = compute_last_28_days()
        
        delta = end - start
        print(f"  ✅ Date range: {start.date()} to {end.date()}")
        print(f"  ✅ Duration: {delta.days} days")
        
        if delta.days != 28:
            print(f"  ⚠️  Warning: Expected 28 days, got {delta.days}")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_config():
    """Test that configuration loads."""
    print("\nTesting configuration...")
    
    try:
        from dashboard_scraper.config import load_settings
        settings = load_settings()
        
        print(f"  ✅ Base URL: {settings.metrics_api_base_url}")
        print(f"  ✅ Export dir: {settings.export_dir}")
        print(f"  ✅ Enterprise ID: {settings.enterprise_id}")
        print(f"  ✅ Log level: {settings.log_level}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_copilot_converter():
    """Test that Copilot converter can process a sample row."""
    print("\nTesting Copilot converter...")
    
    try:
        from dashboard_scraper.copilot_converter import convert_csv_row_to_copilot_json
        
        # Sample CSV row
        sample_row = {
            "User": "test@example.com",
            "Active Days": "5",
            "Completions": "100",
            "Accepted Completions": "80",
            "Chat Messages": "20",
            "Agent Messages": "10",
            "Remote Agent Messages": "5",
            "Interactive CLI Agent Messages": "3",
            "Non-Interactive CLI Agent Messages": "2",
            "Total Modified Lines of Code": "500",
            "Completion Lines of Code": "300",
            "Agent Lines of Code": "150",
            "Remote Agent Lines of Code": "30",
            "CLI Agent Lines of Code": "20"
        }
        
        result = convert_csv_row_to_copilot_json(
            sample_row,
            "2024-11-17",
            "2024-12-14",
            "283613"
        )
        
        # Verify key fields
        assert result["user_login"] == "test@example.com"
        assert result["enterprise_id"] == "283613"
        assert result["code_generation_activity_count"] == 100
        assert result["code_acceptance_activity_count"] == 80
        assert len(result["totals_by_feature"]) == 3
        
        print("  ✅ Sample conversion successful")
        print(f"  ✅ User: {result['user_login']}")
        print(f"  ✅ Completions: {result['code_generation_activity_count']}")
        print(f"  ✅ Features: {len(result['totals_by_feature'])}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("🧪 Installation Test Suite")
    print("=" * 80)
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Date Calculation", test_date_calculation()))
    results.append(("Configuration", test_config()))
    results.append(("Copilot Converter", test_copilot_converter()))
    
    print()
    print("=" * 80)
    print("📊 Test Results")
    print("=" * 80)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    
    if all(passed for _, passed in results):
        print("🎉 All tests passed! Installation is working correctly.")
        print()
        print("Next steps:")
        print("  1. Set up authentication: python -m dashboard_scraper --auth")
        print("  2. Run the feature: python -m dashboard_scraper --last-28-days")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())


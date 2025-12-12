#!/usr/bin/env python3
"""
Check all unique fields across all user records.
"""
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dashboard_scraper.config import load_settings
from dashboard_scraper.cookie_auth import CookieAuth
from dashboard_scraper.http import HTTPClient
from dashboard_scraper.client import DashboardClient

def main():
    settings = load_settings()
    cookie_auth = CookieAuth(settings.cookie_file_path())
    
    if not cookie_auth.has_cookies():
        print("❌ No cookies found. Run: python -m dashboard_scraper --auth")
        sys.exit(1)
    
    http = HTTPClient(settings, cookie_auth=cookie_auth)
    client = DashboardClient(settings, http)
    
    # Test with 30 days
    end = datetime.now()
    start = end - timedelta(days=30)
    
    data = client.fetch_endpoint("/api/user-feature-stats", start, end)
    records = data.get("userFeatureStats", [])
    
    # Collect all unique fields
    all_fields = set()
    for record in records:
        all_fields.update(record.keys())
    
    print("All unique fields in user-feature-stats:")
    print("=" * 80)
    for field in sorted(all_fields):
        print(f"  - {field}")
    print()
    print(f"Total: {len(all_fields)} fields")
    print(f"Total records: {len(records)}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Test script to see what URLs are being generated for API calls.
"""
from datetime import datetime, timezone
from urllib.parse import quote
import json


def parse_date(date_str):
    """Parse date string in MM-DD-YYYY format."""
    dt = datetime.strptime(date_str, "%m-%d-%Y")
    return dt.replace(tzinfo=timezone.utc)


def format_date_param(dt):
    """Format datetime as URL-encoded JSON for the API."""
    date_obj = {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day
    }
    # Use separators to remove spaces from JSON (API expects no spaces)
    return quote(json.dumps(date_obj, separators=(',', ':')))


def build_url(endpoint, start, end):
    """Build the full URL with date parameters."""
    base_url = "https://app.augmentcode.com/"
    start_param = format_date_param(start)
    end_param = format_date_param(end)
    return f"{base_url}{endpoint}?startDate={start_param}&endDate={end_param}"


def test_url_generation():
    """Test URL generation for different date scenarios."""
    
    print("=" * 80)
    print("API URL Generation Test")
    print("=" * 80)
    
    endpoint = "/api/user-feature-stats"
    
    # Test 1: Single date (Oct 21)
    print("\n1. Single date: 10-21-2025")
    start = parse_date("10-21-2025")
    end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
    url = build_url(endpoint, start, end)
    print(f"   Start: {start}")
    print(f"   End:   {end}")
    print(f"   URL: {url}")
    
    # Decode to see what the API receives
    start_json = json.dumps({"year": start.year, "month": start.month, "day": start.day})
    end_json = json.dumps({"year": end.year, "month": end.month, "day": end.day})
    print(f"   Start param (decoded): {start_json}")
    print(f"   End param (decoded):   {end_json}")
    
    # Test 2: Date range (Oct 20-21)
    print("\n2. Date range: 10-20-2025 to 10-21-2025")
    start = parse_date("10-20-2025")
    end_date = parse_date("10-21-2025")
    end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    url = build_url(endpoint, start, end)
    print(f"   Start: {start}")
    print(f"   End:   {end}")
    print(f"   URL: {url}")
    
    start_json = json.dumps({"year": start.year, "month": start.month, "day": start.day})
    end_json = json.dumps({"year": end.year, "month": end.month, "day": end.day})
    print(f"   Start param (decoded): {start_json}")
    print(f"   End param (decoded):   {end_json}")
    
    # Test 3: Today
    print("\n3. Today: 10-22-2025")
    start = parse_date("10-22-2025")
    end = datetime.now(timezone.utc)
    url = build_url(endpoint, start, end)
    print(f"   Start: {start}")
    print(f"   End:   {end}")
    print(f"   URL: {url}")
    
    start_json = json.dumps({"year": start.year, "month": start.month, "day": start.day})
    end_json = json.dumps({"year": end.year, "month": end.month, "day": end.day})
    print(f"   Start param (decoded): {start_json}")
    print(f"   End param (decoded):   {end_json}")
    
    print("\n" + "=" * 80)
    print("Note: The API expects dates in format: {\"year\":2025,\"month\":10,\"day\":22}")
    print("=" * 80)


if __name__ == "__main__":
    test_url_generation()


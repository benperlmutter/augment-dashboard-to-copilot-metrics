#!/usr/bin/env python3
"""
Test script to see the actual API response structure.
"""
import sys
import os
import json
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
    
    print("=" * 80)
    print("Testing API Endpoints")
    print("=" * 80)
    print(f"Date range: {start.date()} to {end.date()}")
    print()
    
    endpoints = settings.get_endpoints_to_scrape()
    
    for name, endpoint in endpoints:
        print(f"\n{'=' * 80}")
        print(f"Endpoint: {name} ({endpoint})")
        print('=' * 80)
        
        try:
            data = client.fetch_endpoint(endpoint, start, end)
            
            print(f"\nResponse type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                
                # Show first item if it's a list
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        print(f"\n{key} (list with {len(value)} items)")
                        print("First item:")
                        print(json.dumps(value[0], indent=2, default=str))
                        break
                else:
                    # No list found, show the whole dict
                    print("\nFull response:")
                    print(json.dumps(data, indent=2, default=str))
                    
            elif isinstance(data, list):
                print(f"List with {len(data)} items")
                if len(data) > 0:
                    print("\nFirst item:")
                    print(json.dumps(data[0], indent=2, default=str))
            else:
                print(f"\nResponse: {data}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()


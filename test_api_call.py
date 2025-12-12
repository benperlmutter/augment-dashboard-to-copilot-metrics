#!/usr/bin/env python3
"""
Test actual API call to see what's being returned.
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import requests

def format_date_param(dt):
    """Format datetime as URL-encoded JSON for the API."""
    date_obj = {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day
    }
    return quote(json.dumps(date_obj, separators=(',', ':')))

def test_api_call():
    """Test API call with current date format."""
    
    # Use default 30-day window
    now = datetime.now(timezone.utc)
    end = now
    start = end - timedelta(days=30)
    
    base_url = "https://app.augmentcode.com/"
    endpoint = "/api/user-feature-stats"
    
    start_param = format_date_param(start)
    end_param = format_date_param(end)
    
    url = f"{base_url}{endpoint}?startDate={start_param}&endDate={end_param}"
    
    print("=" * 80)
    print("Testing API Call")
    print("=" * 80)
    print(f"\nDate range:")
    print(f"  Start: {start}")
    print(f"  End:   {end}")
    print(f"\nURL:")
    print(f"  {url}")
    print(f"\nDecoded parameters:")
    from urllib.parse import unquote
    print(f"  startDate={unquote(start_param)}")
    print(f"  endDate={unquote(end_param)}")
    
    print("\n" + "=" * 80)
    print("Making API request...")
    print("=" * 80)
    
    # Load cookies from file
    try:
        with open("secrets/cookies.json", "r") as f:
            cookies_dict = json.load(f)
        
        # Make request
        response = requests.get(url, cookies=cookies_dict)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'content-length']:
                print(f"  {key}: {value}")
        
        if response.status_code == 200:
            # Check if response is JSON
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                data = response.json()
                print(f"\n✅ Success!")
                print(f"Response type: {type(data)}")

                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")

                    if "userFeatureStats" in data:
                        records = data["userFeatureStats"]
                        print(f"\n✅ Found {len(records)} user records")
                        if len(records) > 0:
                            print(f"\nFirst record sample:")
                            first = records[0]
                            for key in list(first.keys())[:5]:
                                print(f"  {key}: {first[key]}")
                    else:
                        print(f"\n⚠️  No 'userFeatureStats' key found")
                        print(f"Full response: {json.dumps(data, indent=2)[:500]}")
                else:
                    print(f"Response: {data}")
            else:
                print(f"\n⚠️  Response is HTML, not JSON!")
                print(f"This usually means:")
                print(f"  1. Cookies have expired (need to re-authenticate)")
                print(f"  2. API is redirecting to login page")
                print(f"  3. URL format is incorrect")
                print(f"\nFirst 500 chars of response:")
                print(response.text[:500])
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except FileNotFoundError:
        print("\n❌ Error: cookies.json not found")
        print("Run: python -m dashboard_scraper --auth")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_call()


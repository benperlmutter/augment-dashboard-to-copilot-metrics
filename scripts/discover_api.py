#!/usr/bin/env python3
"""
Helper script to discover the actual API endpoint used by the dashboard.

This script helps you find the correct API endpoint by inspecting network requests.
"""

print("""
================================================================================
API Endpoint Discovery Helper
================================================================================

The dashboard at your application URL is a web page, not an API endpoint.
We need to find the actual API it calls.

Follow these steps:

1. Open your dashboard URL in your browser

2. Open DevTools (F12 or Cmd+Option+I)

3. Go to the Network tab

4. Reload the page (Cmd+R or Ctrl+R)

5. Look for API requests in the Network tab. Common patterns:
   - Look for XHR/Fetch requests (filter by XHR)
   - Look for requests to endpoints containing:
     * "api"
     * "metrics"
     * "usage"
     * "dashboard"
     * "stats"
     * "analytics"
   
6. Click on the API request and note:
   - Request URL (full URL)
   - Request Method (GET/POST)
   - Query Parameters (if any)
   - Request Headers (especially Cookie)
   - Response format (JSON, etc.)

7. Common endpoint patterns to look for:
   - /api/v1/metrics
   - /api/dashboard/metrics
   - /api/usage
   - /api/analytics/usage
   - /graphql (if using GraphQL)
   - /trpc/* (if using tRPC)

================================================================================
What to do next:
================================================================================

Once you find the API endpoint, update your .env file:

METRICS_API_BASE_URL=https://app.augmentcode.com/
METRICS_ENDPOINT=/api/actual/endpoint/here

If the API uses different query parameters than start/end/limit, let me know
and I'll update the client code to match.

Common parameter patterns:
- start/end (timestamps)
- from/to (timestamps)
- startDate/endDate
- period=30d
- range=30
- filter=last_30_days

================================================================================
""")

# Ask if they want to test a specific endpoint
print("\nOptional: Test an endpoint now")
print("If you've found an endpoint, enter it here to test (or press Enter to skip):")
endpoint = input("Endpoint (e.g., /api/v1/metrics): ").strip()

if endpoint:
    import sys
    import os
    
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    from dashboard_scraper.config import load_settings
    from dashboard_scraper.cookie_auth import CookieAuth
    import requests
    
    settings = load_settings()
    cookie_auth = CookieAuth(settings.cookie_file_path())
    
    if not cookie_auth.has_cookies():
        print("\n❌ No cookies found. Run: python -m dashboard_scraper --auth")
        sys.exit(1)
    
    cookies = cookie_auth.get_cookies_dict()
    base_url = settings.metrics_api_base_url
    full_url = f"{base_url}{endpoint}"
    
    print(f"\n🔍 Testing: {full_url}")
    print(f"   Cookies: {len(cookies)} cookie(s)")
    
    try:
        response = requests.get(full_url, cookies=cookies, timeout=10)
        print(f"\n✓ Status: {response.status_code}")
        print(f"✓ Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"✓ Response length: {len(response.text)} bytes")
        
        if response.status_code == 200:
            print("\n✓ Success! This endpoint works.")
            print("\nFirst 500 characters of response:")
            print("-" * 80)
            print(response.text[:500])
            print("-" * 80)
            
            # Try to parse as JSON
            try:
                data = response.json()
                print(f"\n✓ Valid JSON response")
                print(f"✓ Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'array'}")
            except:
                print("\n⚠ Response is not JSON")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text[:500])
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
else:
    print("\nSkipped. Follow the steps above to find the API endpoint manually.")


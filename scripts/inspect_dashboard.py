#!/usr/bin/env python3
"""
Helper script to fetch and inspect the dashboard HTML structure.
This helps us understand how to parse the metrics data from the page.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dashboard_scraper.config import load_settings
from dashboard_scraper.cookie_auth import CookieAuth
import requests

def main():
    settings = load_settings()
    cookie_auth = CookieAuth(settings.cookie_file_path())
    
    if not cookie_auth.has_cookies():
        print("❌ No cookies found. Run: python -m dashboard_scraper --auth")
        sys.exit(1)
    
    cookies = cookie_auth.get_cookies_dict()
    url = "https://app.staging.augmentcode.com/dashboard?yourUsageFilter=30"
    
    print(f"🔍 Fetching: {url}")
    print(f"   Using {len(cookies)} cookie(s)")
    print()
    
    try:
        response = requests.get(url, cookies=cookies, timeout=30)
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"✓ Response length: {len(response.text)} bytes")
        print()
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text[:1000])
            sys.exit(1)
        
        html = response.text
        
        # Save to file for inspection
        output_file = "dashboard_page.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✓ Saved HTML to: {output_file}")
        print()
        
        # Look for common patterns
        print("=" * 80)
        print("ANALYSIS")
        print("=" * 80)
        
        # Check if it's a React/SPA app
        if "react" in html.lower() or "__NEXT_DATA__" in html or "root" in html:
            print("\n⚠️  This appears to be a React/Next.js single-page application (SPA)")
            print("    The data is likely loaded via JavaScript after page load.")
            print()
            
            # Look for embedded JSON data
            if "__NEXT_DATA__" in html:
                print("✓ Found __NEXT_DATA__ - Next.js app with server-side data")
                import re
                match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
                if match:
                    print("✓ Can extract data from __NEXT_DATA__ script tag")
                    print()
                    print("First 500 chars of __NEXT_DATA__:")
                    print("-" * 80)
                    print(match.group(1)[:500])
                    print("-" * 80)
            
            # Look for other embedded data
            import re
            script_data_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.initialData\s*=\s*({.*?});',
                r'window\.APP_STATE\s*=\s*({.*?});',
            ]
            
            for pattern in script_data_patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                if matches:
                    print(f"✓ Found embedded data matching pattern: {pattern[:50]}...")
                    print("First 500 chars:")
                    print("-" * 80)
                    print(matches[0][:500])
                    print("-" * 80)
                    print()
        
        # Look for tables
        if "<table" in html.lower():
            print("✓ Found <table> tags - data might be in HTML tables")
            import re
            tables = re.findall(r'<table[^>]*>.*?</table>', html, re.DOTALL | re.IGNORECASE)
            print(f"  Found {len(tables)} table(s)")
            print()
        
        # Look for JSON in script tags
        import re
        json_scripts = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
        if json_scripts:
            print(f"✓ Found {len(json_scripts)} JSON script tag(s)")
            for i, script in enumerate(json_scripts[:3]):  # Show first 3
                print(f"\n  Script {i+1} (first 300 chars):")
                print("  " + "-" * 76)
                print("  " + script[:300].replace("\n", "\n  "))
                print("  " + "-" * 76)
            print()
        
        # Look for data attributes
        data_attrs = re.findall(r'data-[a-z-]+=["\'][^"\']*["\']', html, re.IGNORECASE)
        if data_attrs:
            print(f"✓ Found {len(data_attrs)} data-* attributes")
            unique_attrs = set([attr.split('=')[0] for attr in data_attrs])
            print(f"  Unique data attributes: {', '.join(sorted(unique_attrs)[:10])}")
            print()
        
        print("=" * 80)
        print("\nNext steps:")
        print("1. Open dashboard_page.html in a text editor")
        print("2. Search for your usage data (numbers you see on the dashboard)")
        print("3. Look at the HTML structure around that data")
        print("4. Tell me what you find, and I'll update the scraper accordingly")
        print()
        print("Common patterns:")
        print("  - Data in __NEXT_DATA__ script tag (Next.js)")
        print("  - Data in HTML tables")
        print("  - Data in data-* attributes")
        print("  - Data loaded via JavaScript (need to find the API endpoint)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


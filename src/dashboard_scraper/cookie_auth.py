"""
Cookie-based authentication for dashboard scraper.
Simple authentication method - just copy your session cookie from the browser.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class CookieAuth:
    """
    Manages cookie-based authentication.

    Uses a session cookie that you copy from your browser after
    logging in manually to the dashboard.
    """
    
    def __init__(self, cookie_file: Path):
        """
        Initialize cookie auth.
        
        Args:
            cookie_file: Path to JSON file storing cookies
        """
        self.cookie_file = cookie_file
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save_cookies(self, cookies: Dict[str, str]) -> None:
        """
        Save cookies to file with restricted permissions.

        Args:
            cookies: Dictionary of cookie name -> value
        """
        logger.info("Saving cookies to %s", self.cookie_file)
        with open(self.cookie_file, "w") as f:
            json.dump(cookies, f, indent=2)
        # Restrict permissions to owner only (read/write) for security
        os.chmod(self.cookie_file, 0o600)
        logger.debug("Set cookie file permissions to 0600")
    
    def load_cookies(self) -> Optional[Dict[str, str]]:
        """
        Load cookies from file.
        
        Returns:
            Dictionary of cookie name -> value, or None if file doesn't exist
        """
        if not self.cookie_file.exists():
            logger.warning("Cookie file not found: %s", self.cookie_file)
            return None
        
        try:
            with open(self.cookie_file, "r") as f:
                cookies = json.load(f)
            logger.info("Loaded %d cookies from %s", len(cookies), self.cookie_file)
            return cookies
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load cookies: %s", e)
            return None
    
    def get_cookies_dict(self) -> Dict[str, str]:
        """
        Get cookies as a dictionary suitable for requests.
        
        Returns:
            Dictionary of cookie name -> value (empty if no cookies)
        """
        cookies = self.load_cookies()
        return cookies if cookies else {}
    
    def has_cookies(self) -> bool:
        """
        Check if cookies are available.
        
        Returns:
            True if cookie file exists and contains cookies
        """
        cookies = self.load_cookies()
        return bool(cookies)


def extract_cookies_from_browser_format(browser_cookies: str) -> Dict[str, str]:
    """
    Parse cookies from browser format (copied from DevTools).
    
    Supports multiple formats:
    1. "name1=value1; name2=value2" (standard Cookie header format)
    2. JSON: {"name1": "value1", "name2": "value2"}
    3. Single cookie: "name=value"
    
    Args:
        browser_cookies: Cookie string from browser
        
    Returns:
        Dictionary of cookie name -> value
    """
    browser_cookies = browser_cookies.strip()
    
    # Try JSON format first
    if browser_cookies.startswith("{"):
        try:
            return json.loads(browser_cookies)
        except json.JSONDecodeError:
            pass
    
    # Parse semicolon-separated format
    cookies = {}
    for part in browser_cookies.split(";"):
        part = part.strip()
        if "=" in part:
            name, value = part.split("=", 1)
            cookies[name.strip()] = value.strip()
    
    return cookies


def interactive_cookie_setup(cookie_file: Path) -> None:
    """
    Interactive CLI to help user set up cookie authentication.
    
    Args:
        cookie_file: Path where cookies will be saved
    """
    print("\n" + "="*70)
    print("Cookie-Based Authentication Setup")
    print("="*70)
    print("\nSimple setup - just copy your session cookie!")
    print("\nSteps:")
    print("1. Open your dashboard URL in your browser")
    print("2. Log in with your credentials")
    print("3. Open DevTools (F12 or Cmd+Option+I)")
    print("4. Go to: Application → Cookies → [your dashboard URL]")
    print("5. Find the session cookie (usually named 'session', 'auth_token', or similar)")
    print("6. Copy the cookie value")
    print("\nAlternatively, you can:")
    print("- Go to Network tab → Reload page → Click any request → Copy 'Cookie' header")
    print("\n" + "="*70)
    
    print("\nEnter your cookies in one of these formats:")
    print("  1. Cookie header: name1=value1; name2=value2")
    print("  2. JSON: {\"name1\": \"value1\", \"name2\": \"value2\"}")
    print("  3. Single cookie: name=value")
    print("\nPaste your cookies here (or press Ctrl+C to cancel):")
    
    try:
        cookie_input = input("> ").strip()
        
        if not cookie_input:
            print("❌ No cookies provided. Exiting.")
            return
        
        cookies = extract_cookies_from_browser_format(cookie_input)
        
        if not cookies:
            print("❌ Could not parse cookies. Please check the format.")
            return
        
        print(f"\n✓ Parsed {len(cookies)} cookie(s):")
        for name in cookies.keys():
            print(f"  - {name}")
        
        # Save cookies
        auth = CookieAuth(cookie_file)
        auth.save_cookies(cookies)
        
        print(f"\n✓ Cookies saved to: {cookie_file}")
        print("\nYou can now run the scraper without --auth flag:")
        print("  python -m dashboard_scraper")
        print("\n" + "="*70)
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


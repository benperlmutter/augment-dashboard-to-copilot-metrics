from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from .config import Settings
from .cookie_auth import CookieAuth

logger = logging.getLogger(__name__)


class AuthenticationExpiredError(Exception):
    """Raised when authentication has expired."""
    pass


class HTTPClient:
    def __init__(
        self,
        settings: Settings,
        cookie_auth: CookieAuth
    ) -> None:
        """
        Initialize HTTP client with cookie authentication.

        Args:
            settings: Application settings
            cookie_auth: Cookie authentication manager
        """
        self.s = settings
        self.cookie_auth = cookie_auth
        self.session = requests.Session()

        # Set up cookies
        cookies = self.cookie_auth.get_cookies_dict()
        if cookies:
            self.session.cookies.update(cookies)
            logger.info("Loaded %d cookies into session", len(cookies))

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        headers = kwargs.pop("headers", {})
        kwargs["headers"] = headers
        kwargs.setdefault("timeout", self.s.request_timeout_seconds)

        attempt = 0
        backoff = self.s.retry_backoff_seconds
        max_retries = self.s.max_retries

        while True:
            try:
                resp = self.session.request(method, url, **kwargs)
                if resp.status_code == 401:
                    # Cookie auth failed - session expired
                    logger.error("⚠️  401 Unauthorized - Session has expired")
                    logger.error("Run with --auth to manually set up new cookies.")
                    raise AuthenticationExpiredError(
                        "Session expired. Please re-authenticate with --auth"
                    )

                if resp.status_code in {429, 500, 502, 503, 504} and attempt < max_retries:
                    attempt += 1
                    sleep = backoff * (2 ** (attempt - 1))
                    logger.warning("HTTP %s; retrying in %.1fs (attempt %d/%d)", resp.status_code, sleep, attempt, max_retries)
                    time.sleep(sleep)
                    continue
                resp.raise_for_status()
                return resp
            except AuthenticationExpiredError:
                raise
            except requests.RequestException as e:
                if attempt < max_retries:
                    attempt += 1
                    sleep = backoff * (2 ** (attempt - 1))
                    logger.warning("Request error %s; retrying in %.1fs (attempt %d/%d)", e, sleep, attempt, max_retries)
                    time.sleep(sleep)
                    continue
                logger.error("Request failed after %d attempts", attempt)
                raise


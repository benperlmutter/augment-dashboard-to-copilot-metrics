from __future__ import annotations

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Cookie authentication
    cookie_file: str = "secrets/cookies.json"

    # API
    metrics_api_base_url: str = "https://app.augmentcode.com/"

    # Multiple endpoints for different data types
    user_feature_stats_endpoint: str = "/api/user-feature-stats"
    tenant_feature_stats_endpoint: str = "/api/tenant-feature-stats"
    tenant_mau_endpoint: str = "/api/tenant-monthly-active-users"

    # Which endpoints to scrape (comma-separated)
    # Options: user_stats, tenant_stats, tenant_mau, all
    scrape_endpoints: str = "all"

    # App behavior
    lookback_days: int = 30
    export_dir: str = "data"
    log_level: str = "INFO"

    # HTTP
    request_timeout_seconds: int = 30
    max_retries: int = 3
    retry_backoff_seconds: float = 0.5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def export_dir_path(self) -> Path:
        p = Path(self.export_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def cookie_file_path(self) -> Path:
        p = Path(self.cookie_file)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def get_endpoints_to_scrape(self) -> List[tuple[str, str]]:
        """
        Get list of (name, endpoint) tuples to scrape.

        Returns:
            List of (name, endpoint_path) tuples
        """
        all_endpoints = [
            ("user_stats", self.user_feature_stats_endpoint),
            ("tenant_stats", self.tenant_feature_stats_endpoint),
            ("tenant_mau", self.tenant_mau_endpoint),
        ]

        if self.scrape_endpoints.lower() == "all":
            return all_endpoints

        # Parse comma-separated list
        requested = [s.strip().lower() for s in self.scrape_endpoints.split(",")]
        return [(name, endpoint) for name, endpoint in all_endpoints if name in requested]


def load_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]


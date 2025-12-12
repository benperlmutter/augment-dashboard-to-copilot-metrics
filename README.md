# dashboard-scraper

A Python-based metrics scraper for extracting dashboard usage data via authenticated API calls and exporting to CSV.

## Features

- **Cookie-based authentication** - Simple session cookie setup from your browser
- **Custom date ranges** - Query specific dates or date ranges
- **30-day rolling window** data extraction (configurable)
- **Automatic pagination** handling for complete data collection
- **CSV export** with flattened nested data and stable column ordering
- **Retry logic** with exponential backoff for resilient API calls
- **Cron-ready** for daily scheduled execution

## Architecture

This project follows patterns from the `docs-scraper` reference implementation:

- **Modular design**: Separate modules for auth, HTTP client, API client, export, and config
- **Pydantic settings**: Environment-based configuration with `.env` support
- **Structured logging**: Consistent log format with configurable levels
- **Token persistence**: Secure local storage with automatic refresh
- **Error handling**: Graceful retries and clear error messages

## Project Structure

```
dashboard-scraper/
├── src/dashboard_scraper/
│   ├── __init__.py
│   ├── client.py            # Dashboard API client with pagination
│   ├── config.py            # Pydantic settings loader
│   ├── cookie_auth.py       # Cookie-based authentication
│   ├── date_utils.py        # Date range calculations
│   ├── export.py            # CSV writer with flattening
│   ├── http.py              # HTTP client with retries
│   ├── logging_config.py    # Logging setup
│   └── main.py              # CLI entrypoint
├── tests/                   # Unit tests
├── data/                    # CSV output directory (gitignored)
├── secrets/                 # Cookie storage (gitignored)
├── .env.example             # Example environment configuration
├── pyproject.toml           # Project metadata and dependencies
└── requirements.txt         # Pinned dependencies

```

## Setup

### 1. Install dependencies

```bash
# Create virtual environment (if not already created)
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in editable mode
pip install -e .
```

### 2. Configure your API base URL

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and set your API base URL:

```bash
METRICS_API_BASE_URL=https://app.augmentcode.com/
```

### 3. Authenticate

Set up your session cookie from the browser:

```bash
python -m dashboard_scraper --auth
```

When prompted, enter your session cookie in the following format:

```
_session=<INSERT URL DECODED COOKIE FROM BROWSER HERE>
```

**How to get your session cookie:**
1. Open your dashboard (https://app.augmentcode.com/) in a browser
2. Log in with your credentials
3. Open DevTools (F12 or Cmd+Option+I)
4. Go to: Application → Cookies → [your dashboard URL]
5. Find the `_session` cookie
6. Copy the **URL-decoded** value (not the encoded version)
7. Paste it in the format shown above when prompted

The cookie will be saved to `secrets/cookies.json` for future runs.

**Note:** Session cookies typically expire after ~1 hour and require re-authentication.

## Usage

### Basic usage (30-day window)

```bash
python -m dashboard_scraper
```

This fetches metrics for the past 30 days and writes to `data/metrics_YYYYMMDD.csv`.

### Custom date ranges

Query specific dates or date ranges:

```bash
# Single date (24-hour period or up to now if today)
python -m dashboard_scraper 10-22-2025

# Date range (from start date 00:00 to end date 23:59:59)
python -m dashboard_scraper 10-20-2025 10-22-2025
```

**Date format:** `MM-DD-YYYY` (e.g., `10-22-2025`)

**Output filenames:**
- Single date: `metrics_20251022.csv`
- Date range: `metrics_20251020_to_20251022.csv`
- Default (30 days): `metrics_YYYYMMDD.csv` (current date)

### Custom output file

```bash
python -m dashboard_scraper --out custom_metrics.csv
```

### Debug logging

```bash
python -m dashboard_scraper --log-level DEBUG
```

### Re-authenticate

If your session expires, run the authentication setup again:

```bash
python -m dashboard_scraper --auth
```

## Scheduling with Cron

To run daily at 1:05 AM UTC:

```bash
crontab -e
```

Add:

```cron
5 1 * * * /path/to/dashboard-scraper/.venv/bin/python -m dashboard_scraper >> /var/log/dashboard_scraper.log 2>&1
```

**Important**: Ensure the cron environment has access to the `.env` file or set environment variables explicitly in the crontab.

## Output Format

CSV files are written to the `data/` directory with:

- **Filename**: `metrics_YYYYMMDD.csv` (date of export)
- **Headers**: Dynamically generated from API response fields
- **Column ordering**: Common fields (`timestamp`, `date`, `user_id`, `email`, `metric`, `value`) appear first, followed by alphabetically sorted remaining fields
- **Nested data**: Flattened with dot notation (e.g., `user.email`, `usage.count`)
- **Lists**: Serialized as JSON strings to maintain CSV structure
- **Timestamps**: Normalized to ISO 8601 UTC format

Example output:

```csv
timestamp,user_id,email,metric,value,tool_name
2025-10-01T00:00:00+00:00,user123,user@example.com,tool_usage,42,code_completion
2025-10-01T01:00:00+00:00,user456,other@example.com,tool_usage,17,agent_chat
```

## Configuration Reference

All settings can be configured via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `COOKIE_FILE` | `secrets/cookies.json` | Path to cookie storage file |
| `METRICS_API_BASE_URL` | `https://app.augmentcode.com/` | Base URL for your metrics API |
| `USER_FEATURE_STATS_ENDPOINT` | `/api/user-feature-stats` | User stats API endpoint |
| `TENANT_FEATURE_STATS_ENDPOINT` | `/api/tenant-feature-stats` | Tenant stats API endpoint |
| `TENANT_MAU_ENDPOINT` | `/api/tenant-monthly-active-users` | MAU API endpoint |
| `SCRAPE_ENDPOINTS` | `all` | Which endpoints to scrape (comma-separated or "all") |
| `LOOKBACK_DAYS` | `30` | Number of days to fetch in default mode |
| `EXPORT_DIR` | `data` | Output directory for CSV files |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `REQUEST_TIMEOUT_SECONDS` | `30` | HTTP request timeout |
| `MAX_RETRIES` | `3` | Maximum retry attempts for failed requests |
| `RETRY_BACKOFF_SECONDS` | `0.5` | Initial backoff delay for retries (exponential) |

## Development

### Running tests

```bash
pip install -e ".[dev]"
pytest
```

### Code formatting

```bash
black src/ tests/
ruff check src/ tests/
```

## Troubleshooting

### "No cookies found" error

Run the authentication setup:
```bash
python -m dashboard_scraper --auth
```

### "401 Unauthorized" errors

Your session has expired. Re-authenticate:
```bash
python -m dashboard_scraper --auth
```

### Empty CSV output

- Verify the API endpoints are correct in your `.env` file
- Ensure your session is valid (check for 401 errors in logs)
- Ensure the API returns data for the specified date range
- Run with `--log-level DEBUG` to inspect API responses

### Pagination not working

The client supports common pagination patterns (`next` URL, `items`/`data` arrays). If your API uses a different pattern, you may need to customize `client.py`.

## License

MIT

## Support

For issues or questions, contact the Augment Code team or open an issue in this repository.

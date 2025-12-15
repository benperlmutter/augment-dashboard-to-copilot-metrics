# dashboard-scraper

A Python-based metrics scraper for extracting dashboard usage data via authenticated API calls and exporting to CSV.

## Features

- **Cookie-based authentication** - Simple session cookie setup from your browser
- **Custom date ranges** - Query specific dates or date ranges
- **30-day rolling window** data extraction (configurable)
- **28-day daily metrics** - Generate daily CSV and Copilot JSON files for the last 28 days
- **Copilot JSON conversion** - Automatic conversion to GitHub Copilot Metrics API format
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
│   ├── copilot_converter.py # CSV to Copilot JSON converter
│   ├── daily_metrics.py     # 28-day daily metrics processing
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

### 28-day daily metrics (NEW)

Generate daily CSV and Copilot JSON files for the last 28 days:

```bash
python -m dashboard_scraper --last-28-days
```

This will:
1. Calculate the date range (28 days ago to yesterday)
2. Fetch metrics for each day individually
3. Generate daily CSV files in Augment format
4. Convert each CSV to Copilot JSON format
5. Organize files in a dated directory

**Output structure:**
```
data/
└── daily_exports_2024-11-14_to_2024-12-11/
    ├── augment_metrics_2024-11-14.csv
    ├── copilot_metrics_2024-11-14.json
    ├── augment_metrics_2024-11-15.csv
    ├── copilot_metrics_2024-11-15.json
    │   ...
    ├── augment_metrics_2024-12-11.csv
    └── copilot_metrics_2024-12-11.json
```

**Features:**
- Individual day processing with progress tracking
- Automatic retry logic for failed days
- Summary report showing successful/failed days
- Both Augment CSV and Copilot JSON formats
- Organized directory structure with date range in name

**Note:** This mode is mutually exclusive with custom date parameters.

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

## Output Formats

### CSV Format (Augment)

CSV files are written to the `data/` directory with:

- **Filename**: `metrics_YYYYMMDD.csv` or `augment_metrics_YYYY-MM-DD.csv` (for daily exports)
- **Headers**: Dynamically generated from API response fields
- **Column ordering**: Common fields (`timestamp`, `date`, `user_id`, `email`, `metric`, `value`) appear first, followed by alphabetically sorted remaining fields
- **Nested data**: Flattened with dot notation (e.g., `user.email`, `usage.count`)
- **Lists**: Serialized as JSON strings to maintain CSV structure
- **Timestamps**: Normalized to ISO 8601 UTC format

Example output:

```csv
User,First Seen,Last Seen,Active Days,Completions,Accepted Completions,Accept Rate,Chat Messages,Agent Messages,...
user@example.com,2024-11-14,2024-12-11,28,450,180,40.0%,25,50,...
```

### JSON Format (Copilot)

When using `--last-28-days`, JSON files are automatically generated in GitHub Copilot Metrics API format:

- **Filename**: `copilot_metrics_YYYY-MM-DD.json`
- **Format**: Array of per-user records
- **Schema**: Follows official GitHub Copilot per-user JSON schema

Example output:

```json
[
  {
    "report_start_day": "2024-11-14",
    "report_end_day": "2024-12-11",
    "day": "2024-12-11",
    "enterprise_id": "283613",
    "user_id": 12345,
    "user_login": "user@example.com",

    "user_initiated_interaction_count": 85,
    "code_generation_activity_count": 450,
    "code_acceptance_activity_count": 180,

    "totals_by_feature": [
      {
        "feature": "code_completion",
        "code_generation_activity_count": 450,
        "code_acceptance_activity_count": 180,
        "loc_suggested_to_add_sum": 500,
        "loc_added_sum": 500
      },
      {
        "feature": "chat_panel",
        "user_initiated_interaction_count": 25
      },
      {
        "feature": "agent_edit",
        "user_initiated_interaction_count": 60,
        "loc_added_sum": 250
      }
    ],

    "used_agent": true,
    "used_chat": true,

    "loc_suggested_to_add_sum": 500,
    "loc_added_sum": 850
  }
]
```

**Field Mappings:**

| Augment CSV | Copilot JSON |
|-------------|--------------|
| Completions | `code_generation_activity_count` |
| Accepted Completions | `code_acceptance_activity_count` |
| Chat Messages | `chat_panel.user_initiated_interaction_count` |
| Agent Messages (all types) | `agent_edit.user_initiated_interaction_count` |
| Completion Lines of Code | `code_completion.loc_added_sum` |
| Agent Lines of Code (all types) | `agent_edit.loc_added_sum` |
| Total Modified Lines of Code | `loc_added_sum` (root) |

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
| `ENTERPRISE_ID` | `283613` | GitHub Enterprise ID for Copilot JSON conversion |
| `REQUEST_TIMEOUT_SECONDS` | `30` | HTTP request timeout |
| `MAX_RETRIES` | `3` | Maximum retry attempts for failed requests |
| `RETRY_BACKOFF_SECONDS` | `0.5` | Initial backoff delay for retries (exponential) |

## Copilot JSON Conversion

The `--last-28-days` mode automatically converts Augment CSV metrics to GitHub Copilot Metrics API format. This enables:

- **Compatibility** with GitHub Copilot analytics tools
- **Standardized format** for cross-platform metrics comparison
- **Per-user daily records** matching Copilot's schema

### Conversion Details

The converter (`copilot_converter.py`) implements the mapping defined in `CSV_TO_JSON_MAPPING.md`:

1. **User Identification**: Generates numeric user IDs from email addresses using MD5 hash
2. **Feature Breakdown**: Maps metrics to three Copilot features:
   - `code_completion`: Code completions and acceptances
   - `chat_panel`: Chat interactions
   - `agent_edit`: Agent-assisted code modifications
3. **Lines of Code**: Tracks suggested and accepted LOC at both root and feature levels
4. **Boolean Flags**: Sets `used_agent` and `used_chat` based on activity
5. **Date Handling**: Uses report end date as the `day` field

### Customizing Enterprise ID

Set your GitHub Enterprise ID in `.env`:

```bash
ENTERPRISE_ID=your-enterprise-id
```

This ID appears in all generated Copilot JSON files.

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

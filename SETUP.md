# Setup Guide

## Quick Start

### 1. Clone and setup environment

```bash
cd dashboard-scraper
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Create `.env` from the example:

```bash
cp .env.example .env
```

Edit `.env` with your API base URL if it's different than the default value below:

```bash
METRICS_API_BASE_URL=https://app.augmentcode.com/
```

### 3. Authenticate with cookie

Run the interactive authentication flow:

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

The cookie will be stored securely in `secrets/cookies.json`.

### 4. Test the scraper

```bash
python -m dashboard_scraper
```

This fetches the last 30 days of metrics and writes to `data/metrics_YYYYMMDD.csv`.

### 5. Verify output

```bash
ls -lh data/
head data/metrics_*.csv
```

## API Endpoint Configuration

The only required configuration is the base URL in `.env`:

```bash
METRICS_API_BASE_URL=https://app.augmentcode.com/
```

The API endpoint paths are configured with sensible defaults. If you need to customize them, you can override these environment variables:

```bash
USER_FEATURE_STATS_ENDPOINT=/api/user-feature-stats
TENANT_FEATURE_STATS_ENDPOINT=/api/tenant-feature-stats
TENANT_MAU_ENDPOINT=/api/tenant-monthly-active-users
```

Use the helper scripts to discover your actual API endpoints if needed:

```bash
python scripts/discover_api.py
```

## Pagination Support

The client automatically handles pagination for these common patterns:

1. **Cursor-based with `next` URL**:
   ```json
   {
     "items": [...],
     "next": "https://api.example.com/metrics?cursor=abc123"
   }
   ```

2. **Page-based with nested pagination**:
   ```json
   {
     "data": [...],
     "pagination": {
       "next": "https://api.example.com/metrics?page=2"
     }
   }
   ```

3. **Simple array response** (no pagination):
   ```json
   [...]
   ```

If your API uses a different pagination scheme, you may need to customize `src/dashboard_scraper/client.py`.

## Troubleshooting

### "No module named 'dashboard_scraper'"

Ensure you're in the project root and the virtual environment is activated:

```bash
source .venv/bin/activate
python -m dashboard_scraper --help
```

### "No valid cookie and interactive auth disabled"

You need to authenticate first:

```bash
python -m dashboard_scraper --auth
```

### "Failed to load cookie"

The cookie file may be corrupted or expired. Delete and re-authenticate:

```bash
rm secrets/cookies.json
python -m dashboard_scraper --auth
```

### Empty CSV or no data

- Verify the API endpoint is correct
- Ensure your session cookie is still valid (try logging into the dashboard manually)
- Ensure there's data in the 30-day window
- Run with debug logging to inspect API responses:

```bash
python -m dashboard_scraper --log-level DEBUG
```

### API returns 403 Forbidden

Your session cookie may have expired or lack permissions. Try:

1. Re-authenticate with `--auth` to get a fresh cookie
2. Verify your user account has permissions to access the metrics data
3. Check if you need to be logged in as an admin user

## Running Tests

```bash
pip install -e ".[dev]"
pytest -v
```

## Production Deployment

### Cron Setup

1. Create a dedicated user or use an existing service account
2. Clone the repo and set up the virtual environment
3. Authenticate once interactively (tokens will be reused)
4. Add to crontab:

```bash
crontab -e
```

Example: Run daily at 1:05 AM UTC:

```cron
5 1 * * * cd /opt/dashboard-scraper && /opt/dashboard-scraper/.venv/bin/python -m dashboard_scraper >> /var/log/dashboard_scraper.log 2>&1
```

### Environment Variables in Cron

Cron has a minimal environment. Either:

1. **Use `.env` file** (recommended): Ensure `.env` is in the project root
2. **Set variables in crontab**:

```cron
METRICS_API_BASE_URL=https://app.augmentcode.com/
5 1 * * * cd /opt/dashboard-scraper && .venv/bin/python -m dashboard_scraper
```

### Log Rotation

Configure logrotate for `/var/log/dashboard_scraper.log`:

```
/var/log/dashboard_scraper.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
}
```

### Monitoring

Monitor for:

- **Exit codes**: Non-zero indicates failure
- **Empty CSV files**: May indicate API issues or auth problems
- **Log errors**: Check for 401/403/500 errors

Example monitoring script:

```bash
#!/bin/bash
OUTPUT=$(python -m dashboard_scraper 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "Dashboard scraper failed with exit code $EXIT_CODE"
    echo "$OUTPUT"
    # Send alert (email, Slack, PagerDuty, etc.)
fi
```

## Next Steps

- Customize CSV column ordering in `src/dashboard_scraper/export.py`
- Add additional metrics endpoints if needed
- Implement data validation or post-processing
- Set up automated data pipeline (e.g., upload to S3, load into database)


# Architecture Documentation

## Overview

The dashboard-scraper is a Python-based tool that extracts usage metrics from a dashboard API using cookie-based authentication and exports the data to CSV format. It's designed to run as a daily scheduled job, fetching a rolling 30-day window of metrics.

## Design Principles

This implementation follows the architectural patterns established in the `docs-scraper` reference repository:

1. **Separation of concerns**: Each module has a single, well-defined responsibility
2. **Configuration-driven**: All settings externalized via environment variables
3. **Resilient by default**: Automatic retries and graceful error handling
4. **Observable**: Structured logging with configurable levels
5. **Testable**: Pure functions and dependency injection for easy testing

## Module Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                    (CLI Entrypoint)                          │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──> config.py (Settings)
             │
             ├──> logging_config.py (Setup)
             │
             ├──> cookie_auth.py (Cookie management)
             │      │
             │      └──> Cookie persistence & loading
             │
             ├──> http.py (HTTPClient)
             │      │
             │      ├──> Cookie injection
             │      ├──> Retry logic with backoff
             │      └──> 401 handling
             │
             ├──> client.py (DashboardClient)
             │      │
             │      └──> Pagination handling
             │
             ├──> date_utils.py (Lookback window calculation)
             │
             └──> export.py (CSV writer)
                    │
                    ├──> Nested data flattening
                    └──> Column ordering
```

## Component Details

### 1. Configuration (`config.py`)

**Responsibility**: Load and validate all application settings from environment variables.

**Key Features**:
- Uses `pydantic-settings` for type-safe configuration
- Supports `.env` file loading
- Provides helper methods for path resolution

**Settings Categories**:
- Cookie authentication configuration
- API base URL and endpoint paths
- Application behavior (lookback days, output directory)
- HTTP client settings (timeouts, retries)

### 2. Cookie Authentication (`cookie_auth.py`)

**Responsibility**: Manage cookie-based authentication.

**Key Components**:

#### `CookieAuth`
- Loads cookies from JSON file
- Provides cookies as dictionary for HTTP requests
- Validates cookie file exists and is readable

#### `interactive_cookie_setup()`
- Guides user through copying session cookie from browser
- Stores cookie securely in JSON file with restricted permissions
- Validates cookie format

**Security Features**:
- Cookies stored locally with file system permissions (0600)
- Clear instructions for obtaining session cookies
- Graceful error handling for expired cookies

### 3. HTTP Client (`http.py`)

**Responsibility**: Make authenticated HTTP requests with resilience.

**Key Features**:
- Cookie-based authentication
- Retry logic for transient failures (429, 5xx)
- Exponential backoff with configurable base delay
- Request timeout enforcement

**Retry Strategy**:
```
Attempt 1: Immediate
Attempt 2: Wait 0.5s
Attempt 3: Wait 1.0s
Attempt 4: Wait 2.0s (if max_retries=3)
```

### 4. Dashboard Client (`client.py`)

**Responsibility**: Interact with the dashboard metrics API.

**Key Features**:
- Constructs API URLs from base + endpoint
- Handles multiple pagination patterns:
  - Cursor-based: `{items: [...], next: "url"}`
  - Nested pagination: `{data: [...], pagination: {next: "url"}}`
  - Simple array: `[...]` (no pagination)
- Yields metrics incrementally (memory-efficient for large datasets)

**Pagination Logic**:
1. Make initial request with `start`, `end`, `limit` parameters
2. Parse response to extract items and next URL
3. Yield each item
4. Follow `next` URL if present
5. Repeat until no more pages

### 5. Date Utilities (`date_utils.py`)

**Responsibility**: Calculate date ranges and format timestamps.

**Functions**:
- `compute_lookback_window(days, now)`: Returns (start, end) tuple for past N days
- `isoformat_utc(dt)`: Formats datetime as ISO 8601 UTC string

**Design Notes**:
- All datetimes are timezone-aware (UTC)
- Lookback window is half-open: `[start, end)`
- Microseconds stripped for cleaner output

### 6. Export (`export.py`)

**Responsibility**: Transform API responses to CSV format.

**Key Features**:

#### Flattening
- Nested dicts: `{user: {id: "123"}}` → `{user.id: "123"}`
- Lists: `{tags: ["a", "b"]}` → `{tags: "[\"a\",\"b\"]"}` (JSON string)
- Preserves primitive types

#### Column Ordering
- Priority fields first: `timestamp`, `date`, `user_id`, `email`, `metric`, `value`
- Remaining fields alphabetically sorted
- Ensures consistent CSV structure across runs

#### Timestamp Normalization
- Converts Unix timestamps to ISO 8601 UTC
- Handles both integer and float timestamps

### 7. Main CLI (`main.py`)

**Responsibility**: Provide command-line interface and orchestrate execution.

**Commands**:
- `--auth`: Interactive cookie setup
- `--start` / `--end`: Custom date range
- `--out`: Custom output filename
- `--log-level`: Override log level

**Execution Flow**:
1. Parse arguments
2. Load settings from environment
3. Setup logging
4. Initialize auth and HTTP client
5. Authenticate (interactive if `--auth`, otherwise use stored cookies)
6. Calculate date range (custom or 30-day default)
7. Fetch metrics via client
8. Write to CSV
9. Print output path

## Data Flow

```
┌──────────────┐
│ User invokes │
│  CLI command │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Load config      │
│ from .env        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Load cookies     │
│ from file        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Calculate date   │
│ range (30 days)  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐     ┌─────────────────┐
│ Fetch metrics    │────>│ Handle          │
│ from API         │     │ pagination      │
└──────┬───────────┘     └─────────────────┘
       │
       ▼
┌──────────────────┐     ┌─────────────────┐
│ Flatten nested   │────>│ Order columns   │
│ data structures  │     │ consistently    │
└──────┬───────────┘     └─────────────────┘
       │
       ▼
┌──────────────────┐
│ Write CSV to     │
│ data/ directory  │
└──────────────────┘
```

## Error Handling Strategy

### Transient Errors (Retryable)
- **429 Too Many Requests**: Exponential backoff
- **5xx Server Errors**: Exponential backoff
- **Network timeouts**: Exponential backoff

### Authentication Errors
- **401 Unauthorized**: Cookie expired or invalid, user must re-authenticate with `--auth`
- **403 Forbidden**: Fail immediately (insufficient permissions)

### Configuration Errors
- **Missing .env**: Fail with clear error message
- **Missing cookies**: Fail with instructions to run `--auth`

### Data Errors
- **Empty response**: Log warning, write empty CSV
- **Malformed JSON**: Fail with parse error
- **Unexpected pagination format**: Log warning, attempt best-effort parsing

## Security Considerations

### Cookie Storage
- Cookies stored in `secrets/cookies.json` (gitignored)
- File permissions should be restricted (600)
- Consider encrypting cookies at rest for production

### Session Management
- Session cookies may expire and need to be refreshed
- Users should re-run `--auth` when cookies expire
- Monitor for 401 errors indicating expired sessions

### Secrets Management
- Never commit `.env` or `secrets/` to version control
- Use environment variables or secret management service in production
- Regularly refresh session cookies

## Performance Characteristics

### Memory Usage
- **Streaming design**: Metrics yielded one at a time
- **CSV buffering**: All rows held in memory before write (trade-off for column ordering)
- **Typical footprint**: <100MB for 100K rows

### Network Efficiency
- **Pagination**: Fetches data in chunks (default 500 items/page)
- **Connection reuse**: `requests.Session` for HTTP connection pooling
- **Timeouts**: 30-second default prevents hanging

### Execution Time
- **Typical run**: 10-60 seconds for 30 days of data
- **Factors**: API response time, pagination depth, network latency

## Testing Strategy

### Unit Tests
- `test_date_utils.py`: Date range calculations, ISO formatting
- `test_export.py`: Flattening, column ordering, CSV writing

### Integration Tests (Future)
- Mock API server for pagination testing
- End-to-end test with fixture data

### Manual Testing
- Run with `--auth` to verify cookie setup flow
- Run with `--log-level DEBUG` to inspect API calls
- Verify CSV output structure and content

## Deployment Considerations

### Environment Requirements
- Python 3.9+
- Network access to API endpoints
- Write permissions for `data/` and `secrets/` directories

### Cron Setup
- Use `scripts/run_scraper.sh` wrapper for robust execution
- Configure log rotation for `/var/log/dashboard_scraper.log`
- Monitor exit codes and log errors

### Monitoring
- Track CSV file sizes and row counts
- Alert on consecutive failures
- Monitor for 401 errors indicating expired cookies

## Future Enhancements

### Potential Improvements
1. **Incremental fetching**: Store last fetch timestamp, only fetch new data
2. **Data validation**: Schema validation for API responses
3. **Multiple output formats**: JSON, Parquet, database insert
4. **Parallel fetching**: Concurrent requests for date ranges
5. **Metrics aggregation**: Pre-compute summaries before export
6. **Webhook notifications**: Slack/email on completion or failure
7. **Cloud storage**: Direct upload to S3/GCS
8. **Database integration**: Load CSV into PostgreSQL/BigQuery

### Extensibility Points
- **Custom exporters**: Subclass or replace `export.py`
- **Additional clients**: Add modules for other dashboard endpoints
- **Post-processing**: Add pipeline stages after CSV generation
- **Authentication methods**: Support API keys, service accounts

## Comparison to docs-scraper

### Similarities
- Modular architecture with separation of concerns
- Pydantic-based configuration
- Structured logging
- Retry logic with exponential backoff
- CLI-based execution

### Differences
- **Authentication**: Cookie-based (vs. API key or basic auth)
- **Data source**: REST API (vs. HTML scraping)
- **Output format**: CSV (vs. JSON or database)
- **Pagination**: API-based (vs. page navigation)

## Maintenance

### Regular Tasks
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Refresh session cookies when they expire: Run `--auth`
- Review logs for errors or warnings
- Validate CSV output structure

### Troubleshooting
- Check logs: `/var/log/dashboard_scraper.log`
- Verify cookie validity: `cat secrets/cookies.json`
- Test API manually: `curl -b secrets/cookies.json $API_URL`
- Run with debug logging: `--log-level DEBUG`


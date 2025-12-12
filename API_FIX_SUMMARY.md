# API Date Parameter Fix

## Problem

The API calls were failing because the JSON date parameters had spaces in them.

### Before (Incorrect)
```
{"year": 2025, "month": 10, "day": 21}
```
URL-encoded:
```
%7B%22year%22%3A%202025%2C%20%22month%22%3A%2010%2C%20%22day%22%3A%2021%7D
```

### After (Correct)
```
{"year":2025,"month":10,"day":21}
```
URL-encoded:
```
%7B%22year%22%3A2025%2C%22month%22%3A10%2C%22day%22%3A21%7D
```

## Root Cause

Python's `json.dumps()` by default adds spaces after colons and commas for readability:
```python
json.dumps({"year": 2025, "month": 10, "day": 21})
# Output: '{"year": 2025, "month": 10, "day": 21}'
```

The API expects compact JSON without spaces.

## Solution

Use the `separators` parameter to remove spaces:
```python
json.dumps(date_obj, separators=(',', ':'))
# Output: '{"year":2025,"month":10,"day":21}'
```

## Code Change

**File**: `src/dashboard_scraper/client.py`

```python
def _format_date_param(self, dt: datetime) -> str:
    """
    Format datetime as URL-encoded JSON for the API.
    API expects: {"year":2025,"month":10,"day":22} (no spaces)
    """
    date_obj = {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day
    }
    # Use separators to remove spaces from JSON
    return quote(json.dumps(date_obj, separators=(',', ':')))
```

## Testing

### Example URLs Generated

#### Single Date (Oct 21, 2025)
```
https://app.augmentcode.com/api/user-feature-stats?startDate=%7B%22year%22%3A2025%2C%22month%22%3A10%2C%22day%22%3A21%7D&endDate=%7B%22year%22%3A2025%2C%22month%22%3A10%2C%22day%22%3A21%7D
```
Decoded: `startDate={"year":2025,"month":10,"day":21}&endDate={"year":2025,"month":10,"day":21}`

#### Date Range (Oct 20-21, 2025)
```
https://app.augmentcode.com/api/user-feature-stats?startDate=%7B%22year%22%3A2025%2C%22month%22%3A10%2C%22day%22%3A20%7D&endDate=%7B%22year%22%3A2025%2C%22month%22%3A10%2C%22day%22%3A21%7D
```
Decoded: `startDate={"year":2025,"month":10,"day":20}&endDate={"year":2025,"month":10,"day":21}`

## Verification

Compare with the working URLs from the browser DevTools:
```
https://app.augmentcode.com/api/user-feature-stats?startDate=%7B%22year%22%3A2025%2C%22month%22%3A9%2C%22day%22%3A22%7D&endDate=%7B%22year%22%3A2025%2C%22month%22%3A10%2C%22day%22%3A22%7D
```
Decoded: `startDate={"year":2025,"month":9,"day":22}&endDate={"year":2025,"month":10,"day":22}`

✅ Format matches exactly!

## Impact

This fix should resolve the empty CSV files issue. The API should now return data for:
- Single date queries
- Date range queries
- Today queries

## Next Steps

Test the scraper with the fixed date formatting:
```bash
# Single date
python -m dashboard_scraper 10-21-2025

# Date range
python -m dashboard_scraper 10-20-2025 10-21-2025

# Today
python -m dashboard_scraper 10-22-2025
```


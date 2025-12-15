# Aggregated Metrics Feature

## Overview

The `--last-28-days` feature now generates **both** daily JSON files and a **single aggregated JSON file** that combines metrics across all 28 days.

## What's New

### New File: `copilot_metrics_aggregated.json`

This is the **main output file** that aggregates all 28 days of metrics into a single file with per-user records.

**Location:** `data/daily_exports_<date-range>/copilot_metrics_aggregated.json`

### How Aggregation Works

The aggregator (`src/dashboard_scraper/copilot_aggregator.py`):

1. **Reads all 28 daily JSON files**
2. **Groups records by user** (`user_login`)
3. **Sums metrics** across all days for each user:
   - `user_initiated_interaction_count`
   - `code_generation_activity_count`
   - `code_acceptance_activity_count`
   - `loc_suggested_to_add_sum`
   - `loc_added_sum`
   - All metrics in `totals_by_feature` array
4. **Combines boolean flags** using OR logic:
   - `used_agent` = true if user used agent on ANY day
   - `used_chat` = true if user used chat on ANY day
5. **Writes a single consolidated JSON file**

## Output Format

The aggregated file matches the GitHub Copilot Metrics API schema:

```json
[
  {
    "report_start_day": "2024-11-17",
    "report_end_day": "2024-12-14",
    "day": "2024-12-14",
    "enterprise_id": "283613",
    "user_id": 12345,
    "user_login": "user@example.com",
    "user_initiated_interaction_count": 150,
    "code_generation_activity_count": 500,
    "code_acceptance_activity_count": 400,
    "totals_by_feature": [
      {
        "feature": "code_completion",
        "user_initiated_interaction_count": 0,
        "code_generation_activity_count": 500,
        "code_acceptance_activity_count": 400,
        "loc_suggested_to_add_sum": 2000,
        "loc_suggested_to_delete_sum": 0,
        "loc_added_sum": 2000,
        "loc_deleted_sum": 0
      },
      {
        "feature": "chat_panel",
        "user_initiated_interaction_count": 75,
        "code_generation_activity_count": 0,
        "code_acceptance_activity_count": 0,
        "loc_suggested_to_add_sum": 0,
        "loc_suggested_to_delete_sum": 0,
        "loc_added_sum": 0,
        "loc_deleted_sum": 0
      },
      {
        "feature": "agent_edit",
        "user_initiated_interaction_count": 75,
        "code_generation_activity_count": 0,
        "code_acceptance_activity_count": 0,
        "loc_suggested_to_add_sum": 0,
        "loc_suggested_to_delete_sum": 0,
        "loc_added_sum": 1500,
        "loc_deleted_sum": 0
      }
    ],
    "used_agent": true,
    "used_chat": true,
    "loc_suggested_to_add_sum": 2000,
    "loc_suggested_to_delete_sum": 0,
    "loc_added_sum": 3500,
    "loc_deleted_sum": 0
  }
]
```

## Files Generated

When you run `python -m dashboard_scraper --last-28-days`, you get:

```
data/daily_exports_2024-11-17_to_2024-12-14/
├── augment_metrics_2024-11-17.csv          # Daily CSV (Augment format)
├── copilot_metrics_2024-11-17.json         # Daily JSON (Copilot format)
├── augment_metrics_2024-11-18.csv
├── copilot_metrics_2024-11-18.json
│   ... (26 more days)
├── augment_metrics_2024-12-14.csv
├── copilot_metrics_2024-12-14.json
└── copilot_metrics_aggregated.json         ⭐ MAIN OUTPUT (all 28 days combined)
```

## Use Cases

### Daily Files
- **Per-day analysis**: Track daily trends and patterns
- **Debugging**: Identify which specific days had issues
- **Granular reporting**: Show day-by-day breakdowns

### Aggregated File
- **Overall metrics**: Total activity across the 28-day period
- **User summaries**: Complete picture of each user's activity
- **Copilot compatibility**: Matches the expected Copilot Metrics API format
- **Easier consumption**: Single file instead of 28 separate files

## Example: Viewing the Aggregated File

```bash
# Pretty-print the aggregated file
python3 -m json.tool data/daily_exports_*/copilot_metrics_aggregated.json

# Count total users
jq 'length' data/daily_exports_*/copilot_metrics_aggregated.json

# View a specific user's metrics
jq '.[] | select(.user_login == "user@example.com")' data/daily_exports_*/copilot_metrics_aggregated.json

# Get total completions across all users
jq '[.[].code_generation_activity_count] | add' data/daily_exports_*/copilot_metrics_aggregated.json
```

## Testing

Run the aggregation test to verify it works correctly:

```bash
source .venv/bin/activate
python test_aggregation.py
```

This creates sample data and verifies that metrics are correctly summed across multiple days.

## Implementation Details

- **Module**: `src/dashboard_scraper/copilot_aggregator.py`
- **Function**: `aggregate_daily_json_files()`
- **Integration**: Called automatically in `process_last_28_days()` after daily files are generated
- **Error handling**: Continues processing even if some daily files fail to read
- **Logging**: Full logging of aggregation process

## Schema Compliance

The aggregated file matches the GitHub Copilot Metrics API schema as documented in `copilot_dailyy_schema.txt`, including:

- ✅ All required fields
- ✅ Correct data types
- ✅ Proper structure for `totals_by_feature` array
- ✅ Boolean flags for `used_agent` and `used_chat`
- ✅ Summed metrics across all days


# Testing Guide for `--last-28-days` Feature

## ✅ Setup Complete!

The virtual environment is set up and all dependencies are installed. You're ready to test!

## 🚀 How to Run and Test

### Step 1: Activate Virtual Environment

Every time you open a new terminal, activate the virtual environment:

```bash
source .venv/bin/activate
```

### Step 2: Set Up Authentication (One-Time)

If you haven't already set up authentication:

```bash
python -m dashboard_scraper --auth
```

**How to get your session cookie:**
1. Open your dashboard URL in your browser
2. Log in with your credentials
3. Open DevTools (F12 or Cmd+Option+I)
4. Go to: Application → Cookies → [your dashboard URL]
5. Find the `_session` cookie
6. Copy the **Value** (it should be a long string)
7. Paste it when prompted (format: `_session=<your-cookie-value>`)

### Step 3: Test the `--last-28-days` Feature

```bash
python -m dashboard_scraper --last-28-days
```

**What this does:**
1. Calculates date range: 28 days ago (at 00:00:00) to yesterday (at 23:59:59)
2. Fetches metrics for each of the 28 days individually
3. Generates 28 CSV files (one per day) in Augment format
4. Converts each CSV to Copilot JSON format
5. Creates 28 JSON files (one per day) in Copilot format
6. **Aggregates all 28 days into a single consolidated JSON file**
7. Organizes everything in a dated directory

**Expected output:**
```
================================================================================
🚀 Starting 28-day metrics processing
================================================================================
Date range: 2024-11-17 to 2024-12-14
Total days to process: 28

Output directory: data/daily_exports_2024-11-17_to_2024-12-14

📅 Processing day 1 of 28: 2024-11-17
   ✅ Fetched 45 records
   📄 Wrote CSV: augment_metrics_2024-11-17.csv

📅 Processing day 2 of 28: 2024-11-18
   ✅ Fetched 42 records
   📄 Wrote CSV: augment_metrics_2024-11-18.csv

... (continues for all 28 days)

================================================================================
📄 Converting CSV to Copilot JSON format
================================================================================
✅ augment_metrics_2024-11-17.csv -> copilot_metrics_2024-11-17.json (45 users)
✅ augment_metrics_2024-11-18.csv -> copilot_metrics_2024-11-18.json (42 users)
... (continues for all 28 days)

================================================================================
📊 Aggregating metrics across all days
================================================================================
✅ Created aggregated metrics file: copilot_metrics_aggregated.json
   Total unique users: 45

================================================================================
📊 Final Summary
================================================================================
Total days processed: 28
Successful: 28
Failed: 0
CSV files generated: 28
JSON files generated: 28

✅ Processing complete!
📁 Output directory: data/daily_exports_2024-11-17_to_2024-12-14

Files generated:
  - 28 CSV files (Augment format)
  - 28 JSON files (Copilot format)
  - 1 aggregated JSON file (copilot_metrics_aggregated.json)
```

### Step 4: Verify the Output

Check the generated files:

```bash
# List the output directory
ls -lh data/daily_exports_*/

# View a sample CSV file
head -20 data/daily_exports_*/augment_metrics_2024-*.csv | head -20

# View a sample JSON file (pretty-printed)
python3 -m json.tool data/daily_exports_*/copilot_metrics_2024-*.json | head -50
```

## 📊 Output Structure

```
data/
└── daily_exports_2024-11-17_to_2024-12-14/
    ├── augment_metrics_2024-11-17.csv
    ├── copilot_metrics_2024-11-17.json
    ├── augment_metrics_2024-11-18.csv
    ├── copilot_metrics_2024-11-18.json
    │   ... (26 more days)
    ├── augment_metrics_2024-12-14.csv
    ├── copilot_metrics_2024-12-14.json
    └── copilot_metrics_aggregated.json  ⭐ Main output file
```

## 🧪 Additional Tests

### Test 1: Check Help Text

```bash
python -m dashboard_scraper --help
```

Should show the `--last-28-days` option.

### Test 2: Test Mutual Exclusivity

```bash
python -m dashboard_scraper --last-28-days 10-20-2025
```

Should error with: "Cannot use --last-28-days with manual date arguments"

### Test 3: Verify JSON Schema

```bash
# Install jq for JSON validation (optional)
brew install jq

# View the aggregated file (main output)
jq '.[0]' data/daily_exports_*/copilot_metrics_aggregated.json

# Validate daily JSON structure
jq '.[0]' data/daily_exports_*/copilot_metrics_2024-*.json | head -1
```

### Test 4: Run Existing Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v
```

## 🐛 Troubleshooting

### Issue: "Authentication expired"
**Solution:** Re-run authentication setup:
```bash
python -m dashboard_scraper --auth
```

### Issue: "No module named 'dashboard_scraper'"
**Solution:** Make sure virtual environment is activated:
```bash
source .venv/bin/activate
```

### Issue: Empty or missing data
**Solution:** Check your date range and API access. The feature fetches data for 28 days ago to yesterday, so today's data is not included.

## 📝 Configuration

Edit `.env` to customize:

```bash
# Your GitHub Enterprise ID for Copilot JSON conversion
ENTERPRISE_ID=283613

# Output directory
EXPORT_DIR=data

# Log level (DEBUG for more verbose output)
LOG_LEVEL=INFO
```

## ✅ Success Criteria

The feature is working correctly if:
1. ✅ All 28 days are processed without errors
2. ✅ 28 CSV files are generated
3. ✅ 28 JSON files are generated
4. ✅ JSON files contain valid Copilot schema
5. ✅ User counts match between CSV and JSON
6. ✅ No authentication errors


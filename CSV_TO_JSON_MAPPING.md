# Augment CSV to Copilot Per-User JSON Mapping

## Overview

This document shows how to map Augment CSV data to the **OFFICIAL per-user** GitHub Copilot metrics format (from the `users-28-day/latest` endpoint).

## Important Context

- **Source**: Augment CSV with per-user cumulative metrics
- **Target**: Copilot per-user JSON format (per-user, per-day records)
- **Schema Source**: `copilot_dailyy_schema.txt` (official schema)
- **Key Challenge**: Augment CSV has cumulative data; Copilot expects daily granularity

**Critical Schema Notes:**
- Use `"ide"` not `"name"` in `totals_by_ide`
- Use `"feature"` not `"name"` in `totals_by_feature`
- No separate `agent_edit` object - it's a feature in `totals_by_feature`
- Version tracking is within `totals_by_ide`, not at root level
- Add `used_agent` and `used_chat` boolean flags at root level

## CSV Columns to Copilot Fields Mapping

| CSV Column | Copilot Field(s) | Direct Match? | Notes |
|------------|-----------------|---------------|-------|
| User | `user_login` | ✅ Yes | Map user email/name to username |
| First Seen | N/A | ❌ No | Not in Copilot format |
| Last Seen | `day` (conceptually) | ⚠️ Partial | Could use as the reporting day |
| Active Days | N/A | ❌ No | Not in Copilot per-user format |
| Completions | `code_generation_activity_count` (partial) | ⚠️ Partial | Copilot includes all outputs |
| Accepted Completions | `code_acceptance_activity_count` | ✅ Yes | Direct mapping |
| Accept Rate | N/A | ❌ No | Copilot doesn't pre-calculate this |
| Chat Messages | `user_initiated_interaction_count` (partial) | ⚠️ Partial | Copilot includes all prompts |
| Agent Messages | `user_initiated_interaction_count` (partial), `agent_edit` feature | ⚠️ Partial | Include in user interactions and agent_edit feature |
| Remote Agent Messages | `user_initiated_interaction_count` (partial), `agent_edit` feature | ⚠️ Partial | Include in user interactions and agent_edit feature |
| Interactive CLI Agent Messages | `user_initiated_interaction_count` (partial), `agent_edit` feature | ⚠️ Partial | Include in user interactions and agent_edit feature |
| Non-Interactive CLI Agent Messages | `user_initiated_interaction_count` (partial), `agent_edit` feature | ⚠️ Partial | Include in user interactions and agent_edit feature |
| Tool Uses | N/A | ❌ No | Not in Copilot |
| Total Modified Lines of Code | `loc_added_sum` | ✅ Yes | Total lines added |
| Completion Lines of Code | `loc_suggested_to_add_sum` | ✅ Yes | Lines suggested via completions |
| Instruction Lines of Code | N/A | ❌ No | Excluded - not mapped to Copilot |
| Agent Lines of Code | `loc_added_sum` (root), `agent_edit.loc_added_sum` | ✅ Yes | Include in total and agent_edit feature |
| Remote Agent Lines of Code | `loc_added_sum` (root), `agent_edit.loc_added_sum` | ✅ Yes | Include in total and agent_edit feature |
| CLI Agent Lines of Code | `loc_added_sum` (root), `agent_edit.loc_added_sum` | ✅ Yes | Include in total and agent_edit feature |

---

## Mapping Strategy

### Option 1: Per-User Records (Recommended)
Create one JSON record per user, mapping cumulative CSV data to a single day.

```javascript
// For each user in CSV
for (user in csv_data) {
  copilot_record = {
    "report_start_day": "2024-11-14",  // Start of your reporting period
    "report_end_day": "2024-12-11",    // End of your reporting period
    "day": "2024-12-11",                // Use end date as the reporting day
    "enterprise_id": "your-enterprise-id",
    "user_id": generate_user_id(user.User),
    "user_login": user.User,

    // Activity counts
    "user_initiated_interaction_count": user.ChatMessages,  // Approximate
    "code_generation_activity_count": user.Completions,     // Approximate
    "code_acceptance_activity_count": user.AcceptedCompletions,

    // Boolean flags
    "used_agent": user.AgentMessages > 0 || user.RemoteAgentMessages > 0 || user.InteractiveCLIAgentMessages > 0 || user.NonInteractiveCLIAgentMessages > 0,
    "used_chat": user.ChatMessages > 0,

    // Lines of code (root level)
    "loc_suggested_to_add_sum": user.CompletionLinesOfCode,
    "loc_suggested_to_delete_sum": 0,  // Not tracked in Augment
    "loc_added_sum": user.TotalModifiedLinesOfCode,
    "loc_deleted_sum": 0,  // Not tracked in Augment

    // Feature breakdown (conceptual mapping)
    "totals_by_feature": [
      {
        "feature": "code_completion",  // NOTE: "feature" not "name"!
        "user_initiated_interaction_count": 0,
        "code_generation_activity_count": user.Completions,
        "code_acceptance_activity_count": user.AcceptedCompletions,
        "loc_suggested_to_add_sum": user.CompletionLinesOfCode,
        "loc_suggested_to_delete_sum": 0,
        "loc_added_sum": user.CompletionLinesOfCode,
        "loc_deleted_sum": 0
      },
      {
        "feature": "chat_panel",  // NOTE: "feature" not "name"!
        "user_initiated_interaction_count": user.ChatMessages,
        "code_generation_activity_count": 0,  // Not tracked separately
        "code_acceptance_activity_count": 0,
        "loc_suggested_to_add_sum": 0,
        "loc_suggested_to_delete_sum": 0,
        "loc_added_sum": 0,
        "loc_deleted_sum": 0
      },
      {
        "feature": "agent_edit",  // NOTE: "feature" not "name"!
        "user_initiated_interaction_count": user.AgentMessages + user.RemoteAgentMessages + user.InteractiveCLIAgentMessages + user.NonInteractiveCLIAgentMessages,
        "code_generation_activity_count": 0,  // Not tracked separately
        "code_acceptance_activity_count": 0,
        "loc_suggested_to_add_sum": 0,
        "loc_suggested_to_delete_sum": 0,
        "loc_added_sum": user.AgentLinesOfCode + user.RemoteAgentLinesOfCode + user.CLIAgentLinesOfCode,
        "loc_deleted_sum": 0
      }
    ]
  }
}
```

### Option 2: Daily Distribution (Advanced)
If you have historical snapshots, calculate daily deltas:

```javascript
// Calculate daily changes
for (day in date_range) {
  for (user in users) {
    daily_delta = snapshot[day][user] - snapshot[day-1][user]

    copilot_record = {
      "day": day,
      "user_login": user,
      "code_acceptance_activity_count": daily_delta.AcceptedCompletions,
      "loc_added_sum": daily_delta.TotalModifiedLinesOfCode,
      // ... etc
    }
  }
}
```

---

## Field Calculation Formulas

### Core Activity Metrics

```javascript
// User identification
user_login = csv.User
user_id = generate_or_map_user_id(csv.User)

// Activity counts (approximate mapping)
user_initiated_interaction_count = csv.ChatMessages + csv.AgentMessages + csv.RemoteAgentMessages + csv.InteractiveCLIAgentMessages + csv.NonInteractiveCLIAgentMessages
code_generation_activity_count = csv.Completions
code_acceptance_activity_count = csv.AcceptedCompletions

// Boolean flags
used_agent = csv.AgentMessages > 0 || csv.RemoteAgentMessages > 0 || csv.InteractiveCLIAgentMessages > 0 || csv.NonInteractiveCLIAgentMessages > 0
used_chat = csv.ChatMessages > 0

// Lines of code (root level)
loc_suggested_to_add_sum = csv.CompletionLinesOfCode
loc_suggested_to_delete_sum = 0  // Not tracked in Augment
loc_added_sum = csv.TotalModifiedLinesOfCode
loc_deleted_sum = 0  // Not tracked in Augment
```

### Feature Breakdown (Conceptual)

```javascript
// Code completion feature
feature_code_completion = {
  feature: "code_completion",  // NOTE: "feature" not "name"!
  user_initiated_interaction_count: 0,
  code_generation_activity_count: csv.Completions,
  code_acceptance_activity_count: csv.AcceptedCompletions,
  loc_suggested_to_add_sum: csv.CompletionLinesOfCode,
  loc_suggested_to_delete_sum: 0,
  loc_added_sum: csv.CompletionLinesOfCode,
  loc_deleted_sum: 0
}

// Chat panel feature
feature_chat_panel = {
  feature: "chat_panel",  // NOTE: "feature" not "name"!
  user_initiated_interaction_count: csv.ChatMessages,
  code_generation_activity_count: 0,
  code_acceptance_activity_count: 0,
  loc_suggested_to_add_sum: 0,
  loc_suggested_to_delete_sum: 0,
  loc_added_sum: 0,
  loc_deleted_sum: 0
}

// Agent edit feature
feature_agent_edit = {
  feature: "agent_edit",  // NOTE: "feature" not "name"!
  user_initiated_interaction_count: csv.AgentMessages + csv.RemoteAgentMessages + csv.InteractiveCLIAgentMessages + csv.NonInteractiveCLIAgentMessages,
  code_generation_activity_count: 0,
  code_acceptance_activity_count: 0,
  loc_suggested_to_add_sum: 0,
  loc_suggested_to_delete_sum: 0,
  loc_added_sum: csv.AgentLinesOfCode + csv.RemoteAgentLinesOfCode + csv.CLIAgentLinesOfCode,
  loc_deleted_sum: 0
}
```

---

## Example: CSV Row to Copilot JSON

### Input CSV Row
```csv
user@example.com,2024-11-14,2024-12-11,28,450,180,40.0,25,50,10,5,8,120,850,500,15,200,50,85
```

### Output Copilot JSON (Official Schema)
```json
{
  "report_start_day": "2024-11-14",
  "report_end_day": "2024-12-11",
  "day": "2024-12-11",
  "enterprise_id": "283613",
  "user_id": 12345,
  "user_login": "user@example.com",

  "user_initiated_interaction_count": 25,
  "code_generation_activity_count": 450,
  "code_acceptance_activity_count": 180,

  "totals_by_feature": [
    {
      "feature": "code_completion",
      "user_initiated_interaction_count": 0,
      "code_generation_activity_count": 450,
      "code_acceptance_activity_count": 180,
      "loc_suggested_to_add_sum": 500,
      "loc_suggested_to_delete_sum": 0,
      "loc_added_sum": 500,
      "loc_deleted_sum": 0
    },
    {
      "feature": "chat_panel",
      "user_initiated_interaction_count": 25,
      "code_generation_activity_count": 0,
      "code_acceptance_activity_count": 0,
      "loc_suggested_to_add_sum": 0,
      "loc_suggested_to_delete_sum": 0,
      "loc_added_sum": 0,
      "loc_deleted_sum": 0
    },
    {
      "feature": "agent_edit",
      "user_initiated_interaction_count": 60,
      "code_generation_activity_count": 0,
      "code_acceptance_activity_count": 0,
      "loc_suggested_to_add_sum": 0,
      "loc_suggested_to_delete_sum": 0,
      "loc_added_sum": 250,
      "loc_deleted_sum": 0
    }
  ],

  "used_agent": true,
  "used_chat": true,

  "loc_suggested_to_add_sum": 500,
  "loc_suggested_to_delete_sum": 0,
  "loc_added_sum": 850,
  "loc_deleted_sum": 0
}
```

---

## Implementation Pseudocode

```python
def csv_to_copilot_json(csv_file, report_start_day, report_end_day, enterprise_id):
    """
    Convert Augment CSV to Copilot per-user JSON format
    """
    import pandas as pd

    # Read CSV
    df = pd.read_csv(csv_file)

    # Filter out summary rows
    df = df[df['User'].notna()]
    df = df[df['User'] != '']

    # Generate JSON records
    records = []

    for index, row in df.iterrows():
        # Skip zero-activity users if desired
        if row['Active Days'] == 0:
            continue

        record = {
            "report_start_day": report_start_day,
            "report_end_day": report_end_day,
            "day": report_end_day,  # Use end date as reporting day
            "enterprise_id": enterprise_id,
            "user_id": generate_user_id(row['User']),
            "user_login": row['User'],

            # Activity counts
            "user_initiated_interaction_count": int(row['Chat Messages']) + int(row['Agent Messages']) + int(row['Remote Agent Messages']) + int(row['Interactive CLI Agent Messages']) + int(row['Non-Interactive CLI Agent Messages']),
            "code_generation_activity_count": int(row['Completions']),
            "code_acceptance_activity_count": int(row['Accepted Completions']),

            # Feature breakdown
            "totals_by_feature": [
                {
                    "feature": "code_completion",  # NOTE: "feature" not "name"!
                    "user_initiated_interaction_count": 0,
                    "code_generation_activity_count": int(row['Completions']),
                    "code_acceptance_activity_count": int(row['Accepted Completions']),
                    "loc_suggested_to_add_sum": int(row['Completion Lines of Code']),
                    "loc_suggested_to_delete_sum": 0,
                    "loc_added_sum": int(row['Completion Lines of Code']),
                    "loc_deleted_sum": 0
                },
                {
                    "feature": "chat_panel",  # NOTE: "feature" not "name"!
                    "user_initiated_interaction_count": int(row['Chat Messages']),
                    "code_generation_activity_count": 0,
                    "code_acceptance_activity_count": 0,
                    "loc_suggested_to_add_sum": 0,
                    "loc_suggested_to_delete_sum": 0,
                    "loc_added_sum": 0,
                    "loc_deleted_sum": 0
                },
                {
                    "feature": "agent_edit",  # NOTE: "feature" not "name"!
                    "user_initiated_interaction_count": int(row['Agent Messages']) + int(row['Remote Agent Messages']) + int(row['Interactive CLI Agent Messages']) + int(row['Non-Interactive CLI Agent Messages']),
                    "code_generation_activity_count": 0,
                    "code_acceptance_activity_count": 0,
                    "loc_suggested_to_add_sum": 0,
                    "loc_suggested_to_delete_sum": 0,
                    "loc_added_sum": int(row['Agent Lines of Code']) + int(row['Remote Agent Lines of Code']) + int(row['CLI Agent Lines of Code']),
                    "loc_deleted_sum": 0
                }
            ],

            # Boolean flags
            "used_agent": int(row['Agent Messages']) > 0 or int(row['Remote Agent Messages']) > 0 or int(row['Interactive CLI Agent Messages']) > 0 or int(row['Non-Interactive CLI Agent Messages']) > 0,
            "used_chat": int(row['Chat Messages']) > 0,

            # Lines of code (root level)
            "loc_suggested_to_add_sum": int(row['Completion Lines of Code']),
            "loc_suggested_to_delete_sum": 0,
            "loc_added_sum": int(row['Total Modified Lines of Code']),
            "loc_deleted_sum": 0
        }

        records.append(record)

    return records

def generate_user_id(user_email):
    """Generate a numeric user ID from email (or use existing mapping)"""
    import hashlib
    return int(hashlib.md5(user_email.encode()).hexdigest()[:8], 16)
```

---

## Data Quality Notes

### Empty User Rows
- Filter out rows where `User` is empty or null
- These likely represent invalid data

### Zero Activity Users
- Consider excluding users with `Active Days = 0`
- Or include them but with all metrics set to 0

### Date Handling
- Use `Last Seen` as the `day` field
- Or use the end date of your reporting period
- Set `report_start_day` and `report_end_day` based on your CSV date range

### Missing Copilot Fields
Since Augment CSV doesn't have all Copilot fields:
- Set `loc_suggested_to_delete_sum` to 0
- Set `loc_deleted_sum` to 0
- Omit `totals_by_ide`, `totals_by_language_feature`, etc. if not available
- Set `last_known_ide_version` and `last_known_plugin_version` to null or omit

---

## Validation

After conversion, validate:
1. ✅ Each user has exactly one record (or 28 if doing daily distribution)
2. ✅ `code_acceptance_activity_count` matches CSV `Accepted Completions`
3. ✅ `loc_added_sum` matches CSV `Total Modified Lines of Code`
4. ✅ `agent_edit.loc_added_sum` = `Agent Lines of Code` + `Remote Agent Lines of Code`
5. ✅ All required Copilot fields are present
6. ✅ Date formats are YYYY-MM-DD


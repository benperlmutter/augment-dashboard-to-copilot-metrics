# Quick Reference Guide: Copilot Per-User Metrics Format (Official Schema)

## 📋 TL;DR

**Schema Source:** `copilot_dailyy_schema.txt` (official GitHub Copilot schema)

**What's Changed:**
- GitHub Copilot metrics are now **per-user, per-day** records (not aggregated daily totals)
- Source: `/enterprises/{enterprise}/copilot/metrics/reports/users-28-day/latest` endpoint
- Each user gets 28 daily records (one per day over 28-day period)
- Augment CSV has per-user cumulative data (simpler to map!)

**Critical Schema Details:**
1. ✅ Use `"ide"` not `"name"` in `totals_by_ide`
2. ✅ Use `"feature"` not `"name"` in `totals_by_feature`
3. ✅ No separate `agent_edit` object - it's a feature in `totals_by_feature`
4. ✅ Version tracking is within `totals_by_ide`, not at root level
5. ✅ Add `used_agent` and `used_chat` boolean flags at root level

**What to do:**
1. ✅ Map Augment CSV users to Copilot per-user JSON structure
2. 🔄 Convert cumulative metrics to Copilot's field names (use correct names!)
3. ⚠️ Handle temporal difference (cumulative vs. daily)
4. ➕ Highlight Augment-specific metrics (tool usage, CLI agent, etc.)

---

## 🎯 Quick Field Mapping

| Copilot Field | Augment CSV Column | Match? |
|---------------|-------------------|--------|
| `user_login` | `User` | ✅ Direct |
| `code_acceptance_activity_count` | `Accepted Completions` | ✅ Direct |
| `loc_suggested_to_add_sum` | `Completion Lines of Code` | ✅ Direct |
| `loc_added_sum` | `Total Modified Lines of Code` | ✅ Direct |
| `agent_edit.loc_added_sum` | `Agent Lines of Code` + `Remote Agent Lines of Code` + `CLI Agent Lines of Code` | ✅ Direct |
| `user_initiated_interaction_count` | `Chat Messages` + `Agent Messages` + `Remote Agent Messages` + `Interactive CLI Agent Messages` + `Non-Interactive CLI Agent Messages` | ✅ Direct |
| `code_generation_activity_count` | `Completions` | ⚠️ Partial |
| `loc_deleted_sum` | N/A | ❌ Not tracked |

---

## 📊 Per-User JSON Example (Official Schema)

```json
{
  "report_start_day": "2024-11-14",
  "report_end_day": "2024-12-11",
  "day": "2024-12-11",
  "enterprise_id": "283613",
  "user_id": 12345,
  "user_login": "octocat",

  "user_initiated_interaction_count": 45,
  "code_generation_activity_count": 52,
  "code_acceptance_activity_count": 38,

  "totals_by_feature": [
    {
      "feature": "code_completion",
      "user_initiated_interaction_count": 0,
      "code_generation_activity_count": 30,
      "code_acceptance_activity_count": 25,
      "loc_suggested_to_add_sum": 250,
      "loc_suggested_to_delete_sum": 0,
      "loc_added_sum": 200,
      "loc_deleted_sum": 0
    },
    {
      "feature": "chat_panel",
      "user_initiated_interaction_count": 25,
      "code_generation_activity_count": 15,
      "code_acceptance_activity_count": 10,
      "loc_suggested_to_add_sum": 180,
      "loc_suggested_to_delete_sum": 0,
      "loc_added_sum": 120,
      "loc_deleted_sum": 0
    },
    {
      "feature": "agent_edit",
      "user_initiated_interaction_count": 5,
      "code_generation_activity_count": 2,
      "code_acceptance_activity_count": 0,
      "loc_suggested_to_add_sum": 0,
      "loc_suggested_to_delete_sum": 0,
      "loc_added_sum": 85,
      "loc_deleted_sum": 12
    }
  ],

  "used_agent": true,
  "used_chat": true,

  "loc_suggested_to_add_sum": 520,
  "loc_suggested_to_delete_sum": 0,
  "loc_added_sum": 405,
  "loc_deleted_sum": 12
}
```

---

## 🔢 Quick Mapping Formulas

### CSV Row → Copilot JSON

```python
# For each user in CSV
copilot_record = {
    # User identification
    "user_login": csv.User,
    "user_id": generate_user_id(csv.User),

    # Dates
    "day": "2024-12-11",  # End date of reporting period
    "report_start_day": "2024-11-14",
    "report_end_day": "2024-12-11",

    # Activity counts
    "user_initiated_interaction_count": csv.ChatMessages + csv.AgentMessages + csv.RemoteAgentMessages + csv.InteractiveCLIAgentMessages + csv.NonInteractiveCLIAgentMessages,
    "code_generation_activity_count": csv.Completions,
    "code_acceptance_activity_count": csv.AcceptedCompletions,

    # Feature breakdown (NOTE: use "feature" not "name"!)
    "totals_by_feature": [
        {
            "feature": "code_completion",
            "code_generation_activity_count": csv.Completions,
            "code_acceptance_activity_count": csv.AcceptedCompletions,
            "loc_suggested_to_add_sum": csv.CompletionLinesOfCode,
            "loc_suggested_to_delete_sum": 0,
            "loc_added_sum": csv.CompletionLinesOfCode,
            "loc_deleted_sum": 0
        },
        {
            "feature": "agent_edit",
            "user_initiated_interaction_count": csv.AgentMessages + csv.RemoteAgentMessages + csv.InteractiveCLIAgentMessages + csv.NonInteractiveCLIAgentMessages,
            "loc_suggested_to_add_sum": 0,
            "loc_suggested_to_delete_sum": 0,
            "loc_added_sum": csv.AgentLinesOfCode + csv.RemoteAgentLinesOfCode + csv.CLIAgentLinesOfCode,
            "loc_deleted_sum": 0
        }
    ],

    # Boolean flags
    "used_agent": csv.AgentMessages > 0 or csv.RemoteAgentMessages > 0 or csv.InteractiveCLIAgentMessages > 0 or csv.NonInteractiveCLIAgentMessages > 0,
    "used_chat": csv.ChatMessages > 0,

    # Lines of code (root level)
    "loc_suggested_to_add_sum": csv.CompletionLinesOfCode,
    "loc_suggested_to_delete_sum": 0,
    "loc_added_sum": csv.TotalModifiedLinesOfCode,
    "loc_deleted_sum": 0
}
```

---

## ⚠️ Common Pitfalls

### 1. Temporal Mismatch
- **Copilot**: Daily records (28 days per user)
- **Augment**: Cumulative totals over date range
- **Solution**: Report Augment data as single day (end of period) or estimate daily distribution

### 2. Date Format
- ✅ Use: `"2024-12-11"` (YYYY-MM-DD)
- ❌ Avoid: `"12/11/2024"` or `"2024-12-11T00:00:00Z"`

### 3. Wrong Field Names (CRITICAL!)
- ❌ **WRONG**: `"name": "vscode"` in `totals_by_ide`
- ✅ **CORRECT**: `"ide": "vscode"` in `totals_by_ide`
- ❌ **WRONG**: `"name": "code_completion"` in `totals_by_feature`
- ✅ **CORRECT**: `"feature": "code_completion"` in `totals_by_feature`

### 4. Missing Fields
- Copilot has fields Augment doesn't track:
  - `loc_deleted_sum` → Set to 0
  - `loc_suggested_to_delete_sum` → Set to 0
  - `totals_by_ide` → Omit if not available
  - `totals_by_language_feature` → Omit if not available

### 5. Separate `agent_edit` Object (WRONG!)
- ❌ **WRONG**: Creating a separate `"agent_edit": {...}` object at root level
- ✅ **CORRECT**: Agent edit is a feature in `totals_by_feature` with `"feature": "agent_edit"`

### 6. User ID Generation
- Copilot uses numeric `user_id`
- Augment CSV has email/username
- **Solution**: Generate ID from email hash or use existing mapping

### 7. Activity Count Mapping
- `user_initiated_interaction_count` = `Chat Messages` + `Agent Messages` + `Remote Agent Messages` + `Interactive CLI Agent Messages` + `Non-Interactive CLI Agent Messages`
- `code_generation_activity_count` ≈ `Completions` (not exact)
- Copilot counts differently than Augment

### 8. Empty User Rows
- Filter out rows where `User` is empty
- These represent invalid data

### 9. Version Tracking Location (WRONG!)
- ❌ **WRONG**: `"last_known_ide_version": "1.85.0"` at root level
- ✅ **CORRECT**: Version tracking is within each IDE in `totals_by_ide` as objects with `sampled_at`, `ide_version`, `plugin`, `plugin_version`

---

## 🚀 Implementation Checklist

- [ ] Read CSV file
- [ ] Filter out empty user rows
- [ ] For each user, create a Copilot JSON record
- [ ] Map user identification fields (`user_login`, `user_id`)
- [ ] Map activity counts (`code_acceptance_activity_count`, etc.)
- [ ] Create `totals_by_feature` breakdown with **`"feature"`** field (NOT `"name"`!)
- [ ] Add `used_agent` and `used_chat` boolean flags
- [ ] Map lines of code fields at root level (`loc_added_sum`, etc.)
- [ ] Set date fields (`day`, `report_start_day`, `report_end_day`)
- [ ] Set `enterprise_id` (string format, e.g., "283613")
- [ ] ❌ **DO NOT** create separate `agent_edit` object at root level
- [ ] ❌ **DO NOT** use `"name"` field in breakdowns - use `"ide"` or `"feature"`
- [ ] ❌ **DO NOT** put version tracking at root level - it goes in `totals_by_ide`
- [ ] Validate JSON structure against official schema (`copilot_dailyy_schema.txt`)
- [ ] Test with sample data

---

## 📁 File Reference

| File | Purpose |
|------|---------|
| `copilot_metrics_format.json` | **UPDATED** - Per-user Copilot format example |
| `augment_metrics_format.json` | Augment aggregated format (for reference) |
| `FIELD_MAPPING.md` | **UPDATED** - Per-user field-by-field mapping |
| `CSV_TO_JSON_MAPPING.md` | **UPDATED** - CSV to per-user JSON mapping |
| `COMPARISON_COPILOT_VS_AUGMENT.md` | **UPDATED** - Per-user format comparison |
| `QUICK_REFERENCE.md` | This file - quick lookup |

---

## 🔗 Key Differences: Copilot vs Augment

| Feature | Copilot (Per-User) | Augment (Per-User CSV) |
|---------|-------------------|----------------------|
| **Granularity** | Daily (28 days) | Cumulative |
| **IDE breakdown** | ✅ `totals_by_ide` | ❌ Not in CSV |
| **Language breakdown** | ✅ `totals_by_language_feature` | ❌ Not in CSV |
| **Feature breakdown** | ✅ `totals_by_feature` | ⚠️ Can map conceptually |
| **Model tracking** | ✅ `totals_by_model_feature` | ❌ N/A |
| **Version tracking** | ✅ IDE/plugin versions | ❌ Not in CSV |
| **Deletion tracking** | ✅ `loc_deleted_sum` | ❌ Not tracked |
| **Accept rate** | ❌ Not pre-calculated | ✅ Pre-calculated % |
| **Tool usage** | ❌ Not tracked | ✅ `Tool Uses` |
| **CLI agent** | ❌ Not tracked | ✅ Interactive/Non-Interactive |
| **Remote agent** | ❌ Not tracked | ✅ Remote Agent metrics |

---

## 💡 Pro Tips

1. **Start Simple**: Map core fields first (user, activity counts, LoC)
2. **Single Day Approach**: Report Augment cumulative data as single day (end of period)
3. **Generate User IDs**: Hash email addresses to create numeric user IDs
4. **Handle Missing Fields**: Set Copilot fields not in Augment to 0 or null
5. **Feature Breakdown**: Use `totals_by_feature` to separate completions, chat, and agent
6. **Validate**: Check that `code_acceptance_activity_count` matches CSV `Accepted Completions`
7. **Document Differences**: Note that Augment data is cumulative, not daily

---

## 📞 Next Steps

1. **Review** the updated `copilot_metrics_format.json` (per-user format)
2. **Check** the per-user mappings in `FIELD_MAPPING.md`
3. **Implement** using the pseudocode in `CSV_TO_JSON_MAPPING.md`
4. **Compare** formats using `COMPARISON_COPILOT_VS_AUGMENT.md`
5. **Test** with a few CSV rows first
6. **Iterate** and add breakdowns as needed

---

## ❓ FAQ

**Q: How do I handle the temporal difference (cumulative vs. daily)?**
A: Report Augment data as a single day (use end date of period), or if you have historical snapshots, calculate daily deltas.

**Q: What should I use for `user_id`?**
A: Generate a numeric ID from the email hash, or use an existing user ID mapping if available.

**Q: Do I need to include all Copilot fields?**
A: No. Omit fields like `totals_by_ide`, `totals_by_language_feature` if you don't have the data.

**Q: Should I set missing fields to 0 or omit them?**
A: For required fields like `loc_deleted_sum`, set to 0. For optional breakdowns, you can omit them.

**Q: Can I create 28 daily records per user?**
A: Only if you have daily snapshots. Otherwise, use a single record per user with the cumulative data.

**Q: What about Augment-specific metrics (Tool Uses, CLI Agent)?**
A: These don't map to Copilot fields. You could add them as custom fields or track separately.

**Q: How do I validate my mapping?**
A: Check that key fields match: `code_acceptance_activity_count` = CSV `Accepted Completions`, `loc_added_sum` = CSV `Total Modified Lines of Code`.


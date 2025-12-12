# Copilot to Augment Metrics Field Mapping (Per-User Format)

## Overview
This document maps GitHub Copilot **per-user** metrics fields (from the `users-28-day/latest` endpoint) to Augment AI metrics fields. Both formats now provide per-user, per-day data, which simplifies the mapping significantly.

## Important Context
- **Copilot Format**: Per-user daily records over a 28-day period (from `/enterprises/{enterprise}/copilot/metrics/reports/users-28-day/latest`)
- **Augment Format**: Per-user cumulative metrics from CSV export
- **Key Difference**: Copilot provides daily granularity; Augment CSV provides cumulative totals over a date range

## Top-Level Per-User Fields

### Copilot Fields → Augment Mapping

| Copilot Field | Augment CSV Column | Notes |
|---------------|-------------------|-------|
| `report_start_day` | N/A | Copilot-specific: Start of 28-day period |
| `report_end_day` | N/A | Copilot-specific: End of 28-day period |
| `day` | N/A | Copilot-specific: Specific day for this record |
| `enterprise_id` | N/A | Copilot-specific: Enterprise identifier |
| `user_id` | N/A | Maps conceptually to user identifier |
| `user_login` | `User` | GitHub username → Augment user email/name |

### Activity Count Fields

| Copilot Field | Augment Equivalent | Augment CSV Column(s) | Notes |
|---------------|-------------------|----------------------|-------|
| `user_initiated_interaction_count` | Direct sum | `Chat Messages` + `Agent Messages` + `Remote Agent Messages` + `Interactive CLI Agent Messages` + `Non-Interactive CLI Agent Messages` | All user-initiated AI interactions |
| `code_generation_activity_count` | Approximate sum | `Completions` + chat generations | Copilot: distinct output events |
| `code_acceptance_activity_count` | Direct mapping | `Accepted Completions` | Copilot: suggestions/blocks accepted |

### Lines of Code Fields (Root Level)

| Copilot Field | Augment CSV Column | Notes |
|---------------|-------------------|-------|
| `loc_suggested_to_add_sum` | `Completion Lines of Code` | Total lines suggested to add across all features |
| `loc_suggested_to_delete_sum` | N/A | Not tracked in Augment CSV |
| `loc_added_sum` | `Total Modified Lines of Code` | Total lines added (completions + agent/edit mode) |
| `loc_deleted_sum` | N/A | Not tracked in Augment CSV |

### Boolean Flags (Root Level)

| Copilot Field | Augment Equivalent | Notes |
|---------------|-------------------|-------|
| `used_agent` | Check if `Agent Messages` > 0 or `Remote Agent Messages` > 0 or `Interactive CLI Agent Messages` > 0 or `Non-Interactive CLI Agent Messages` > 0 | Boolean indicating agent usage |
| `used_chat` | Check if `Chat Messages` > 0 | Boolean indicating chat usage |

**Note:** The official schema does NOT have a separate `agent_edit` object. Agent edit is just another feature in `totals_by_feature`.

---

## Breakdown Structures

### totals_by_ide (Copilot) → Editor Breakdown (Augment)

**Copilot Structure (Official Schema):**
```json
"totals_by_ide": [
  {
    "ide": "vscode",
    "user_initiated_interaction_count": 7,
    "code_generation_activity_count": 22,
    "code_acceptance_activity_count": 0,
    "loc_suggested_to_add_sum": 10,
    "loc_suggested_to_delete_sum": 0,
    "loc_added_sum": 790,
    "loc_deleted_sum": 384,
    "last_known_plugin_version": {
      "sampled_at": "2025-11-15T23:59:19.7920000Z",
      "plugin": "copilot-chat",
      "plugin_version": "0.32.5"
    },
    "last_known_ide_version": {
      "sampled_at": "2025-11-15T23:59:19.7920000Z",
      "ide_version": "1.105.1"
    }
  }
]
```

**Key Fields:**
- `ide` (not `name`!) - IDE identifier (e.g., "vscode", "jetbrains")
- All activity counts and LoC metrics per IDE
- `last_known_plugin_version` - Object with `sampled_at`, `plugin`, `plugin_version`
- `last_known_ide_version` - Object with `sampled_at`, `ide_version`

**Augment Equivalent:** Not available in CSV (would require additional data source)

### totals_by_feature (Copilot) → Feature Breakdown (Augment)

**Copilot Structure (Official Schema):**
```json
"totals_by_feature": [
  {
    "feature": "chat_panel_agent_mode",
    "user_initiated_interaction_count": 7,
    "code_generation_activity_count": 3,
    "code_acceptance_activity_count": 0,
    "loc_suggested_to_add_sum": 10,
    "loc_suggested_to_delete_sum": 0,
    "loc_added_sum": 0,
    "loc_deleted_sum": 0
  }
]
```

**Key Fields:**
- `feature` (not `name`!) - Feature identifier (e.g., "code_completion", "chat_panel", "agent_edit", "chat_panel_agent_mode")
- All activity counts and LoC metrics per feature
- Includes `loc_suggested_to_delete_sum` and `loc_deleted_sum`

**Copilot Features:**
- `code_completion` → Maps to Augment `Completions` / `Accepted Completions`
- `chat_panel` → Maps to Augment `Chat Messages`
- `chat_panel_agent_mode` → Agent mode in chat panel
- `inline_chat` → Included in Augment chat metrics
- `agent_edit` → Maps to Augment `Agent Messages` / `Agent Lines of Code`

**Mapping:**

| Copilot Feature | Augment CSV Column(s) | Notes |
|----------------|----------------------|-------|
| `code_completion` | `Completions`, `Accepted Completions`, `Completion Lines of Code` | Direct mapping |
| `chat_panel` | `Chat Messages` | User messages in chat |
| `chat_panel_agent_mode` | `Agent Messages` | Agent mode in chat |
| `inline_chat` | Included in `Chat Messages` | Not separated in Augment CSV |
| `agent_edit` | `Agent Messages`, `Remote Agent Messages`, `Interactive CLI Agent Messages`, `Non-Interactive CLI Agent Messages`, `Agent Lines of Code`, `Remote Agent Lines of Code`, `CLI Agent Lines of Code` | Agent-initiated changes |

### totals_by_language_feature (Copilot) → Language + Feature Breakdown (Augment)

**Copilot Structure (Official Schema):**
```json
"totals_by_language_feature": [
  {
    "language": "java",
    "feature": "agent_edit",
    "code_generation_activity_count": 19,
    "code_acceptance_activity_count": 0,
    "loc_suggested_to_add_sum": 0,
    "loc_suggested_to_delete_sum": 0,
    "loc_added_sum": 790,
    "loc_deleted_sum": 384
  }
]
```

**Key Fields:**
- `language` - Programming language (e.g., "java", "python", "typescript")
- `feature` - Feature identifier
- **Does NOT include `user_initiated_interaction_count`** (unlike `totals_by_feature`)
- Includes all LoC metrics

**Augment Equivalent:** Not available in CSV (would require language-specific tracking)

### totals_by_model_feature (Copilot) → Model Breakdown (Augment)

**Copilot Structure (Official Schema):**
```json
"totals_by_model_feature": [
  {
    "model": "claude-4.0-sonnet",
    "feature": "agent_edit",
    "user_initiated_interaction_count": 0,
    "code_generation_activity_count": 19,
    "code_acceptance_activity_count": 0,
    "loc_suggested_to_add_sum": 0,
    "loc_suggested_to_delete_sum": 0,
    "loc_added_sum": 790,
    "loc_deleted_sum": 384
  }
]
```

**Key Fields:**
- Includes all activity counts AND all LoC metrics (unlike our previous understanding)

**Augment Equivalent:** Not applicable (Augment doesn't expose model selection to users in the same way)

### totals_by_language_model (Copilot)

**Copilot Structure (Official Schema):**
```json
"totals_by_language_model": [
  {
    "language": "java",
    "model": "claude-4.0-sonnet",
    "code_generation_activity_count": 19,
    "code_acceptance_activity_count": 0,
    "loc_suggested_to_add_sum": 0,
    "loc_suggested_to_delete_sum": 0,
    "loc_added_sum": 790,
    "loc_deleted_sum": 384
  }
]
```

**Key Fields:**
- **Does NOT include `user_initiated_interaction_count`** (like `totals_by_language_feature`)
- Includes all LoC metrics

**Augment Equivalent:** Not available in CSV

---

## Version Tracking

**Important:** Version tracking is NOT at the root level. It's within each IDE in `totals_by_ide`.

**Copilot Structure (within `totals_by_ide`):**
```json
"last_known_plugin_version": {
  "sampled_at": "2025-11-15T23:59:19.7920000Z",
  "plugin": "copilot-chat",
  "plugin_version": "0.32.5"
},
"last_known_ide_version": {
  "sampled_at": "2025-11-15T23:59:19.7920000Z",
  "ide_version": "1.105.1"
}
```

**Fields:**
- `last_known_plugin_version` - Object with `sampled_at`, `plugin`, `plugin_version`
- `last_known_ide_version` - Object with `sampled_at`, `ide_version`

**Augment Equivalent:** Not available in CSV

---

## Mapping Strategy: Per-User Records

### Approach 1: Direct Per-User Mapping (Recommended)
Since both formats are now per-user, you can create a direct mapping:

**For each user in Augment CSV:**
```json
{
  "user_login": "user@example.com",
  "user_id": <generated_or_mapped_id>,
  "day": "2024-12-11",  // End date of reporting period
  "report_start_day": "2024-11-14",
  "report_end_day": "2024-12-11",
  "enterprise_id": "your-enterprise-id",

  // Map from CSV columns
  "code_acceptance_activity_count": <Accepted Completions>,
  "loc_suggested_to_add_sum": <Completion Lines of Code>,
  "loc_added_sum": <sum of all LoC columns>,

  // Breakdowns (if available)
  "totals_by_feature": [
    {
      "name": "code_completion",
      "code_acceptance_activity_count": <Accepted Completions>,
      "loc_added_sum": <Completion Lines of Code>
    },
    {
      "name": "agent_edit",
      "loc_added_sum": <Agent Lines of Code + Remote Agent Lines of Code>
    }
  ]
}
```

### Approach 2: Aggregate to Daily Totals
If you need to match Copilot's aggregated format (for compatibility), sum across all users per day.

---

## CLI Agent Section (Augment-Specific)

Copilot has no equivalent for CLI agent metrics. This is unique to Augment:

| Augment CSV Column | Description | Usage |
|-------------------|-------------|-------|
| `Interactive CLI Agent Messages` | CLI messages in interactive mode | Track CLI engagement |
| `Non-Interactive CLI Agent Messages` | CLI messages in non-interactive mode | Track automation usage |
| `CLI Agent Lines of Code` | Lines generated by CLI agent | Measure CLI productivity |

---

## Tool Usage (Augment-Specific)

Copilot doesn't track tool usage in the same way. This is unique to Augment:

| Augment CSV Column | Description | Notes |
|-------------------|-------------|-------|
| `Tool Uses` | Number of tool invocations by agent | Unique Augment feature |

---

## Summary: Key Mapping Differences

### What's the Same
- Both formats now provide **per-user data**
- Both track code completions and acceptances
- Both track lines of code metrics

### What's Different in Copilot
- ✅ Daily granularity (28 days of daily records per user)
- ✅ IDE/editor breakdowns
- ✅ Language breakdowns
- ✅ Model tracking
- ✅ Feature-level breakdowns (code_completion, chat_panel, agent_edit, etc.)
- ✅ Version tracking (IDE and plugin versions)

### What's Different in Augment
- ✅ Cumulative metrics over date range (not daily)
- ✅ Accept rate percentage
- ✅ Tool usage tracking
- ✅ CLI agent metrics
- ✅ Remote agent metrics
- ✅ Instruction lines of code
- ❌ No language/editor breakdowns (in current CSV)
- ❌ No model tracking
- ❌ No version tracking

---

## Recommended Implementation Path

1. **Start Simple**: Map core per-user fields (user_login, activity counts, LoC metrics)
2. **Add Feature Breakdown**: Use `totals_by_feature` to separate completions, chat, and agent metrics
3. **Handle Temporal Difference**: Decide whether to:
   - Report Augment data as a single day (end of period)
   - Split cumulative data across 28 days (estimated daily average)
   - Keep as cumulative and document the difference
4. **Add Breakdowns Later**: When language/editor data becomes available, add those breakdowns
5. **Highlight Augment Strengths**: Emphasize tool usage, CLI agent, and remote agent metrics that Copilot doesn't have


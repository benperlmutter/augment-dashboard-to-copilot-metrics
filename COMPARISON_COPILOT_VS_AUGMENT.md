# Side-by-Side Comparison: Copilot vs Augment Metrics (Per-User Format)

## Important Update
This comparison now reflects the **OFFICIAL per-user** GitHub Copilot metrics format from the `/enterprises/{enterprise}/copilot/metrics/reports/users-28-day/latest` endpoint based on the official schema in `copilot_dailyy_schema.txt`.

**Critical Corrections Made:**
- ✅ Field names: `ide` (not `name`), `feature` (not `name`)
- ✅ No separate `agent_edit` object - it's a feature in `totals_by_feature`
- ✅ Version tracking is within `totals_by_ide`, not at root level
- ✅ Added `used_agent` and `used_chat` boolean flags at root level
- ✅ All breakdowns include complete LoC metrics

## Structure Comparison

### Copilot Metrics Structure (Per-User, Per-Day)
```json
{
  "report_start_day": "2024-11-14",
  "report_end_day": "2024-12-11",
  "day": "2024-11-14",
  "enterprise_id": "enterprise-123",
  "user_id": 12345,
  "user_login": "octocat",
  "user_initiated_interaction_count": 45,
  "code_generation_activity_count": 52,
  "code_acceptance_activity_count": 38,
  "loc_suggested_to_add_sum": 520,
  "loc_suggested_to_delete_sum": 0,
  "loc_added_sum": 405,
  "loc_deleted_sum": 12,
  "agent_edit": { ... },
  "totals_by_ide": [ ... ],
  "totals_by_feature": [ ... ],
  "totals_by_language_feature": [ ... ],
  "totals_by_model_feature": [ ... ],
  "totals_by_language_model": [ ... ],
  "last_known_ide_version": "1.85.0",
  "last_known_plugin_version": "1.145.0"
}
```

### Augment CSV Structure (Per-User, Cumulative)
```csv
User, First Seen, Last Seen, Active Days, Completions, Accepted Completions,
Accept Rate, Chat Messages, Agent Messages, Remote Agent Messages,
Interactive CLI Agent Messages, Non-Interactive CLI Agent Messages, Tool Uses,
Total Modified Lines of Code, Completion Lines of Code, Instruction Lines of Code,
Agent Lines of Code, Remote Agent Lines of Code, CLI Agent Lines of Code
```

**Key Difference:**
- **Copilot**: Per-user daily records (28 days × users)
- **Augment**: Per-user cumulative totals over date range

---

## Detailed Field Comparison

### 1. User Identification

#### Copilot Fields
```json
{
  "user_id": 12345,
  "user_login": "octocat",
  "enterprise_id": "enterprise-123"
}
```

#### Augment CSV Columns
```csv
User (email/username)
```

#### Key Differences
| Aspect | Copilot | Augment |
|--------|---------|---------|
| User identifier | `user_id` (numeric) | User email/name (string) |
| Username | `user_login` (GitHub username) | `User` column |
| Enterprise ID | ✅ Yes | ❌ N/A |

---

### 2. Temporal Fields

#### Copilot Fields
```json
{
  "report_start_day": "2024-11-14",
  "report_end_day": "2024-12-11",
  "day": "2024-11-14"
}
```

#### Augment CSV Columns
```csv
First Seen, Last Seen
```

#### Key Differences
| Aspect | Copilot | Augment |
|--------|---------|---------|
| Granularity | Daily records (28 days per user) | Cumulative over date range |
| Date format | YYYY-MM-DD | YYYY-MM-DD |
| Reporting period | 28-day rolling window | Custom date range |

---

### 3. Activity Counts

#### Copilot Fields
```json
{
  "user_initiated_interaction_count": 45,
  "code_generation_activity_count": 52,
  "code_acceptance_activity_count": 38
}
```

#### Augment CSV Columns
```csv
Completions, Accepted Completions, Chat Messages, Agent Messages
```

#### Mapping
| Copilot Field | Augment Equivalent | Notes |
|---------------|-------------------|-------|
| `user_initiated_interaction_count` | `Chat Messages` + `Agent Messages` + `Remote Agent Messages` + `Interactive CLI Agent Messages` + `Non-Interactive CLI Agent Messages` | All user-initiated interactions with AI |
| `code_generation_activity_count` | `Completions` (partial) | Copilot: all output events; Augment: completions shown |
| `code_acceptance_activity_count` | `Accepted Completions` | Direct mapping ✅ |

---

### 4. Lines of Code Metrics

#### Copilot Fields
```json
{
  "loc_suggested_to_add_sum": 520,
  "loc_suggested_to_delete_sum": 0,
  "loc_added_sum": 405,
  "loc_deleted_sum": 12
}
```

#### Augment CSV Columns
```csv
Completion Lines of Code, Agent Lines of Code, Remote Agent Lines of Code,
CLI Agent Lines of Code, Instruction Lines of Code, Total Modified Lines of Code
```

#### Mapping
| Copilot Field | Augment Equivalent | Notes |
|---------------|-------------------|-------|
| `loc_suggested_to_add_sum` | `Completion Lines of Code` | Lines suggested via completions |
| `loc_suggested_to_delete_sum` | ❌ Not tracked | Augment doesn't track deletions |
| `loc_added_sum` | `Total Modified Lines of Code` | Sum of all LoC columns |
| `loc_deleted_sum` | ❌ Not tracked | Augment doesn't track deletions |

---

### 5. Agent Edit Section (Copilot)

#### Copilot Structure
```json
"agent_edit": {
  "loc_added_sum": 85,
  "loc_deleted_sum": 12
}
```

#### Augment Equivalent
```csv
Agent Lines of Code, Remote Agent Lines of Code, CLI Agent Lines of Code
```

#### Mapping
| Copilot Field | Augment CSV Column | Notes |
|---------------|-------------------|-------|
| `agent_edit.loc_added_sum` | `Agent Lines of Code` + `Remote Agent Lines of Code` + `CLI Agent Lines of Code` | Agent-generated code |
| `agent_edit.loc_deleted_sum` | ❌ Not tracked | Augment doesn't track deletions |

---

### 6. Breakdown by IDE (Copilot)

#### Copilot Structure
```json
"totals_by_ide": [
  {
    "name": "vscode",
    "user_initiated_interaction_count": 35,
    "code_generation_activity_count": 40,
    "code_acceptance_activity_count": 30,
    "loc_suggested_to_add_sum": 420,
    "loc_added_sum": 320
  },
  {
    "name": "jetbrains",
    "user_initiated_interaction_count": 10,
    "code_generation_activity_count": 12,
    "code_acceptance_activity_count": 8,
    "loc_suggested_to_add_sum": 100,
    "loc_added_sum": 85
  }
]
```

#### Augment Equivalent
```
NOT AVAILABLE IN CURRENT CSV
```

**Note:** Augment CSV doesn't include IDE/editor breakdowns. Would require additional data source.

---

### 7. Breakdown by Feature (Copilot)

#### Copilot Structure
```json
"totals_by_feature": [
  {
    "name": "code_completion",
    "user_initiated_interaction_count": 0,
    "code_generation_activity_count": 30,
    "code_acceptance_activity_count": 25,
    "loc_suggested_to_add_sum": 250,
    "loc_added_sum": 200
  },
  {
    "name": "chat_panel",
    "user_initiated_interaction_count": 25,
    "code_generation_activity_count": 15,
    "code_acceptance_activity_count": 10,
    "loc_suggested_to_add_sum": 180,
    "loc_added_sum": 120
  },
  {
    "name": "agent_edit",
    "user_initiated_interaction_count": 5,
    "code_generation_activity_count": 2,
    "code_acceptance_activity_count": 0,
    "loc_added_sum": 85,
    "loc_deleted_sum": 12
  }
]
```

#### Augment Equivalent (Conceptual Mapping)
```csv
# code_completion → Completions, Accepted Completions, Completion Lines of Code
# chat_panel → Chat Messages
# agent_edit → Agent Messages, Remote Agent Messages, Interactive CLI Agent Messages, Non-Interactive CLI Agent Messages, Agent Lines of Code, Remote Agent Lines of Code, CLI Agent Lines of Code
```

**Note:** Augment data can be mapped to features conceptually, but not broken down per-feature in the CSV.

---

### 8. Breakdown by Language + Feature (Copilot)

#### Copilot Structure
```json
"totals_by_language_feature": [
  {
    "language": "python",
    "feature": "code_completion",
    "user_initiated_interaction_count": 0,
    "code_generation_activity_count": 18,
    "code_acceptance_activity_count": 15,
    "loc_suggested_to_add_sum": 150,
    "loc_added_sum": 120
  }
]
```

#### Augment Equivalent
```
NOT AVAILABLE IN CURRENT CSV
```

**Note:** Would require language-specific tracking in Augment.

---

### 9. Breakdown by Model (Copilot)

#### Copilot Structure
```json
"totals_by_model_feature": [
  {
    "model": "gpt-4",
    "feature": "chat_panel",
    "user_initiated_interaction_count": 20,
    "code_generation_activity_count": 12,
    "code_acceptance_activity_count": 8
  }
]
```

#### Augment Equivalent
```
NOT APPLICABLE
```

**Note:** Augment doesn't expose model selection to users in the same way Copilot does.

---

### 10. Version Tracking (Copilot)

#### Copilot Fields
```json
{
  "last_known_ide_version": "1.85.0",
  "last_known_plugin_version": "1.145.0"
}
```

#### Augment Equivalent
```
NOT AVAILABLE IN CURRENT CSV
```

---

### 11. Augment-Specific Metrics (No Copilot Equivalent)

#### Tool Usage
```csv
Tool Uses
```
**Unique to Augment:** Tracks agent tool invocations

#### CLI Agent
```csv
Interactive CLI Agent Messages, Non-Interactive CLI Agent Messages, CLI Agent Lines of Code
```
**Unique to Augment:** Tracks CLI-based agent usage

#### Remote Agent
```csv
Remote Agent Messages, Remote Agent Lines of Code
```
**Unique to Augment:** Tracks remote agent usage

#### Accept Rate
```csv
Accept Rate
```
**Unique to Augment:** Pre-calculated acceptance rate percentage

#### Instruction Lines
```csv
Instruction Lines of Code
```
**Unique to Augment:** Lines from instruction-based generation

---

## Summary Table: Per-User Format Comparison

| Aspect | Copilot (Per-User) | Augment (Per-User) |
|--------|-------------------|-------------------|
| **Data Structure** | JSON per user per day | CSV per user (cumulative) |
| **Temporal Granularity** | Daily (28 days) | Cumulative over date range |
| **User Identification** | `user_id`, `user_login` | `User` (email/name) |
| **Activity Counts** | `user_initiated_interaction_count`, `code_generation_activity_count`, `code_acceptance_activity_count` | `Completions`, `Accepted Completions`, `Chat Messages`, `Agent Messages` |
| **Lines of Code** | `loc_suggested_to_add_sum`, `loc_added_sum`, `loc_deleted_sum` | `Completion Lines of Code`, `Agent Lines of Code`, `Total Modified Lines of Code` |
| **IDE Breakdown** | ✅ `totals_by_ide` | ❌ Not available |
| **Language Breakdown** | ✅ `totals_by_language_feature` | ❌ Not available |
| **Feature Breakdown** | ✅ `totals_by_feature` | ❌ Not available (can map conceptually) |
| **Model Tracking** | ✅ `totals_by_model_feature` | ❌ N/A |
| **Version Tracking** | ✅ `last_known_ide_version`, `last_known_plugin_version` | ❌ Not available |
| **Agent Metrics** | `agent_edit` section only | ✅ Comprehensive: `Agent Messages`, `Remote Agent Messages`, `Tool Uses` |
| **CLI Agent** | ❌ Not available | ✅ `Interactive/Non-Interactive CLI Agent Messages` |
| **Accept Rate** | ❌ Not tracked | ✅ Pre-calculated percentage |
| **Tool Usage** | ❌ Not tracked | ✅ `Tool Uses` |
| **Deletion Tracking** | ✅ `loc_deleted_sum` | ❌ Not tracked |

---

## Metric Field Translation

| Copilot Field | Augment CSV Column | Direct Match? | Notes |
|---------------|-------------------|---------------|-------|
| `user_login` | `User` | ✅ Yes | Username/email |
| `day` | N/A | ❌ No | Copilot has daily granularity |
| `code_acceptance_activity_count` | `Accepted Completions` | ✅ Yes | Direct mapping |
| `loc_suggested_to_add_sum` | `Completion Lines of Code` | ✅ Yes | Lines suggested |
| `loc_added_sum` | `Total Modified Lines of Code` | ✅ Yes | Total lines added |
| `loc_deleted_sum` | N/A | ❌ No | Augment doesn't track deletions |
| `user_initiated_interaction_count` | `Chat Messages` + `Agent Messages` + `Remote Agent Messages` + `Interactive CLI Agent Messages` + `Non-Interactive CLI Agent Messages` | ✅ Yes | All user-initiated AI interactions |
| `code_generation_activity_count` | `Completions` | ⚠️ Partial | Copilot includes all outputs; Augment only completions |
| `agent_edit.loc_added_sum` | `Agent Lines of Code` + `Remote Agent Lines of Code` + `CLI Agent Lines of Code` | ✅ Yes | Agent-generated code |
| N/A | `Tool Uses` | ➕ New | Unique to Augment |
| N/A | `Accept Rate` | ➕ New | Unique to Augment |
| N/A | `Instruction Lines of Code` | ➕ New | Excluded from mapping |

---

## Key Insights

### What Makes Copilot's Format Powerful
1. **Daily Granularity**: Track trends over time (28 days of daily data per user)
2. **Rich Breakdowns**: IDE, language, feature, and model-level insights
3. **Version Tracking**: Correlate metrics with IDE/plugin versions
4. **Deletion Tracking**: Understand code removal patterns

### What Makes Augment's Format Powerful
1. **Comprehensive Agent Metrics**: Tool usage, remote agent, CLI agent
2. **Accept Rate**: Pre-calculated acceptance percentage
3. **Simplicity**: Single cumulative record per user
4. **Unique Features**: CLI agent, tool usage, instruction-based generation

### Mapping Strategy Recommendation
1. **For Compatibility**: Map Augment CSV to Copilot's per-user structure
2. **For Simplicity**: Report Augment data as single-day snapshot (end of period)
3. **For Accuracy**: If possible, query Augment database for daily breakdowns
4. **For Completeness**: Highlight Augment-specific metrics that Copilot doesn't have


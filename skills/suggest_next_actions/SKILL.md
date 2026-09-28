---
name: suggest_next_actions
description: Map ESCALATE / ENHANCED_REVIEW / CLEAR to auditable next actions.
---

# suggest_next_actions (Phase 1 – 4th modular skill)

## Contract
**Input:** `recommendation`, `risk_score`, `txn_id`  
**Output:** `next_actions[]`, `priority`

| Recommendation | Next actions | Priority |
|---|---|---|
| `ESCALATE` | Escalate to L2; attach context; request source of funds | HIGH |
| `ENHANCED_REVIEW` | Request SOF; follow-up date; KYC refresh | MEDIUM |
| `CLEAR` | Clear with documented rationale | LOW |

No automatic customer messages. **Open Case** in Streamlit is the only Phase 1 write (`CASES` + `CASE_EVENTS`).

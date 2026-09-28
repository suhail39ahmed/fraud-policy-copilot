# Phase 2 runbook

Schema: `FRAUD_COPILOT.DEMO`. App uses Streamlit in Snowflake (`get_active_session()`).

## 1. Run SQL (worksheet order)

```sql
-- Phase 1 (if not already applied)
-- @sql/02_cases_and_audit.sql
-- @sql/03_audit_and_alert.sql

-- Phase 2
-- @sql/04_fraud_ring_graph.sql
-- @sql/05_case_management.sql
```

Verify ring seeds:

```sql
SELECT * FROM V_FRAUD_RING_EDGES
WHERE EDGE_TYPE IN ('SHARED_DEVICE', 'SHARED_IBAN_LAST4')
ORDER BY EDGE_TYPE, SRC_CUSTOMER;
-- Expect C003–C005 DEV-RING-01; C002–C005 7789
```

## 2. Deploy Streamlit (SiS)

**Option A — new SiS app file**

1. In Snowsight → Projects → Streamlit → create or open your Fraud Copilot app.
2. Paste / upload `app/streamlit_phase2.py` as the main file (or add alongside and set as entrypoint).
3. Ensure the app role can `SELECT` on `CUSTOMERS`, `TRANSACTIONS`, `POLICIES`, `CUSTOMER_GRAPH_ATTRS`, `V_FRAUD_RING_*`, `CASES`, `CASE_EVENTS`, `CASE_COMMENTS`, `REVIEW_AUDIT` and `INSERT`/`UPDATE` on case tables (+ `CALL` on `SP_*` if you use procedures).

**Option B — replace existing entrypoint**

```text
Copy app/streamlit_phase2.py → app/streamlit_app.py  (or the SiS main module name)
```

Local connector app (`streamlit_app.py` Phase 1) is unchanged; Phase 2 UI is SiS-first.

## 3. Demo walkthrough

| Tab | What to show |
|---|---|
| **Review** | Pick `T2001` / `T2005` / `T1001` → Run → score + AML citations + Open Case |
| **Fraud ring** | Select customer `C005` (or txn that maps to it) → nodes/edges tables + HTML cards for `DEV-RING-01` / `7789` |
| **Cases** | Filter status, add comment, transition `OPEN → IN_REVIEW → ESCALATED → CLOSED` |

## 4. Skills (CoCo)

1. `get_case_context`  
2. `match_policy`  
3. `explain_decision`  
4. `suggest_next_actions`  
5. **`map_fraud_ring`** ← Phase 2 (`skills/map_fraud_ring/SKILL.md`)

## 5. Out of scope this phase

- Live sanctions / PEP / adverse-media APIs → **SKIPPED** (inline `HIGH_RISK_COUNTRIES` only)
- Heavy JS graph libraries (vis.js / Cytoscape) — HTML/CSS node cards only

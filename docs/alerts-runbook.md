# Snowflake alerts + audit

## Already done in app
- Tiny Streamlit UI: paste/pick txn → score + citations + next actions
- Skill `suggest_next_actions` (open case / SOF / clear)
- Skip: graph rings, sanctions APIs, multi-agent, full case app

## Run once in a worksheet
`sql/03_audit_and_alert.sql`

Creates:
- `REVIEW_AUDIT` — every Streamlit run logs txn_id, score, recommendation, rules, timestamp
- View `HIGH_RISK_REVIEWS_24H`
- Alert `FRAUD_HIGH_RISK_ALERT` (hourly) → writes `CASE_EVENTS` type `ALERT_HIGH_RISK`

If `CREATE ALERT` fails on trial, use the Task fallback commented in the same file.

## Verify
```sql
SELECT * FROM REVIEW_AUDIT ORDER BY REVIEWED_AT DESC LIMIT 20;
SHOW ALERTS LIKE 'FRAUD%';
SELECT * FROM CASE_EVENTS WHERE EVENT_TYPE = 'ALERT_HIGH_RISK' ORDER BY CREATED_AT DESC;
```

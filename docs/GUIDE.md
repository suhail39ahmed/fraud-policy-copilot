# Fraud Policy Copilot — Build & Demo Guide

**Event:** Snowflake CoCo CLI Hackathon 2026 – GCC Edition (Hack2Skill)  
**Challenge:** Risk, Fraud and Regulatory Intelligence Copilot  
**Repo:** https://github.com/suhail39ahmed/fraud-policy-copilot  
**Live app (SiS):** `FRAUD_COPILOT.DEMO` → Streamlit `fraud_policy_copilot`

This is the single project doc. Use the README for the overview; use this file for setup, phases, and demo steps.

---

## What we built

A **policy-cited fraud case copilot** for analysts:

| Step | What happens |
|------|----------------|
| **Input** | Transaction id (demo: `T2001`, `T2005`, `T1001`) |
| **Processing** | Modular skills load context, match AML-style rules, score risk, suggest next actions, map fraud rings |
| **Output** | Risk score, fired rules with citations, escalate / enhanced review / clear, case + alert trail |

**Snowflake features used:** Streamlit in Snowflake (SiS), tables + views, Snowflake Alert on high-risk reviews, case/event audit trail. Cortex / CoCo CLI skills power the narrative path; the SiS app mirrors the same decision logic for the live demo.

**Explicitly skipped:** live OFAC/UN/EU sanctions APIs. Geography risk uses a **demo country set** (`CY`, `IR`, `KP`, `RU`) so the prototype stays self-contained.

---

## Phases (complete)

### Phase 1 — Review & cases
- Skills: `get_case_context`, `match_policy`, `explain_decision`, `suggest_next_actions`
- Sample data + policies in `sql/01_sample_data.sql`
- Cases / events: `sql/02_cases_and_audit.sql`
- Streamlit **Review** tab: pipeline UI, risk gauge, open case

### Phase 2 — Fraud ring & case management
- Skill: `map_fraud_ring`
- Graph attrs + edges: `sql/04_fraud_ring_graph.sql`
- Status transitions / comments: `sql/05_case_management.sql`
- Streamlit **Fraud ring** + **Cases** tabs
- Demo ring seeds: `C003`↔`C005` device `DEV-RING-01`; `C002`↔`C005` IBAN last4 `7789`

### Phase 3 — Alerts
- Audit + alert: `sql/03_audit_and_alert.sql`
  - Table `REVIEW_AUDIT`
  - View `HIGH_RISK_REVIEWS_24H` (score ≥ 70, last 24h)
  - Alert `FRAUD_HIGH_RISK_ALERT` → `CASE_EVENTS` with `ALERT_HIGH_RISK`
- Streamlit **Alerts** tab: audit rows, high-risk 24h, alert firings

---

## One-time Snowflake setup

Role: **ACCOUNTADMIN** (or equivalent). Warehouse: **COMPUTE_WH**.

```sql
USE DATABASE FRAUD_COPILOT;
USE SCHEMA DEMO;
```

Run in order (Worksheets):

1. `sql/01_sample_data.sql`
2. `sql/02_cases_and_audit.sql`
3. `sql/03_audit_and_alert.sql`  ← creates / resumes the Alert
4. `sql/04_fraud_ring_graph.sql`
5. `sql/05_case_management.sql`

Verify alert:

```sql
SHOW ALERTS LIKE 'FRAUD_HIGH_RISK_ALERT';
-- If suspended:
ALTER ALERT FRAUD_HIGH_RISK_ALERT RESUME;
-- Fire once after a high-risk review (optional, do not wait 60 min):
EXECUTE ALERT FRAUD_HIGH_RISK_ALERT;
```

If `CREATE ALERT` is unavailable on the trial, use the **Task fallback** commented at the bottom of `sql/03_audit_and_alert.sql`.

---

## Streamlit app (SiS)

- **Single entry file:** `app/streamlit_app.py` (do not add extra Streamlit modules under `app/`)
- Uses `get_active_session()` — **no** `secrets.toml` required in Snowflake
- Local `secrets.toml` is only for optional local Streamlit; see `app/.streamlit/secrets.toml.example`
- Deploy: paste or Git sync into Snowflake Streamlit; entry path `app/streamlit_app.py`
- Tabs: **Review** · **Fraud ring** · **Cases** · **Alerts**

---

## Demo script (about 4 minutes)

1. **Review** → Quick pick `T2005` → Run policy review → show structuring / high score → Open Case  
2. Compare briefly with `T2001` (wire + geo) and `T1001` (clean control)  
3. **Fraud ring** → Customer `C005` → Map ring → show shared device / IBAN cluster cards  
4. **Cases** → select the case → comment + status transition  
5. **Alerts** → show `REVIEW_AUDIT`, high-risk 24h, `ALERT_HIGH_RISK` events  

Talking points for judges: modular skills, policy citations, native Snowflake Alert (not only a UI flash), honest demo sanctions list instead of a fake live feed.

---

## CoCo CLI skills (optional narrative path)

Under `skills/` + workflow `fraud_case_review`. Useful for CLI demos; SiS alone is enough for the Streamlit path.

---

## Submission checklist

- [ ] GitHub repo + polished README  
- [ ] Live SiS link or Loom of the live app  
- [ ] Screenshots: Review (T2005), Fraud ring (C005), Cases, Alerts  
- [ ] Demo video (3–5 min) following the script above  
- [ ] Deck / PDF: problem, architecture, Snowflake features, demo, skips  
- [ ] Hack2Skill portal fields filled  

---

## Key identifiers

| Item | Value |
|------|--------|
| Database / schema | `FRAUD_COPILOT.DEMO` |
| Demo txns | `T2001`, `T2005` (often highest), `T1001` |
| Ring focus | `C005` |
| High-risk threshold | Risk score ≥ 70 |
| Sanctions | Demo list only — `CY`, `IR`, `KP`, `RU` |

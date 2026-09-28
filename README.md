# Fraud Policy Copilot

**Snowflake CoCo CLI Hackathon 2026 – GCC Edition** (Hack2Skill)  
**Challenge:** Risk, Fraud and Regulatory Intelligence Copilot

A Streamlit-in-Snowflake copilot that helps fraud analysts go from a **flagged transaction** to a **policy-cited decision**, a **fraud-ring map**, a **case**, and a **native Snowflake alert trail**.

---

## Why it exists

Analysts burn time hunting AML / KYC policy text for every alert. This prototype takes a transaction id, loads customer context, matches rules, and returns a **risk score**, **citations**, **next actions**, plus optional **ring** and **case** workflow — all inside Snowflake.

---

## Demo in one glance

| Tab | What you show |
|-----|----------------|
| **Review** | `T2005` → score + fired rules → Open case |
| **Fraud ring** | `C005` → shared device / IBAN cluster |
| **Cases** | Status transitions + comments |
| **Alerts** | `REVIEW_AUDIT` + Snowflake `FRAUD_HIGH_RISK_ALERT` events |

**Sanctions:** demo country list only (`CY`, `IR`, `KP`, `RU`) — live sanctions APIs intentionally skipped.

---

## Architecture

```text
Transaction id
    → get_case_context
    → match_policy (+ demo geo list)
    → explain_decision / suggest_next_actions
    → REVIEW_AUDIT
    → Snowflake Alert (score ≥ 70) → CASE_EVENTS
    → map_fraud_ring / Cases UI
```

**Stack:** Snowflake · Streamlit in Snowflake · CoCo CLI skills · SQL tables / views / Alert

---

## Modular skills

| Skill | Role |
|--------|------|
| `get_case_context` | Customer + recent transactions |
| `match_policy` | Score against AML-style rules |
| `explain_decision` | Citations + recommendation |
| `suggest_next_actions` | Analyst next steps |
| `map_fraud_ring` | Shared device / IBAN / phone / merchant links |

Workflow: `fraud_case_review` chains the review skills end-to-end (CLI path).

---

## Quick start

### 1. Load Snowflake objects
In a worksheet (`ACCOUNTADMIN`, warehouse `COMPUTE_WH`):

```sql
USE DATABASE FRAUD_COPILOT;
USE SCHEMA DEMO;
```

Run `sql/01` → `02` → `03` → `04` → `05` in order.  
Details and alert checks: **[docs/GUIDE.md](docs/GUIDE.md)**.

### 2. Open the Streamlit app
- Entry file: **`app/streamlit_app.py`** (single app file)
- In Snowflake: Streamlit app on `FRAUD_COPILOT.DEMO` (Git sync or paste)
- No `secrets.toml` needed in SiS (`get_active_session()`)

### 3. Walk the demo
Follow the 4-minute script in **[docs/GUIDE.md](docs/GUIDE.md)**.

---

## Repo layout

```text
app/
  streamlit_app.py          # Only Streamlit entry (SiS)
  requirements.txt
  .streamlit/               # Local optional config example
docs/
  GUIDE.md                  # Full setup, phases, demo, submission
sql/
  01_sample_data.sql
  02_cases_and_audit.sql
  03_audit_and_alert.sql    # REVIEW_AUDIT + Alert
  04_fraud_ring_graph.sql
  05_case_management.sql
skills/                     # CoCo CLI skill stubs
workflow/                   # fraud_case_review
README.md
environment.yml
```

---

## Phases (all complete)

1. **Review & cases** — scoring UI, audit, open case  
2. **Fraud ring & case management** — graph + status workflow  
3. **Alerts** — `REVIEW_AUDIT` + Snowflake Alert → `ALERT_HIGH_RISK`

---

## License / notes

Hackathon prototype for Hack2Skill · Snowflake CoCo CLI · GCC Edition.  
Built for demo clarity: small sample data, honest “demo sanctions list,” native Snowflake Alert for monitoring — not a production sanctions product.

# Phase 2 roadmap

## Delivered in this package
1. **Fraud ring graph** — `CUSTOMER_GRAPH_ATTRS` + `V_FRAUD_RING_EDGES` / `V_FRAUD_RING_NODES` (`sql/04_fraud_ring_graph.sql`); CoCo skill `map_fraud_ring`
2. **Case management (light)** — `ASSIGNEE` / `NOTES` on `CASES`, `CASE_COMMENTS`, status workflow `OPEN → IN_REVIEW → ESCALATED → CLOSED` (`sql/05_case_management.sql`)
3. **Streamlit Phase 2** — tabs Review / Fraud ring / Cases (`app/streamlit_phase2.py`); Hack2Skill branding retained
4. CoCo path stays modular: skills 1–4 unchanged; skill 5 = `map_fraud_ring`

## Explicitly SKIPPED
- **Sanctions live API** — SKIPPED. Demo uses inline `HIGH_RISK_COUNTRIES = {CY, RU, IR, KP}` only (documented in Streamlit + skill). No OFAC/UN/EU feed integration.
- Full SLA / queue routing / multi-assignee workflows
- External device-intel or open-banking graph providers
- Heavy client-side graph JS libraries

## Later (Phase 3+)
- Optional sanctions provider behind a secret + feature flag
- 2-hop ring expansion + merchant collusion scoring
- Native Snowflake Network / SnowGraph if account supports it

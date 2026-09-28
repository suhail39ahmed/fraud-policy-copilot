---
name: map_fraud_ring
description: Map shared-device / IBAN / phone / merchant-cluster edges for a customer or txn (demo graph attrs; no external APIs).
---

# map_fraud_ring (Phase 2 – 5th modular CoCo skill)

## Contract
**Input:** `customer_id` *or* `txn_id` (resolve customer via `TRANSACTIONS`)  
**Output:** `nodes[]`, `edges[]`, `focus_customer`, `ring_summary`

| Field | Meaning |
|---|---|
| `nodes[]` | Rows from `V_FRAUD_RING_NODES` connected to the focus customer (1-hop) |
| `edges[]` | Rows from `V_FRAUD_RING_EDGES` where `src` or `dst` is the focus customer |
| `edge_type` | `SHARED_DEVICE` \| `SHARED_IBAN_LAST4` \| `SHARED_PHONE` \| `SHARED_MERCHANT_CLUSTER` |
| `edge_key` | Shared attribute value (e.g. `DEV-RING-01`, `7789`) |
| `ring_summary` | Counts by edge_type + list of related customer_ids |

## Data source (demo only)
- Table `CUSTOMER_GRAPH_ATTRS` seeded in `sql/04_fraud_ring_graph.sql`
- **No live device fingerprint, open-banking, or sanctions API**
- Seed facts for the demo: `C003`↔`C005` share `DEVICE_ID=DEV-RING-01`; `C002`↔`C005` share `IBAN_LAST4=7789`

## Sanctions note
Geography / sanctions scoring stays on the inline demo set `HIGH_RISK_COUNTRIES = {CY, RU, IR, KP}` inside Streamlit (`streamlit_phase2.py`). **Live sanctions API = SKIPPED** (see `docs/phase2-roadmap.md`).

## Side effects
Read-only. Does not open cases or mutate `CASES` / `CASE_EVENTS`. Case writes remain in the Review / Cases tabs.

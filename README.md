# Fraud Policy Copilot

Snowflake **CoCo CLI** prototype for the **Snowflake CoCo CLI Hackathon 2026 – GCC Edition**.

**Challenge:** Risk, Fraud and Regulatory Intelligence Copilot

## Problem
Fraud analysts spend too long hunting policy clauses for each alert. This copilot takes a transaction/case id, gathers customer context, matches AML/KYC-style rules, and returns a risk score with citations and an escalate/clear recommendation.

## What it does (Input → Processing → Output)
1. **Input:** flagged transaction id (e.g. `T2001`)
2. **Processing:** three CoCo CLI skills run in sequence
3. **Output:** risk score, fired rules, policy citations, escalate/clear

## Modular skills
| Skill | Purpose |
|--------|---------|
| `get_case_context` | Load customer + recent transactions for a txn id |
| `match_policy` | Score the case against policy rules |
| `explain_decision` | Produce citations + short narrative + recommendation |

## Workflow
`fraud_case_review` → `get_case_context` → `match_policy` → `explain_decision`

## Stack
- Snowflake (trial / AI Data Cloud)
- CoCo CLI skills + one end-to-end workflow
- Sample demo data in `FRAUD_COPILOT.DEMO`

## Repo layout

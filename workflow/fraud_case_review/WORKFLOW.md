Name: fraud_case_review
Input: txn_id

Steps:
1. get_case_context(txn_id)     → case_context
2. match_policy(txn_id)         → match_result
3. explain_decision(match_json) → decision

Output: decision (score, fired rules, citations, escalate/clear, narrative)
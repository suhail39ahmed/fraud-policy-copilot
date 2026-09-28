USE DATABASE FRAUD_COPILOT;
USE SCHEMA DEMO;

-- :MATCH is VARIANT from match_policy; or recompute from :TXN_ID
WITH m AS (
  -- simplest: call same scoring inline or pass JSON
  SELECT PARSE_JSON(:MATCH_JSON) AS match_result
),
decision AS (
  SELECT
    match_result:txn_id::STRING AS txn_id,
    match_result:risk_score::NUMBER AS risk_score,
    match_result:fired_rules AS fired_rules,
    CASE
      WHEN match_result:risk_score::NUMBER >= 70 THEN 'ESCALATE'
      WHEN match_result:risk_score::NUMBER >= 40 THEN 'ENHANCED_REVIEW'
      ELSE 'CLEAR'
    END AS recommendation
  FROM m
)
SELECT
  OBJECT_CONSTRUCT(
    'txn_id', txn_id,
    'risk_score', risk_score,
    'recommendation', recommendation,
    'citations', fired_rules,
    'narrative',
      -- Optional Cortex (if enabled on your trial):
      SNOWFLAKE.CORTEX.COMPLETE(
        'llama3.1-8b',
        'You are an AML analyst. In 3 sentences, explain why this case is '
        || recommendation || ' given score ' || risk_score
        || ' and these rules: ' || fired_rules::STRING
        || '. Be factual; cite rule codes.'
      )
      -- If Cortex fails, replace narrative with a static string you write yourself.
  ) AS DECISION
FROM decision;
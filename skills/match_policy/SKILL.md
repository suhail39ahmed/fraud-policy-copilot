-- Feed case_context as VARIANT :CTX  (or join from txn_id again)
USE DATABASE FRAUD_COPILOT;
USE SCHEMA DEMO;

WITH ctx AS (
  SELECT
    t.*,
    c.RISK_TIER,
    c.ACCOUNT_OPENED,
    c.ACCOUNT_TYPE,
    DATEDIFF('month', c.ACCOUNT_OPENED, CURRENT_DATE()) AS account_age_months
  FROM TRANSACTIONS t
  JOIN CUSTOMERS c ON c.CUSTOMER_ID = t.CUSTOMER_ID
  WHERE t.TXN_ID = :TXN_ID
),
hits AS (
  SELECT p.*, 40 AS points FROM POLICIES p, ctx
  WHERE p.RULE_CODE = 'AML-WIRE-01'
    AND ctx.CHANNEL = 'WIRE' AND ctx.COUNTRY <> 'SA' AND ctx.COUNTRY <> 'AE' AND ctx.COUNTRY <> 'SG'
    AND ctx.AMOUNT >= 10000
  UNION ALL
  SELECT p.*, 35 FROM POLICIES p, ctx
  WHERE p.RULE_CODE = 'AML-NEW-02'
    AND ctx.CHANNEL = 'WIRE' AND ctx.AMOUNT >= 5000 AND ctx.account_age_months <= 18
  UNION ALL
  SELECT p.*, 25 FROM POLICIES p, ctx
  WHERE p.RULE_CODE = 'AML-CASH-03'
    AND ctx.CHANNEL = 'ATM' AND ctx.AMOUNT >= 10000
  UNION ALL
  SELECT p.*, 45 FROM POLICIES p, ctx
  WHERE p.RULE_CODE = 'AML-STRUCT-04'
    AND ctx.CHANNEL = 'WIRE' AND ctx.AMOUNT >= 10000
    AND (
      SELECT COUNT(*) FROM TRANSACTIONS r
      WHERE r.CUSTOMER_ID = ctx.CUSTOMER_ID
        AND r.AMOUNT < 1000
        AND r.TXN_TS >= DATEADD('hour', -24, ctx.TXN_TS)
        AND r.TXN_ID <> ctx.TXN_ID
    ) >= 2
  UNION ALL
  SELECT p.*, 30 FROM POLICIES p, ctx
  WHERE p.RULE_CODE = 'AML-GEO-05'
    AND ctx.COUNTRY IN ('CY','RU','IR','KP')  -- demo list; tune as you like
  UNION ALL
  SELECT p.*, 20 FROM POLICIES p, ctx
  WHERE p.RULE_CODE = 'AML-PROF-06'
    AND ctx.ACCOUNT_TYPE = 'PERSONAL' AND ctx.CHANNEL = 'WIRE' AND ctx.AMOUNT >= 10000
)
SELECT
  OBJECT_CONSTRUCT(
    'txn_id', :TXN_ID,
    'risk_score', LEAST(100, COALESCE(SUM(points), 0)),
    'fired_rules', COALESCE(ARRAY_AGG(
      OBJECT_CONSTRUCT(
        'policy_id', POLICY_ID,
        'rule_code', RULE_CODE,
        'title', TITLE,
        'severity', SEVERITY,
        'rule_text', RULE_TEXT,
        'points', points
      )
    ), ARRAY_CONSTRUCT())
  ) AS MATCH_RESULT
FROM hits;
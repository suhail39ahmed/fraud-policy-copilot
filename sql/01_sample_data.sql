CREATE DATABASE IF NOT EXISTS FRAUD_COPILOT;
CREATE SCHEMA IF NOT EXISTS FRAUD_COPILOT.DEMO;

USE DATABASE FRAUD_COPILOT;
USE SCHEMA DEMO;

CREATE OR REPLACE TABLE CUSTOMERS (
  CUSTOMER_ID    STRING,
  FULL_NAME      STRING,
  COUNTRY        STRING,
  RISK_TIER      STRING,
  ACCOUNT_OPENED DATE,
  ACCOUNT_TYPE   STRING
);

CREATE OR REPLACE TABLE TRANSACTIONS (
  TXN_ID      STRING,
  CUSTOMER_ID STRING,
  AMOUNT      NUMBER(18,2),
  CURRENCY    STRING,
  MERCHANT    STRING,
  COUNTRY     STRING,
  CHANNEL     STRING,
  TXN_TS      TIMESTAMP_NTZ,
  STATUS      STRING
);

CREATE OR REPLACE TABLE POLICIES (
  POLICY_ID STRING,
  TITLE     STRING,
  RULE_CODE STRING,
  RULE_TEXT STRING,
  SEVERITY  STRING
);

INSERT INTO CUSTOMERS VALUES
('C001','Omar Al Harbi','SA','LOW', '2021-03-12','PERSONAL'),
('C002','Fatima Rahman','AE','MEDIUM','2023-11-02','PERSONAL'),
('C003','Nova Trading LLC','AE','HIGH','2024-08-20','BUSINESS'),
('C004','James Khoo','SG','LOW','2020-01-15','PERSONAL'),
('C005','Green Palm Imports','SA','MEDIUM','2025-01-08','BUSINESS');

INSERT INTO TRANSACTIONS VALUES
('T1001','C001', 420.00,'SAR','Jarir Bookstore','SA','POS','2026-09-20 10:15:00','POSTED'),
('T1002','C001', 85.50,'SAR','Starbucks','SA','APP','2026-09-21 08:02:00','POSTED'),
('T1003','C004',1200.00,'SGD','FairPrice','SG','POS','2026-09-22 19:40:00','POSTED'),
('T2001','C003',48500.00,'USD','Offshore Supplies Ltd','CY','WIRE','2026-09-25 02:11:00','FLAGGED'),
('T2002','C002',12500.00,'AED','Cash Withdrawal','AE','ATM','2026-09-24 23:45:00','FLAGGED'),
('T2003','C005', 990.00,'SAR','Local Vendor A','SA','APP','2026-09-26 09:01:00','POSTED'),
('T2004','C005', 980.00,'SAR','Local Vendor B','SA','APP','2026-09-26 09:03:00','POSTED'),
('T2005','C005',32000.00,'USD','EU Parts GmbH','DE','WIRE','2026-09-26 09:10:00','FLAGGED'),
('T2006','C002', 3100.00,'AED','Dubai Mall','AE','POS','2026-09-23 16:20:00','POSTED'),
('T2007','C001', 7500.00,'SAR','Family Transfer','SA','APP','2026-09-22 21:00:00','PENDING');

INSERT INTO POLICIES VALUES
('P01','AML Wire Threshold','AML-WIRE-01',
 'Any cross-border wire above 10,000 USD (or equivalent) requires enhanced review and source-of-funds check.',
 'HIGH'),
('P02','New Account Elevated Risk','AML-NEW-02',
 'Accounts opened within the last 18 months that send cross-border wires above 5,000 USD are HIGH risk until KYC refresh.',
 'HIGH'),
('P03','Cash / ATM Large Withdrawal','AML-CASH-03',
 'ATM or cash-equivalent withdrawals above 10,000 in local currency require enhanced due diligence.',
 'MEDIUM'),
('P04','Structuring Pattern','AML-STRUCT-04',
 'Multiple payments just under 1,000 followed by a large wire within 24 hours may indicate structuring; escalate.',
 'CRITICAL'),
('P05','High-Risk Entity Geography','AML-GEO-05',
 'Transfers involving high-risk or unusual corridors (e.g. certain offshore jurisdictions) need sanctions and purpose checks.',
 'HIGH'),
('P06','Business vs Personal Mismatch','AML-PROF-06',
 'Personal accounts used for commercial-scale wires should be escalated for profile mismatch.',
 'MEDIUM');

-- Optional verify
SELECT 'CUSTOMERS' AS t, COUNT(*) AS n FROM CUSTOMERS
UNION ALL SELECT 'TRANSACTIONS', COUNT(*) FROM TRANSACTIONS
UNION ALL SELECT 'POLICIES', COUNT(*) FROM POLICIES;
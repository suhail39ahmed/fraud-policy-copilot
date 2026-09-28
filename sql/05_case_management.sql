-- Phase 2: light case management extensions (FRAUD_COPILOT.DEMO)
-- Adds ASSIGNEE / NOTES on CASES, CASE_COMMENTS, and status-transition helpers.
-- Allowed workflow: OPEN → IN_REVIEW → ESCALATED → CLOSED
-- (also OPEN → CLOSED for clear-path demos)

USE DATABASE FRAUD_COPILOT;
USE SCHEMA DEMO;

-- Extend CASES (Snowflake supports IF NOT EXISTS on ADD COLUMN)
ALTER TABLE CASES ADD COLUMN IF NOT EXISTS ASSIGNEE STRING;
ALTER TABLE CASES ADD COLUMN IF NOT EXISTS NOTES STRING;

CREATE TABLE IF NOT EXISTS CASE_COMMENTS (
    COMMENT_ID   NUMBER AUTOINCREMENT START 1 INCREMENT 1,
    CASE_ID      NUMBER NOT NULL,
    BODY         STRING NOT NULL,
    AUTHOR       STRING DEFAULT CURRENT_USER(),
    CREATED_AT   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Transition map (reference)
-- OPEN       → IN_REVIEW | CLOSED
-- IN_REVIEW  → ESCALATED | CLOSED
-- ESCALATED  → CLOSED
-- CLOSED     → (terminal)

-- ---------------------------------------------------------------------------
-- Snippet: set status (call from worksheet or Streamlit with bound values)
-- Replace :CASE_ID / :NEW_STATUS / :ACTOR as needed.
-- ---------------------------------------------------------------------------
/*
UPDATE CASES
SET STATUS = :NEW_STATUS,
    UPDATED_AT = CURRENT_TIMESTAMP(),
    ASSIGNEE = COALESCE(:ASSIGNEE, ASSIGNEE),
    NOTES = COALESCE(:NOTES, NOTES)
WHERE CASE_ID = :CASE_ID
  AND (
    (STATUS = 'OPEN'      AND :NEW_STATUS IN ('IN_REVIEW', 'CLOSED'))
 OR (STATUS = 'IN_REVIEW' AND :NEW_STATUS IN ('ESCALATED', 'CLOSED'))
 OR (STATUS = 'ESCALATED' AND :NEW_STATUS IN ('CLOSED'))
  );

INSERT INTO CASE_EVENTS (CASE_ID, TXN_ID, EVENT_TYPE, EVENT_DATA, ACTOR)
SELECT c.CASE_ID, c.TXN_ID, 'STATUS_CHANGED',
       OBJECT_CONSTRUCT('from', :OLD_STATUS, 'to', :NEW_STATUS),
       COALESCE(:ACTOR, CURRENT_USER())
FROM CASES c WHERE c.CASE_ID = :CASE_ID;
*/

-- ---------------------------------------------------------------------------
-- Procedure: SP_TRANSITION_CASE_STATUS
-- Usage: CALL SP_TRANSITION_CASE_STATUS(42, 'IN_REVIEW', 'analyst1', NULL);
-- ---------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE SP_TRANSITION_CASE_STATUS(
    P_CASE_ID NUMBER,
    P_NEW_STATUS STRING,
    P_ASSIGNEE STRING DEFAULT NULL,
    P_NOTES STRING DEFAULT NULL
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    v_old STRING;
    v_txn STRING;
    v_ok BOOLEAN DEFAULT FALSE;
BEGIN
    SELECT STATUS, TXN_ID INTO :v_old, :v_txn
    FROM CASES WHERE CASE_ID = :P_CASE_ID;

    IF (v_old IS NULL) THEN
        RETURN 'ERROR: case not found';
    END IF;

    IF (v_old = 'OPEN' AND :P_NEW_STATUS IN ('IN_REVIEW', 'CLOSED')) THEN
        v_ok := TRUE;
    ELSEIF (v_old = 'IN_REVIEW' AND :P_NEW_STATUS IN ('ESCALATED', 'CLOSED')) THEN
        v_ok := TRUE;
    ELSEIF (v_old = 'ESCALATED' AND :P_NEW_STATUS = 'CLOSED') THEN
        v_ok := TRUE;
    END IF;

    IF (NOT v_ok) THEN
        RETURN 'ERROR: illegal transition ' || v_old || ' → ' || :P_NEW_STATUS;
    END IF;

    UPDATE CASES
    SET STATUS = :P_NEW_STATUS,
        UPDATED_AT = CURRENT_TIMESTAMP(),
        ASSIGNEE = COALESCE(:P_ASSIGNEE, ASSIGNEE),
        NOTES = COALESCE(:P_NOTES, NOTES)
    WHERE CASE_ID = :P_CASE_ID;

    INSERT INTO CASE_EVENTS (CASE_ID, TXN_ID, EVENT_TYPE, EVENT_DATA, ACTOR)
    SELECT :P_CASE_ID, :v_txn, 'STATUS_CHANGED',
           OBJECT_CONSTRUCT('from', :v_old, 'to', :P_NEW_STATUS,
                            'assignee', :P_ASSIGNEE),
           CURRENT_USER();

    RETURN 'OK: ' || v_old || ' → ' || :P_NEW_STATUS;
END;
$$;

-- ---------------------------------------------------------------------------
-- Procedure: SP_ADD_CASE_COMMENT
-- Usage: CALL SP_ADD_CASE_COMMENT(42, 'Reviewed SOF docs', NULL);
-- ---------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE SP_ADD_CASE_COMMENT(
    P_CASE_ID NUMBER,
    P_BODY STRING,
    P_AUTHOR STRING DEFAULT NULL
)
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    INSERT INTO CASE_COMMENTS (CASE_ID, BODY, AUTHOR)
    SELECT :P_CASE_ID, :P_BODY, COALESCE(:P_AUTHOR, CURRENT_USER());

    INSERT INTO CASE_EVENTS (CASE_ID, TXN_ID, EVENT_TYPE, EVENT_DATA, ACTOR)
    SELECT c.CASE_ID, c.TXN_ID, 'COMMENT_ADDED',
           OBJECT_CONSTRUCT('preview', LEFT(:P_BODY, 120)),
           COALESCE(:P_AUTHOR, CURRENT_USER())
    FROM CASES c WHERE c.CASE_ID = :P_CASE_ID;

    RETURN 'OK: comment added';
END;
$$;

-- Example transitions (commented):
-- CALL SP_TRANSITION_CASE_STATUS(1, 'IN_REVIEW', 'analyst.demo', 'Starting review');
-- CALL SP_ADD_CASE_COMMENT(1, 'Requested source of funds from customer');
-- CALL SP_TRANSITION_CASE_STATUS(1, 'ESCALATED', 'l2.queue', 'Structuring pattern');
-- CALL SP_TRANSITION_CASE_STATUS(1, 'CLOSED', 'l2.queue', 'SAR filed / cleared');

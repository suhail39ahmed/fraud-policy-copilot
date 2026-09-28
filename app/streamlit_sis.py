"""Fraud Policy Copilot – Snowflake Streamlit in Snowflake (SiS).
Hack2Skill · Snowflake CoCo CLI Hackathon 2026 – GCC Edition
"""
from __future__ import annotations

import json
import time
from typing import Any

import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Fraud Policy Copilot", page_icon="🛡️", layout="wide")
session = get_active_session()

PRIMARY = "#29B5E8"
ACCENT = "#0B5FFF"
DARK = "#0F172A"

st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 1.2rem; }}
      @keyframes shimmer {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
      }}
      @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
      @keyframes pulseGlow {{
        0%, 100% {{ box-shadow: 0 0 0 0 rgba(220,38,38,.35); }}
        50% {{ box-shadow: 0 0 0 10px rgba(220,38,38,0); }}
      }}
      @keyframes pulseGlowAmber {{
        0%, 100% {{ box-shadow: 0 0 0 0 rgba(245,158,11,.35); }}
        50% {{ box-shadow: 0 0 0 10px rgba(245,158,11,0); }}
      }}
      @keyframes pulseGlowGreen {{
        0%, 100% {{ box-shadow: 0 0 0 0 rgba(22,163,74,.35); }}
        50% {{ box-shadow: 0 0 0 10px rgba(22,163,74,0); }}
      }}
      @keyframes flow {{
        0% {{ left: -30%; }}
        100% {{ left: 100%; }}
      }}
      .hero {{
        background: linear-gradient(120deg, {DARK}, #1e293b, {ACCENT}, {PRIMARY}, {DARK});
        background-size: 300% 300%;
        animation: shimmer 10s ease infinite, fadeUp .6s ease-out;
        border-radius: 16px; padding: 1.4rem 1.6rem; color: white;
        margin-bottom: 1rem; border: 1px solid rgba(255,255,255,.08);
      }}
      .hero h1 {{ margin: 0 0 .35rem 0; font-size: 1.75rem; }}
      .hero p {{ margin: 0; opacity: .92; }}
      .badge {{
        display: inline-block; background: {PRIMARY}; color: #06202a;
        font-weight: 700; font-size: .75rem; padding: .2rem .55rem;
        border-radius: 999px; margin-right: .4rem;
        animation: fadeUp .7s ease-out;
      }}
      .card {{
        background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 1rem 1.1rem; margin-bottom: .75rem;
        animation: fadeUp .45s ease-out;
      }}
      .pipeline {{
        display: flex; gap: .5rem; margin: .75rem 0 1rem 0; flex-wrap: wrap;
      }}
      .pipestep {{
        flex: 1; min-width: 140px; text-align: center; padding: .65rem .5rem;
        border-radius: 10px; background: #f1f5f9; font-weight: 600; font-size: .85rem;
        border: 1px solid #e2e8f0; animation: fadeUp .5s ease-out;
      }}
      .pipestep.active {{
        background: linear-gradient(90deg, {PRIMARY}, {ACCENT}); color: white; border: none;
      }}
      .flowbar {{
        position: relative; height: 6px; border-radius: 999px; background: #e2e8f0;
        overflow: hidden; margin: .25rem 0 1rem 0;
      }}
      .flowbar > span {{
        position: absolute; top: 0; height: 100%; width: 30%;
        background: linear-gradient(90deg, transparent, {PRIMARY}, {ACCENT}, transparent);
        animation: flow 1.4s linear infinite;
      }}
      .risk-hi {{ animation: pulseGlow 1.6s infinite; border-left: 6px solid #dc2626 !important; }}
      .risk-mid {{ animation: pulseGlowAmber 1.8s infinite; border-left: 6px solid #f59e0b !important; }}
      .risk-lo {{ animation: pulseGlowGreen 2s infinite; border-left: 6px solid #16a34a !important; }}
      .gauge-wrap {{
        background: #0f172a; border-radius: 12px; padding: .9rem 1rem; color: #e2e8f0;
        animation: fadeUp .5s ease-out;
      }}
      .gauge-track {{
        height: 14px; border-radius: 999px; background: #1e293b; overflow: hidden;
      }}
      .gauge-fill {{
        height: 100%; border-radius: 999px;
        transition: width 1s ease-out;
        background: linear-gradient(90deg, #16a34a, #f59e0b, #dc2626);
      }}
    </style>
    <div class="hero">
      <span class="badge">Hack2Skill</span>
      <span class="badge">Snowflake CoCo CLI · GCC Edition</span>
      <span class="badge">Risk / Fraud / Regulatory</span>
      <h1>🛡️ Fraud Policy Copilot</h1>
      <p>Input → Processing → Output · AML citations · modular CoCo skills</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def next_actions(recommendation: str, score: float = 0) -> list[str]:
    rec = (recommendation or "").upper().strip()
    if rec == "ESCALATE":
        return ["Escalate to L2", "Attach transaction context", "Request source of funds"]
    if rec == "ENHANCED_REVIEW":
        return ["Request source of funds", "Set a follow-up date", "Enhanced KYC refresh"]
    if score >= 70:
        return ["Escalate to L2", "Request source of funds"]
    if score >= 40:
        return ["Open case", "Review transaction context"]
    return ["Clear with documented rationale"]


def recommend(score: float) -> str:
    if score >= 70:
        return "ESCALATE"
    if score >= 40:
        return "ENHANCED_REVIEW"
    return "CLEAR"


def score_from_row(txn: dict[str, Any], recent_under_1k: int) -> tuple[float, list[dict]]:
    hits = []
    amount = float(txn.get("amount") or 0)
    channel = str(txn.get("channel") or "").upper()
    country = str(txn.get("country") or "").upper()
    account_type = str(txn.get("account_type") or "").upper()
    age = float(txn.get("account_age_months") or 999)
    domestic = {"SA", "AE", "SG"}

    def add(code, title, points, severity, text):
        hits.append({
            "rule_code": code, "title": title, "points": points,
            "severity": severity, "rule_text": text,
        })

    if channel == "WIRE" and country not in domestic and amount >= 10000:
        add("AML-WIRE-01", "AML Wire Threshold", 40, "HIGH",
            "Cross-border wire above 10,000 requires enhanced review.")
    if channel == "WIRE" and amount >= 5000 and age <= 18:
        add("AML-NEW-02", "New Account Elevated Risk", 35, "HIGH",
            "Newer accounts with cross-border wires need KYC refresh.")
    if channel == "ATM" and amount >= 10000:
        add("AML-CASH-03", "Cash / ATM Large Withdrawal", 25, "MEDIUM",
            "Large ATM withdrawals require enhanced due diligence.")
    if channel == "WIRE" and amount >= 10000 and recent_under_1k >= 2:
        add("AML-STRUCT-04", "Structuring Pattern", 45, "CRITICAL",
            "Sub-1000 payments then a large wire may indicate structuring.")
    if country in {"CY", "RU", "IR", "KP"}:
        add("AML-GEO-05", "High-Risk Geography", 30, "HIGH",
            "Unusual corridors need sanctions and purpose checks.")
    if account_type == "PERSONAL" and channel == "WIRE" and amount >= 10000:
        add("AML-PROF-06", "Profile Mismatch", 20, "MEDIUM",
            "Personal accounts used for commercial-scale wires should escalate.")
    return min(100.0, float(sum(h["points"] for h in hits))), hits


@st.cache_data(ttl=60)
def load_txn(txn_id: str):
    safe = txn_id.replace("'", "''")
    df = session.sql(f"""
        SELECT t.*, c.FULL_NAME, c.COUNTRY AS CUST_COUNTRY, c.RISK_TIER,
               c.ACCOUNT_TYPE, c.ACCOUNT_OPENED,
               DATEDIFF('month', c.ACCOUNT_OPENED, CURRENT_DATE()) AS ACCOUNT_AGE_MONTHS
        FROM TRANSACTIONS t
        JOIN CUSTOMERS c ON c.CUSTOMER_ID = t.CUSTOMER_ID
        WHERE t.TXN_ID = '{safe}'
        QUALIFY ROW_NUMBER() OVER (PARTITION BY t.TXN_ID ORDER BY t.TXN_TS) = 1
    """).to_pandas()
    if df.empty:
        return None, 0
    df.columns = [c.lower() for c in df.columns]
    row = df.iloc[0].to_dict()
    und = session.sql(f"""
        SELECT COUNT(*) AS N FROM TRANSACTIONS r
        WHERE r.CUSTOMER_ID = '{str(row["customer_id"]).replace("'", "''")}'
          AND r.AMOUNT < 1000
          AND r.TXN_TS >= DATEADD('hour', -24, '{row["txn_ts"]}')
          AND r.TXN_ID <> '{safe}'
    """).to_pandas()
    n = int(und.iloc[0]["N"]) if not und.empty else 0
    return row, n



def log_review_audit(txn_id: str, score: float, recommendation: str, hits: list[dict]) -> None:
    """Persist each Streamlit/CoCo-style review for alerts + demo audit trail."""
    tid = txn_id.replace("'", "''")
    rules = json.dumps(hits).replace("'", "''")
    try:
        session.sql(f"""
            INSERT INTO REVIEW_AUDIT (TXN_ID, RISK_SCORE, RECOMMENDATION, FIRED_RULES, SOURCE)
            SELECT '{tid}', {score}, '{recommendation}', PARSE_JSON('{rules}'), 'STREAMLIT_SIS'
        """).collect()
    except Exception:
        # Table may not exist yet — run sql/03_audit_and_alert.sql
        pass


def open_case(txn_id: str, score: float, recommendation: str, actions: list[str]) -> int:
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    payload = json.dumps(actions).replace("'", "''")
    tid = txn_id.replace("'", "''")
    session.sql(f"""
        INSERT INTO CASES (TXN_ID, STATUS, PRIORITY, RECOMMENDATION, RISK_SCORE, NEXT_ACTIONS, SOURCE)
        SELECT '{tid}', 'OPEN', '{priority}', '{recommendation}', {score},
               PARSE_JSON('{payload}'), 'STREAMLIT_SIS'
        WHERE NOT EXISTS (
          SELECT 1 FROM CASES WHERE TXN_ID = '{tid}' AND STATUS NOT IN ('CLOSED','CANCELLED')
        )
    """).collect()
    cid = session.sql(f"""
        SELECT CASE_ID FROM CASES
        WHERE TXN_ID = '{tid}' AND STATUS NOT IN ('CLOSED','CANCELLED')
        ORDER BY OPENED_AT DESC LIMIT 1
    """).to_pandas()
    if cid.empty:
        return 0
    case_id = int(cid.iloc[0]["CASE_ID"])
    edata = json.dumps({"recommendation": recommendation, "risk_score": score}).replace("'", "''")
    session.sql(f"""
        INSERT INTO CASE_EVENTS (CASE_ID, TXN_ID, EVENT_TYPE, EVENT_DATA)
        SELECT {case_id}, '{tid}', 'CASE_OPENED', PARSE_JSON('{edata}')
        WHERE NOT EXISTS (
          SELECT 1 FROM CASE_EVENTS WHERE CASE_ID = {case_id} AND EVENT_TYPE = 'CASE_OPENED'
        )
    """).collect()
    return case_id


st.markdown(
    """
    <div class="pipeline">
      <div class="pipestep">① Input</div>
      <div class="pipestep">② Processing</div>
      <div class="pipestep">③ Output</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Demo controls")
    st.caption("Hack2Skill · CoCo CLI · GCC")
    pick = st.selectbox("Quick pick", ["T2001", "T2005", "T1001", "Custom"])
    custom = st.text_input("Custom TXN_ID", value="T2001")
    txn_id = custom.strip() if pick == "Custom" else pick
    st.markdown("---")
    st.markdown("**Skills**")
    st.markdown(
        "1. `get_case_context`  \n"
        "2. `match_policy`  \n"
        "3. `explain_decision`  \n"
        "4. `suggest_next_actions`"
    )
    run = st.button("▶ Run policy review", type="primary", use_container_width=True)

if run:
    pipe = st.empty()
    bar = st.empty()
    status = st.empty()
    stages = [
        ("① Input", "Loading case context…"),
        ("② Processing", "Matching AML policies…"),
        ("③ Output", "Building recommendation…"),
    ]
    for i, (label, msg) in enumerate(stages):
        steps_html = []
        names = ["① Input", "② Processing", "③ Output"]
        for j, name in enumerate(names):
            cls = "pipestep active" if j <= i else "pipestep"
            steps_html.append(f'<div class="{cls}">{name}</div>')
        pipe.markdown(
            f'<div class="pipeline">{"".join(steps_html)}</div><div class="flowbar"><span></span></div>',
            unsafe_allow_html=True,
        )
        status.info(msg)
        time.sleep(0.35)

    txn, under_n = load_txn(txn_id)
    status.empty()
    bar.empty()
    if not txn:
        st.error(f"No transaction found for `{txn_id}`.")
    else:
        score, hits = score_from_row(txn, under_n)
        rec = recommend(score)
        st.session_state["review"] = {
            "txn_id": txn_id, "txn": txn, "score": score, "hits": hits,
            "recommendation": rec, "actions": next_actions(rec, score),
        }
        pipe.empty()

rev = st.session_state.get("review")
if not rev:
    st.info("Pick **T2001**, **T2005**, or **T1001**, then Run — watch the pipeline animate.")
else:
    score = rev["score"]
    risk_cls = "risk-hi" if score >= 70 else "risk-mid" if score >= 40 else "risk-lo"
    band = "High — escalate" if score >= 70 else "Medium — enhanced review" if score >= 40 else "Low — clear"
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Risk score", f"{score:.0f}")
    m2.metric("Recommendation", rev["recommendation"])
    m3.metric("Fired rules", len(rev["hits"]))
    m4.metric("Txn", rev["txn_id"])

    st.markdown(
        f"""
        <div class="gauge-wrap">
          <div style="display:flex;justify-content:space-between;margin-bottom:.4rem">
            <span>Risk gauge</span><span><b>{score:.0f}</b> / 100 · {band}</span>
          </div>
          <div class="gauge-track"><div class="gauge-fill" style="width:{score}%"></div></div>
        </div>
        <div class="card {risk_cls}" style="margin-top:.75rem">
          <b>Decision band:</b> {band}
        </div>
        """,
        unsafe_allow_html=True,
    )

    t1, t2, t3 = st.tabs(["① Input — Context", "② Processing — Rules", "③ Output — Actions"])
    with t1:
        st.dataframe(pd.DataFrame([rev["txn"]]), use_container_width=True, hide_index=True)
    with t2:
        if rev["hits"]:
            st.dataframe(pd.DataFrame(rev["hits"]), use_container_width=True, hide_index=True)
        else:
            st.success("No AML rules fired — clean path.")
    with t3:
        for a in rev["actions"]:
            st.markdown(f"- {a}")
        if st.button("📁 Open Case", type="primary"):
            try:
                cid = open_case(rev["txn_id"], rev["score"], rev["recommendation"], rev["actions"])
                st.success(f"Case ready · CASE_ID = **{cid}**")
                st.balloons()
            except Exception as e:
                st.error(f"Open Case failed (run sql/02_cases_and_audit.sql first): {e}")

    with st.expander("Key considerations"):
        st.markdown(
            """
            - **T2005** can outrank **T2001** because structuring (CRITICAL) beats raw amount.
            - **T2001** hits wire threshold + high-risk geography.
            - **T1001** is a clean domestic POS control case.
            - **Hack2Skill · Snowflake CoCo CLI Hackathon 2026 – GCC Edition**
            """
        )

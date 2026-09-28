"""Fraud Policy Copilot – Phase 2 Streamlit in Snowflake (SiS).
Hack2Skill · Snowflake CoCo CLI Hackathon 2026 – GCC Edition

Tabs: Review | Fraud ring | Cases
Sanctions: demo inline HIGH_RISK_COUNTRIES only (NOT a live API).
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

# Demo-only sanctions / high-risk geography list — NOT a live OFAC/UN/EU API.
# Documented SKIP in docs/phase2-roadmap.md.
HIGH_RISK_COUNTRIES = {"CY", "RU", "IR", "KP"}

ALLOWED_TRANSITIONS = {
    "OPEN": {"IN_REVIEW", "CLOSED"},
    "IN_REVIEW": {"ESCALATED", "CLOSED"},
    "ESCALATED": {"CLOSED"},
    "CLOSED": set(),
}

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
      .node-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: .75rem; margin: .5rem 0 1rem 0;
      }}
      .node-card {{
        width: 100%; box-sizing: border-box;
        background: linear-gradient(145deg, #0f172a, #1e293b);
        color: #e2e8f0; border-radius: 8px; padding: .85rem 1rem;
        border: 1px solid rgba(41,181,232,.35);
        animation: fadeUp .5s ease-out;
        box-shadow: 0 4px 14px rgba(15,23,42,.25);
        overflow: hidden; word-break: break-word; overflow-wrap: anywhere;
      }}
      .node-card.focus {{
        border-color: {PRIMARY};
        box-shadow: 0 0 0 2px rgba(41,181,232,.45);
      }}
      .node-card .nid {{
        font-weight: 700; color: {PRIMARY}; font-size: .95rem;
      }}
      .node-card .meta {{
        font-size: .75rem; opacity: .85; margin-top: .35rem;
        line-height: 1.35; word-break: break-word; overflow-wrap: anywhere;
      }}
      .node-card .meta .lbl {{
        display: inline-block; min-width: 4.5rem; opacity: .7; font-weight: 600;
      }}
      .edge-pill {{
        display: inline-block; background: #e0f2fe; color: #075985;
        font-size: .65rem; font-weight: 700; padding: .2rem .45rem;
        border-radius: 4px; margin: .2rem .2rem 0 0;
        max-width: 100%; white-space: normal; word-break: break-word;
        line-height: 1.25;
      }}
    </style>
    <div class="hero">
      <span class="badge">Hack2Skill</span>
      <span class="badge">Snowflake CoCo CLI · GCC Edition</span>
      <span class="badge">Phase 2 · Risk / Fraud / Regulatory</span>
      <h1>🛡️ Fraud Policy Copilot</h1>
      <p>Review · Fraud ring · Cases · AML citations · 5 modular CoCo skills</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def _esc(val: Any) -> str:
    return str(val if val is not None else "").replace("'", "''")


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
    hits: list[dict] = []
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
    # Demo sanctions list only — not a live API (see HIGH_RISK_COUNTRIES + roadmap SKIP).
    if country in HIGH_RISK_COUNTRIES:
        add("AML-GEO-05", "High-Risk Geography (demo list)", 30, "HIGH",
            f"Country {country} is in demo HIGH_RISK_COUNTRIES={sorted(HIGH_RISK_COUNTRIES)}; "
            "not a live sanctions feed.")
    if account_type == "PERSONAL" and channel == "WIRE" and amount >= 10000:
        add("AML-PROF-06", "Profile Mismatch", 20, "MEDIUM",
            "Personal accounts used for commercial-scale wires should escalate.")
    return min(100.0, float(sum(h["points"] for h in hits))), hits


@st.cache_data(ttl=60)
def load_txn(txn_id: str):
    safe = _esc(txn_id)
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
        WHERE r.CUSTOMER_ID = '{_esc(row["customer_id"])}'
          AND r.AMOUNT < 1000
          AND r.TXN_TS >= DATEADD('hour', -24, '{row["txn_ts"]}')
          AND r.TXN_ID <> '{safe}'
    """).to_pandas()
    n = int(und.iloc[0]["N"]) if not und.empty else 0
    return row, n


def log_review_audit(txn_id: str, score: float, recommendation: str, hits: list[dict]) -> None:
    tid = _esc(txn_id)
    rules = json.dumps(hits).replace("'", "''")
    try:
        session.sql(f"""
            INSERT INTO REVIEW_AUDIT (TXN_ID, RISK_SCORE, RECOMMENDATION, FIRED_RULES, SOURCE)
            SELECT '{tid}', {score}, '{recommendation}', PARSE_JSON('{rules}'), 'STREAMLIT_PHASE2'
        """).collect()
    except Exception:
        pass


def open_case(txn_id: str, score: float, recommendation: str, actions: list[str]) -> int:
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    payload = json.dumps(actions).replace("'", "''")
    tid = _esc(txn_id)
    session.sql(f"""
        INSERT INTO CASES (TXN_ID, STATUS, PRIORITY, RECOMMENDATION, RISK_SCORE, NEXT_ACTIONS, SOURCE)
        SELECT '{tid}', 'OPEN', '{priority}', '{recommendation}', {score},
               PARSE_JSON('{payload}'), 'STREAMLIT_PHASE2'
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


def customer_from_txn(txn_id: str) -> str | None:
    df = session.sql(f"""
        SELECT CUSTOMER_ID FROM TRANSACTIONS WHERE TXN_ID = '{_esc(txn_id)}' LIMIT 1
    """).to_pandas()
    if df.empty:
        return None
    return str(df.iloc[0]["CUSTOMER_ID"])


def load_ring(focus_customer: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    cid = _esc(focus_customer)
    edges = session.sql(f"""
        SELECT SRC_CUSTOMER, DST_CUSTOMER, EDGE_TYPE, EDGE_KEY
        FROM V_FRAUD_RING_EDGES
        WHERE SRC_CUSTOMER = '{cid}' OR DST_CUSTOMER = '{cid}'
        ORDER BY EDGE_TYPE, SRC_CUSTOMER
    """).to_pandas()
    related = {focus_customer}
    if not edges.empty:
        edges.columns = [c.lower() for c in edges.columns]
        for _, r in edges.iterrows():
            related.add(str(r["src_customer"]))
            related.add(str(r["dst_customer"]))
    ids = ",".join(f"'{_esc(x)}'" for x in sorted(related))
    nodes = session.sql(f"""
        SELECT * FROM V_FRAUD_RING_NODES
        WHERE CUSTOMER_ID IN ({ids})
        ORDER BY CUSTOMER_ID
    """).to_pandas()
    if not nodes.empty:
        nodes.columns = [c.lower() for c in nodes.columns]
    return nodes, edges


def render_node_cards(nodes: pd.DataFrame, edges: pd.DataFrame, focus: str) -> None:
    if nodes.empty:
        st.info("No graph nodes for this customer. Run `sql/04_fraud_ring_graph.sql`.")
        return
    edge_by_cust: dict[str, list[str]] = {}
    if not edges.empty:
        for _, e in edges.iterrows():
            et = str(e.get("edge_type", "")).replace("SHARED_", "").replace("_", " ").title()
            ek = str(e.get("edge_key", ""))
            label = f"{et}: {ek}"
            for key in ("src_customer", "dst_customer"):
                c = str(e[key])
                edge_by_cust.setdefault(c, [])
                if label not in edge_by_cust[c]:
                    edge_by_cust[c].append(label)
    cards = []
    for _, n in nodes.iterrows():
        cid = str(n.get("customer_id", ""))
        focus_cls = " focus" if cid == focus else ""
        name = n.get("full_name") or "—"
        device = n.get("device_id") or "—"
        iban = n.get("iban_last4") or "—"
        cluster = n.get("merchant_cluster") or "—"
        pills = "".join(f'<span class="edge-pill">{p}</span>' for p in edge_by_cust.get(cid, []))
        cards.append(
            f"""<div class="node-card{focus_cls}">
              <div class="nid">{"★ " if cid == focus else ""}{cid}</div>
              <div class="meta">
                <b>{name}</b><br/>
                <span class="lbl">Device</span> {device}<br/>
                <span class="lbl">IBAN</span> ****{iban}<br/>
                <span class="lbl">Cluster</span> {cluster}
              </div>
              <div style="margin-top:.45rem">{pills}</div>
            </div>"""
        )
    st.markdown(f'<div class="node-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def list_cases(status_filter: str) -> pd.DataFrame:
    where = ""
    if status_filter and status_filter != "ALL":
        where = f"WHERE STATUS = '{_esc(status_filter)}'"
    try:
        df = session.sql(f"""
            SELECT CASE_ID, TXN_ID, STATUS, PRIORITY, RECOMMENDATION, RISK_SCORE,
                   ASSIGNEE, NOTES, OPENED_BY, OPENED_AT, UPDATED_AT, SOURCE
            FROM CASES
            {where}
            ORDER BY OPENED_AT DESC
            LIMIT 200
        """).to_pandas()
    except Exception:
        df = session.sql(f"""
            SELECT CASE_ID, TXN_ID, STATUS, PRIORITY, RECOMMENDATION, RISK_SCORE,
                   OPENED_BY, OPENED_AT, UPDATED_AT, SOURCE
            FROM CASES
            {where}
            ORDER BY OPENED_AT DESC
            LIMIT 200
        """).to_pandas()
    if not df.empty:
        df.columns = [c.lower() for c in df.columns]
    return df


def add_comment(case_id: int, body: str) -> None:
    session.sql(f"""
        INSERT INTO CASE_COMMENTS (CASE_ID, BODY)
        SELECT {int(case_id)}, '{_esc(body)}'
    """).collect()
    session.sql(f"""
        INSERT INTO CASE_EVENTS (CASE_ID, TXN_ID, EVENT_TYPE, EVENT_DATA)
        SELECT c.CASE_ID, c.TXN_ID, 'COMMENT_ADDED',
               OBJECT_CONSTRUCT('preview', LEFT('{_esc(body)}', 120))
        FROM CASES c WHERE c.CASE_ID = {int(case_id)}
    """).collect()


def transition_case(case_id: int, new_status: str, assignee: str | None, notes: str | None) -> str:
    cur = session.sql(f"""
        SELECT STATUS, TXN_ID FROM CASES WHERE CASE_ID = {int(case_id)}
    """).to_pandas()
    if cur.empty:
        return "ERROR: case not found"
    old = str(cur.iloc[0]["STATUS"])
    allowed = ALLOWED_TRANSITIONS.get(old, set())
    if new_status not in allowed:
        return f"ERROR: illegal transition {old} → {new_status}"
    set_bits = [f"STATUS = '{_esc(new_status)}'", "UPDATED_AT = CURRENT_TIMESTAMP()"]
    if assignee:
        set_bits.append(f"ASSIGNEE = '{_esc(assignee)}'")
    if notes:
        set_bits.append(f"NOTES = '{_esc(notes)}'")
    session.sql(f"""
        UPDATE CASES SET {', '.join(set_bits)} WHERE CASE_ID = {int(case_id)}
    """).collect()
    tid = _esc(cur.iloc[0]["TXN_ID"])
    session.sql(f"""
        INSERT INTO CASE_EVENTS (CASE_ID, TXN_ID, EVENT_TYPE, EVENT_DATA)
        SELECT {int(case_id)}, '{tid}', 'STATUS_CHANGED',
               OBJECT_CONSTRUCT('from', '{_esc(old)}', 'to', '{_esc(new_status)}')
    """).collect()
    return f"OK: {old} → {new_status}"


def load_comments(case_id: int) -> pd.DataFrame:
    try:
        df = session.sql(f"""
            SELECT COMMENT_ID, BODY, AUTHOR, CREATED_AT
            FROM CASE_COMMENTS
            WHERE CASE_ID = {int(case_id)}
            ORDER BY CREATED_AT DESC
        """).to_pandas()
    except Exception:
        return pd.DataFrame()
    if not df.empty:
        df.columns = [c.lower() for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Demo controls")
    st.caption("Hack2Skill · CoCo CLI · GCC · Phase 2")
    st.markdown("**Skills**")
    st.markdown(
        "1. `get_case_context`  \n"
        "2. `match_policy`  \n"
        "3. `explain_decision`  \n"
        "4. `suggest_next_actions`  \n"
        "5. `map_fraud_ring`"
    )
    st.markdown("---")
    st.caption(
        f"Sanctions: demo list only — `{', '.join(sorted(HIGH_RISK_COUNTRIES))}` "
        "(live API SKIPPED)."
    )

tab_review, tab_ring, tab_cases = st.tabs(["🔎 Review", "🕸 Fraud ring", "📁 Cases"])

# ============================= Review =======================================
with tab_review:
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
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        pick = st.selectbox("Quick pick", ["T2001", "T2005", "T1001", "Custom"], key="rev_pick")
    with c2:
        custom = st.text_input("Custom TXN_ID", value="T2001", key="rev_custom")
    with c3:
        st.write("")
        st.write("")
        run = st.button("▶ Run policy review", type="primary", use_container_width=True)

    txn_id = custom.strip() if pick == "Custom" else pick

    if run:
        pipe = st.empty()
        status = st.empty()
        for i, msg in enumerate([
            ("① Input", "Loading case context…"),
            ("② Processing", "Matching AML policies…"),
            ("③ Output", "Building recommendation…"),
        ]):
            names = ["① Input", "② Processing", "③ Output"]
            steps_html = [
                f'<div class="{"pipestep active" if j <= i else "pipestep"}">{name}</div>'
                for j, name in enumerate(names)
            ]
            pipe.markdown(
                f'<div class="pipeline">{"".join(steps_html)}</div>'
                f'<div class="flowbar"><span></span></div>',
                unsafe_allow_html=True,
            )
            status.info(msg[1])
            time.sleep(0.3)

        txn, under_n = load_txn(txn_id)
        status.empty()
        if not txn:
            st.error(f"No transaction found for `{txn_id}`.")
            pipe.empty()
        else:
            score, hits = score_from_row(txn, under_n)
            rec = recommend(score)
            st.session_state["review"] = {
                "txn_id": txn_id, "txn": txn, "score": score, "hits": hits,
                "recommendation": rec, "actions": next_actions(rec, score),
            }
            log_review_audit(txn_id, score, rec, hits)
            pipe.empty()

    rev = st.session_state.get("review")
    if not rev:
        st.info("Pick **T2001**, **T2005**, or **T1001**, then Run — watch the pipeline animate.")
    else:
        score = rev["score"]
        risk_cls = "risk-hi" if score >= 70 else "risk-mid" if score >= 40 else "risk-lo"
        band = (
            "High — escalate" if score >= 70
            else "Medium — enhanced review" if score >= 40
            else "Low — clear"
        )
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
            if st.button("📁 Open Case", type="primary", key="open_case_btn"):
                try:
                    cid = open_case(
                        rev["txn_id"], rev["score"], rev["recommendation"], rev["actions"]
                    )
                    st.success(f"Case ready · CASE_ID = **{cid}**")
                    st.balloons()
                except Exception as e:
                    st.error(f"Open Case failed (run sql/02 + sql/05 first): {e}")

        with st.expander("Key considerations"):
            st.markdown(
                f"""
                - **T2005** can outrank **T2001** because structuring (CRITICAL) beats raw amount.
                - **T2001** hits wire threshold + high-risk geography (demo list `{', '.join(sorted(HIGH_RISK_COUNTRIES))}`).
                - **T1001** is a clean domestic POS control case.
                - Live sanctions API = **SKIPPED** (Phase 2 roadmap).
                - **Hack2Skill · Snowflake CoCo CLI Hackathon 2026 – GCC Edition**
                """
            )

# ============================= Fraud ring ===================================
with tab_ring:
    st.markdown("#### map_fraud_ring · shared device / IBAN / phone / merchant cluster")
    st.caption(
        "Demo attrs from `CUSTOMER_GRAPH_ATTRS` — no external device or open-banking APIs. "
        "Seed: C003↔C005 DEVICE `DEV-RING-01`; C002↔C005 IBAN_LAST4 `7789`."
    )
    mode = st.radio("Lookup by", ["Customer ID", "Transaction ID"], horizontal=True, key="ring_mode")
    r1, r2 = st.columns([2, 1])
    with r1:
        if mode == "Customer ID":
            focus_in = st.selectbox(
                "Customer",
                ["C005", "C003", "C002", "C001", "C004", "Custom"],
                key="ring_cust_pick",
            )
            custom_cust = st.text_input("Custom CUSTOMER_ID", value="C005", key="ring_cust_custom")
            focus = custom_cust.strip() if focus_in == "Custom" else focus_in
        else:
            txn_pick = st.selectbox(
                "Transaction", ["T2001", "T2005", "T1001", "Custom"], key="ring_txn_pick"
            )
            custom_txn = st.text_input("Custom TXN_ID", value="T2001", key="ring_txn_custom")
            txn_for_ring = custom_txn.strip() if txn_pick == "Custom" else txn_pick
            focus = customer_from_txn(txn_for_ring) or ""
            if not focus:
                st.warning(f"No customer for txn `{txn_for_ring}`.")
    with r2:
        st.write("")
        st.write("")
        map_btn = st.button("🗺 Map ring", type="primary", use_container_width=True, key="map_ring")

    if map_btn and focus:
        try:
            nodes, edges = load_ring(focus)
            st.session_state["ring"] = {"focus": focus, "nodes": nodes, "edges": edges}
        except Exception as e:
            st.error(f"Ring load failed (run sql/04_fraud_ring_graph.sql): {e}")

    ring = st.session_state.get("ring")
    if ring:
        st.markdown(f"**Focus customer:** `{ring['focus']}`")
        render_node_cards(ring["nodes"], ring["edges"], ring["focus"])
        n1, n2 = st.columns(2)
        with n1:
            st.markdown("**Nodes** (`V_FRAUD_RING_NODES`)")
            st.dataframe(ring["nodes"], use_container_width=True, hide_index=True)
        with n2:
            st.markdown("**Edges** (`V_FRAUD_RING_EDGES`)")
            st.dataframe(ring["edges"], use_container_width=True, hide_index=True)
        if not ring["edges"].empty:
            summary = ring["edges"].groupby("edge_type").size().reset_index(name="count")
            st.markdown("**Ring summary**")
            st.dataframe(summary, use_container_width=True, hide_index=True)
        else:
            st.info("No 1-hop edges for this customer.")
    else:
        st.info("Select **C005** (richest demo ring) or a txn, then Map ring.")

# ============================= Cases ========================================
with tab_cases:
    st.markdown("#### Case management · OPEN → IN_REVIEW → ESCALATED → CLOSED")
    filt = st.selectbox(
        "Filter status",
        ["ALL", "OPEN", "IN_REVIEW", "ESCALATED", "CLOSED"],
        key="case_status_filt",
    )
    if st.button("↻ Refresh cases", key="refresh_cases"):
        st.session_state.pop("cases_df", None)

    try:
        cases_df = list_cases(filt)
        st.session_state["cases_df"] = cases_df
    except Exception as e:
        st.error(f"Could not load CASES (run sql/02 + sql/05): {e}")
        cases_df = pd.DataFrame()

    if cases_df is not None and not cases_df.empty:
        st.dataframe(cases_df, use_container_width=True, hide_index=True)
        case_ids = cases_df["case_id"].tolist()
        selected = st.selectbox("Select CASE_ID", case_ids, key="case_select")
        row = cases_df[cases_df["case_id"] == selected].iloc[0]
        cur_status = str(row.get("status", "OPEN"))
        st.markdown(f"Current status: **{cur_status}** · txn `{row.get('txn_id')}`")

        allowed = sorted(ALLOWED_TRANSITIONS.get(cur_status, set()))
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Add comment**")
            body = st.text_area("Comment", key="case_comment_body", height=80)
            if st.button("💬 Add comment", key="add_comment_btn"):
                if not body.strip():
                    st.warning("Comment body required.")
                else:
                    try:
                        add_comment(int(selected), body.strip())
                        st.success("Comment added.")
                    except Exception as e:
                        st.error(f"Comment failed (run sql/05_case_management.sql): {e}")
            comments = load_comments(int(selected))
            if not comments.empty:
                st.dataframe(comments, use_container_width=True, hide_index=True)

        with col_b:
            st.markdown("**Change status**")
            if not allowed:
                st.info("Case is CLOSED (terminal).")
            else:
                new_st = st.selectbox("New status", allowed, key="case_new_status")
                assignee = st.text_input("Assignee (optional)", key="case_assignee")
                notes = st.text_input("Notes (optional)", key="case_notes")
                if st.button("⇄ Transition", type="primary", key="case_transition_btn"):
                    try:
                        msg = transition_case(
                            int(selected),
                            new_st,
                            assignee.strip() or None,
                            notes.strip() or None,
                        )
                        if msg.startswith("OK"):
                            st.success(msg)
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"Transition failed: {e}")
    else:
        st.info("No cases yet — open one from the Review tab, or seed via sql/02.")

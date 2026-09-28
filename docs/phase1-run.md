# Phase 1 runbook

## 1. SQL
In Snowflake worksheet run `sql/02_cases_and_audit.sql`.

## 2. Secrets (local only — do not commit)
```powershell
mkdir app\.streamlit
copy docs\secrets.toml.example app\.streamlit\secrets.toml
# edit password / use PAT as password if your connector expects it
```

## 3. Run Streamlit
```powershell
cd C:\Users\SuhailInayathulla\Documents\fraud-policy-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r app\requirements.txt
streamlit run app\streamlit_app.py
```

Demo IDs: `T2001`, `T2005`, `T1001`.

## 4. Deployed link (Hack2Skill)
Streamlit Community Cloud from the public GitHub repo; add the same secrets in the Cloud dashboard.

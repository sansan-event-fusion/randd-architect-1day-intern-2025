import os

import streamlit as st

from app.views import dashboard_view, search_view

os.environ["BASE_URL"] = "https://circuit-trial.stg.rd.ds.sansan.com"
os.environ["OWN_COMPANY_ID"] = "6185710340"

st.set_page_config(
    page_title="企業間つながり分析検索ツール",
    page_icon="🧊",
    layout="wide",
)

st.title("企業間つながり分析検索ツール")


selected_company = search_view()
if selected_company:
    st.divider()
    dashboard_view(selected_company)

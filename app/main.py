import streamlit as st
from views import search_view, dashboard_view

st.set_page_config(
    page_title="企業間つながり分析検索ツール",
    page_icon="🧊",
    layout="wide",
)

st.title("企業間つながり分析検索ツール")


selected_company = search_view()
if selected_company:
    dashboard_view(selected_company)

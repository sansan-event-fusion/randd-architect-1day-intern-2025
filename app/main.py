import streamlit as st
from dotenv import load_dotenv

from app.views import dashboard_view, search_view

load_dotenv()

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

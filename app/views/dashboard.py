import streamlit as st


def dashboard_view(selected_company):
    st.title(f"{selected_company.name} のダッシュボード")
    st.write(selected_company)

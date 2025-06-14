from pathlib import Path

import streamlit as st

from app.models.company import Company
from app.util import contains_japanese_match


def get_all_companies():
    with Path.open("app/data/companies.csv") as f:
        return [
            Company(
                id=int(line.split(",")[0]),
                name=line.split(",")[1],
                address=line.split(",")[2],
                phone=line.split(",")[3],
            )
            for line in f.readlines()
        ]


def init_session_state():
    if "selected_company" not in st.session_state:
        st.session_state.selected_company = None
    if "company_name" not in st.session_state:
        st.session_state.company_name = ""


def display_search_results(filtered_candidates):
    if filtered_candidates:
        st.write("候補:")
        # 3列のグリッドを作成
        cols = st.columns(10)
        for i, candidate in enumerate(filtered_candidates):
            # 列を循環して使用
            col = cols[i % 10]
            with col:
                if st.button(candidate.name, key=f"btn_{candidate.id}"):
                    st.session_state.selected_company = candidate
                    st.session_state.company_name = candidate.name
                    st.rerun()
    else:
        st.write("一致する候補がありません")


def display_error_messages(user_input):
    if not st.session_state.selected_company and user_input:
        st.warning("候補から企業を選択してください")


def search_view():
    init_session_state()
    candidates = get_all_companies()
    user_input = st.text_input(label="企業名を入力", value=st.session_state.company_name, key="search_input")

    if user_input:
        filtered_candidates = [item for item in candidates if contains_japanese_match(item.name, user_input)]
        display_error_messages(user_input)
        display_search_results(filtered_candidates)

    return st.session_state.selected_company

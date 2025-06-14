import streamlit as st
from util import contains_japanese_match
from models.company import Company

candidates = [
    Company(id=1, name="合同会社森鉱業", address="東京都千代田区永田町1-7-1", phone="03-3581-1111"),
    Company(id=2, name="有限会社井上運輸", address="東京都千代田区永田町1-7-1", phone="03-3581-1111"),
    Company(id=3, name="清水運輸合同会社", address="東京都千代田区永田町1-7-1", phone="03-3581-1111"),
]


def search_view():
    if "selected_company" not in st.session_state:
        st.session_state.selected_company = None
    if "company_name" not in st.session_state:
        st.session_state.company_name = ""

    user_input = st.text_input(label="企業名を入力", value=st.session_state.company_name, key="search_input")

    if user_input:
        filtered_candidates = [item for item in candidates if contains_japanese_match(item.name, user_input)]
        if filtered_candidates:
            st.write("候補:")
            for candidate in filtered_candidates:
                if st.button(candidate.name, key=f"btn_{candidate.id}"):
                    st.session_state.selected_company = candidate
                    st.session_state.company_name = candidate.name
                    st.rerun()
        else:
            st.write("一致する候補がありません")

    if st.session_state.selected_company:
        if st.session_state.selected_company:
            pass
        elif user_input:
            st.warning("候補から企業を選択するか、正確な企業名を入力してください")
        else:
            st.error("企業名を入力してください")

    return st.session_state.selected_company

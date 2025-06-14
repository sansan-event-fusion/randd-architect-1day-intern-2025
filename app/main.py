import streamlit as st
from util import contains_japanese_match

st.title("企業間つながり分析検索ツール")
candidates = ["合同会社森鉱業", "有限会社井上運輸", "清水運輸合同会社"]

if "selected_company" not in st.session_state:
    st.session_state.selected_company = None

col1, col2 = st.columns([3, 1])  # 比率を3:1に設定
with col1:
    user_input = st.text_input(label="企業名を入力", value=st.session_state.selected_company)

if user_input:
    filtered_candidates = [item for item in candidates if contains_japanese_match(item, user_input)]
    if filtered_candidates:
        st.write("候補:")
        for candidate in filtered_candidates:
            if st.button(candidate, key=f"btn_{candidate}"):
                st.session_state.selected_company = candidate
                st.rerun()
    else:
        st.write("一致する候補がありません")

with col2:
    st.write("")
    st.write("")
    search_button = st.button("検索", type="primary")

if search_button:
    if st.session_state.selected_company:
        st.success(f"'{st.session_state.selected_company}' で検索を実行しました")
    elif user_input:
        st.warning("候補から企業を選択するか、正確な企業名を入力してください")
    else:
        st.error("企業名を入力してください")

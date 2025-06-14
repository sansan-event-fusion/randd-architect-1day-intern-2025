import json

import streamlit as st

# JSONファイルを読み込む
with open("cand.json", encoding="utf-8") as f:
    cand_data = json.load(f)

# StreamlitのUI
st.title("候補者検索")

user_name = st.text_input("ユーザー名")
company_name = st.text_input("会社名")

if st.button("検索"):
    key = user_name + "_" + company_name
    if key in cand_data:
        st.success(f"見つかりました: {user_name} {company_name}")
        for cand in cand_data[key]:
            with st.expander(cand["full_name"]):
                st.write(f"会社名: {cand['company_name']}")
                st.write(f"住所: {cand.get('address', '不明')}")
                st.write(f"電話番号: {cand.get('phone_number', '不明')}")
        """
        for cand in cand_data[key]:
            st.write("### 候補者情報")
            st.write(f"**名前:** {cand['full_name']}")
            st.write(f"**会社名:** {cand['company_name']}")
            st.markdown("---")
        """
    else:
        st.warning("一致するデータが見つかりませんでした。")

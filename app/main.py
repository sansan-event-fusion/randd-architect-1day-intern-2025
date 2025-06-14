import pandas as pd
import requests
import streamlit as st

# タイトル
st.title("Sansan Circuit Trial")

API_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/"
cards_endpoint = "cards"
contacts_endpoint = "contacts"
headers = {"Content-Type": "application/json"}

page = st.selectbox("アプリ選択", ["営業先リコメンドアプリ", "名刺交換履歴アプリ", "A"])

if page == "営業先リコメンドアプリ":
    st.write("営業先リコメンドアプリを選択しました。")
    response = requests.get(API_URL + cards_endpoint + "/?offset=0&limit=10000", headers=headers, timeout=2000)
    if response.status_code == 200:
        data = response.json()
        cards_data = pd.DataFrame(data)

        # 空選択を含むユーザーセレクトボックス
        options = ["", *(cards_data["full_name"] + "(" + cards_data["user_id"] + ")").tolist()]
        # ユーザー選択のマルチセレクトボックス
        selected_user_list = st.multiselect("ユーザーを選択してください", options, max_selections=1)
        if selected_user_list:
            selected_user = selected_user_list[0]
            selected_user_id = selected_user.split("(")[-1].strip(")")
            # 選択されたユーザーのカード情報を取得
            user_cards = cards_data[cards_data["user_id"] == selected_user_id]
            if not user_cards.empty:
                st.write("選択されたユーザーのカード情報")
                st.dataframe(user_cards)
                # 類似ユーザーのリコメンド
                sim_url = f"{API_URL}cards/{selected_user_id}/similar_top10_users"
                sim_response = requests.get(sim_url, headers=headers, timeout=2000)

                if sim_response.status_code == 200:
                    sim_data = sim_response.json()
                    sim_df = pd.DataFrame(sim_data)
                    st.subheader("営業先リコメンド候補")
                    st.dataframe(sim_df)
                else:
                    st.error(f"類似ユーザー取得エラー: {sim_response.status_code}")
        else:
            st.write("ユーザーが選択されていません。")
        st.subheader("全ユーザーのカード情報")
        st.dataframe(cards_data)

    else:
        st.error(f"APIリクエストに失敗しました。ステータスコード: {response.status_code}")
        st.error("詳細: " + response.text)
elif page == "名刺交換履歴アプリ":
    st.write("名刺交換履歴アプリを選択しました。")
    cards_response = requests.get(API_URL + cards_endpoint + "/?offset=0&limit=3000", headers=headers, timeout=2000)
    contacts_response = requests.get(
        API_URL + contacts_endpoint + "/?offset=0&limit=3000", headers=headers, timeout=2000
    )
    if cards_response.status_code == 200 and contacts_response.status_code == 200:
        cards_data = pd.DataFrame(cards_response.json())
        contacts_data = pd.DataFrame(contacts_response.json())

        # 空選択を含むユーザーセレクトボックス
        options = ["", *(cards_data["full_name"] + "(" + cards_data["user_id"] + ")").tolist()]
        selected_user_list = st.multiselect("ユーザーを選択してください", options, max_selections=1)
        if selected_user_list:
            selected_user = selected_user_list[0]
            selected_user_id = selected_user.split("(")[-1].strip(")")
            # 選択されたユーザーの名刺交換履歴を取得
            user_contacts = contacts_data[contacts_data["user_id"] == selected_user_id]
            if not user_contacts.empty:
                st.write("選択されたユーザーの名刺交換履歴")
                st.dataframe(user_contacts)
            else:
                st.write("選択されたユーザーの名刺交換履歴はありません。")
        else:
            st.write("ユーザーが選択されていません。")

        st.subheader("全ユーザーの名刺交換履歴")
        st.dataframe(contacts_data)

    else:
        st.error(
            f"APIリクエストに失敗しました。ステータスコード: {cards_response.status_code}, {contacts_response.status_code}"
        )
        st.error("詳細: " + cards_response.text + contacts_response.text)

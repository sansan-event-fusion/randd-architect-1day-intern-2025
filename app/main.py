from pathlib import Path
import pandas as pd
import streamlit as st
import requests

# タイトル
st.title("営業先の新規開拓")

# ユーザーに user_id を入力してもらう
input_user_id = st.text_input("あなたのユーザーIDを入力してください")
#日付選択
input_date = st.date_input("いつ以降のデータを取得しますか？", value=pd.to_datetime("2023-01-01"))

# ボタンを押したら API を呼び出す
if st.button("検索"):
    # 入力された user_id を使用して API を呼び出す　limitを10に設定
    owner_url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{input_user_id}?limit=10&start_date={input_date}"
    
    try:
        response = requests.get(owner_url)
        response.raise_for_status()  # エラーハンドリング

        data = response.json()
        df = pd.DataFrame(data)
        user_ids = df["user_id"].unique()  # ユニークな user_id を取得

        user_info_list = []
        for user_id in user_ids:
            user_info_url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}"
            try:
                user_info_response = requests.get(user_info_url)
                user_info_response.raise_for_status()  # エラーハンドリング

                user_info_data = user_info_response.json()
                user_info_list.append(user_info_data[0])
            except requests.exceptions.RequestException as e:
                st.error(f"ユーザー情報の取得に失敗しました: {e}")
        
        # ユーザー情報を DataFrame に変換
        user_info_df = pd.DataFrame(user_info_list)
        # ユーザー情報を表示
        st.subheader("期間中にやりとりをしたユーザー情報")
        st.dataframe(user_info_df)

        #取得したuser_idから、類似するユーザーの情報を取得
        for user_id in user_ids:
            similer_user_url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}/similar_top10_users"
            try:
                similer_response = requests.get(similer_user_url)
                similer_response.raise_for_status()  # エラーハンドリング

                similer_data = similer_response.json()
                similer_df = pd.DataFrame(similer_data)
                
                target_user = user_info_df[user_info_df["user_id"] == user_id]
                user_name = target_user["full_name"].values[0] if not target_user.empty else "不明"
                st.subheader(f"ユーザーID: {user_name} ({user_id}) の類似ユーザー情報")
                # 類似ユーザーの情報を表示
                st.dataframe(similer_df)
            except requests.exceptions.RequestException as e:
                st.error(f"類似ユーザーの情報取得に失敗しました: {e}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"APIリクエストに失敗しました: {e}")


import pandas as pd
import requests
import streamlit as st


def fetch_api_data(url: str) -> pd.DataFrame:
    """指定されたURLからAPIデータを取得してDataFrameに変換"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"API呼び出しエラー: {e}")

def get_user_id_from_full_name(full_name: str) -> str | None:
    """氏名からuser_idを取得"""
    try:
        df = fetch_api_data("https://circuit-trial.stg.rd.ds.sansan.com/api/cards/")
        if df is not None and not df.empty:
            user_row = df[df["full_name"] == full_name]
            if not user_row.empty:
                return str(user_row.iloc[0]["user_id"])
        st.error(f"氏名 {full_name} に対応するuser_idが見つかりませんでした")
        return None
    except Exception as e:
        st.error(f"user_id取得エラー: {e}")
        return None

def fetch_similar_top10_users(user_id: str) -> pd.DataFrame:
    api_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + user_id + "/similar_top10_users"
    return fetch_api_data(api_url)

# 氏名からuser_idを取得する場合
full_name = st.text_input("氏名を入力してください")

if full_name:
    user_id = get_user_id_from_full_name(full_name)
    if user_id:
        similar_top10_users = fetch_similar_top10_users(user_id)
        st.dataframe(similar_top10_users)

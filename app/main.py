import pandas as pd
import requests
import streamlit as st

# タイトル
st.title("サンプルアプリ")

def fetch_api_data(url: str) -> pd.DataFrame:
    """指定されたURLからAPIデータを取得してDataFrameに変換"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"API呼び出しエラー: {e}")

def fetch_similar_top10_users(user_id: str) -> pd.DataFrame:
    api_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + user_id + "/similar_top10_users"
    return fetch_api_data(api_url)

# user_idの入力
user_id = st.text_input("User ID を入力してください", value="1")

if user_id:
    similar_top10_users = fetch_similar_top10_users(user_id)
    st.dataframe(similar_top10_users)

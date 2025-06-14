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

cards = fetch_api_data("https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=100")
st.dataframe(cards)
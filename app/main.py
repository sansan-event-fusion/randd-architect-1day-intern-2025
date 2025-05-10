import streamlit as st
import requests
import pandas as pd

# タイトル
st.title("名刺データ")

url = "https://circuit-trial.stg.rd.ds.sansan.com/api/"

# GETリクエスト
response = requests.get(url + "cards/?offset=0&limit=100", timeout=10)

# JSONレスポンスを辞書として取得
res_json = response.json()

# DataFrameに変換（空なら空のテーブル）
df = pd.DataFrame(res_json)

# 表示
st.dataframe(df)

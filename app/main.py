from pathlib import Path

import pandas as pd
import streamlit as st

import requests

# タイトル
st.title("名刺データ")

url = “https://circuit-trial.stg.rd.ds.sansan.com/api/“

response = requests.get(url + "cards/?offset=0&limit=100", json=data)

df = response.json()

# path = Path(__file__).parent / "dummy_data.csv"

# df_dummy = pd.read_csv(path, dtype=str)

st.dataframe(df)

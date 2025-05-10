from pathlib import Path
from typing import List

import pandas as pd
import requests
import streamlit as st
from api import BuisinessCardAPI
from datatype import BusinessCard, ExchangeHistory

# タイトル
st.title("mattsunkunアプリ")

# API_BASE_PATH =

# path = Path(__file__).parent / "dummy_data.csv"
# df_dummy = pd.read_csv(path.as_uri(), dtype=str)

# st.dataframe(df_dummy)
businessCardAPI = BuisinessCardAPI("https://circuit-trial.stg.rd.ds.sansan.com/api")

print("asdf")
st.title("カードAPIにアクセスする")

# if st.button("カード情報を取得する"):
try:
    cards = businessCardAPI.get_similar_users("9230809757")
    for card in cards:
        st.write(f"名前: {card.full_name}")
        st.write(f"会社名: {card.company_name}")
        st.write(f"役職: {card.position}")
        st.write(f"住所: {card.address}")
        st.write(f"電話番号: {card.phone_number}")
        st.markdown("---")

except Exception as e:
    print(f"error: {e}")
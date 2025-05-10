import json
import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(
    Path(__file__).parent.parent / ".env"
)

API_KEY = os.getenv("API_KEY")
HEALTH_API_URL = os.getenv("HEALTH_API_URL")
CARDS_API_URL = os.getenv("CARDS_API_URL")
CONTACTS_API_URL = os.getenv("CONTACTS_API_URL")
st.set_page_config(
    page_title="サンプルアプリ",
    page_icon=":guardsman:",
    layout="wide",
)
# サイドバー
# タイトル
st.title("サンプルアプリ")


st.write("APIからデータを取得中...")
# APIからデータを取得
response = requests.get(CARDS_API_URL, timeout=5)
if response.status_code == 200:
    data = json.loads(response.text)
    st.write("データ取得成功")
    st.write(data)
else:
    st.write("データ取得失敗")
    st.write(f"Status Code: {response.status_code}")
    st.write(f"Response: {response.text}")

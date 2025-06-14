import pandas as pd
import requests
import streamlit as st

# タイトル
st.title("テスト")

# テキストボックス（文字列入力）
user_id = st.text_input("user_idを入力してください")

# ボタンを押したときに、入力値を使って処理を実行
if st.button("実行"):
    if user_id:
        st.write(f"こんにちは、{user_id}さん！")
        # ここに任意の処理を記述（例: 検索、計算など）
        url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}/similar_top10_users"
        response = requests.get(url)
        results: list[dict] = response.json()
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.warning("user_idを入力してください。")

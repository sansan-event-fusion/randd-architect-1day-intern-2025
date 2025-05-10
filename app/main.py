import random

import requests
import streamlit as st


# ユーザを一人選ぶ
def get_random_user():
    # 名刺の総数を取得
    url_count_buisiness_card = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count"
    response_count_buisiness_card = requests.get(url_count_buisiness_card)
    count_buisiness_card = int(response_count_buisiness_card.content)

    # ユーザをランダムに選ぶ
    user_index = random.randint(0, count_buisiness_card - 1)
    url_user_card = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset={user_index}&limit=1"
    response_user_card = requests.get(url_user_card)
    user_card = response_user_card.json()[0]
    user_id = user_card["user_id"]
    return user_id


# タイトル
st.title("ランダムid")
a_id = get_random_user()
st.write(a_id)

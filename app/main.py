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


def get_surrounding_users(owner_id, entire_limit=200, selection_limit=10):
    # 指定ユーザの周辺ユーザを取得
    url_surrounding_users = (
        f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{owner_id}?offset=0&limit={entire_limit}"
    )
    response_surrounding_users = requests.get(url_surrounding_users)
    surrounding_users = response_surrounding_users.json()
    surrounding_user_ids = {user["user_id"]: 0 for user in surrounding_users}
    # 各ユーザに対して保有名刺数を取得
    for surrounding_user_id in surrounding_user_ids:
        url_count_buisiness_card = (
            f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count?owner_user_id={surrounding_user_id}"
        )
        response_count_buisiness_card = requests.get(url_count_buisiness_card)
        count_buisiness_card = int(response_count_buisiness_card.content)
        surrounding_user_ids[surrounding_user_id] = count_buisiness_card

    # 名刺の多い順にソート
    sorted_surrounding_user_ids = sorted(surrounding_user_ids.keys(), key=lambda x: x[1], reverse=True)
    # 上位 {min(selection_limit, len(surrounding_users))} 人を取得
    selection_num = min(selection_limit, len(surrounding_user_ids))
    selected_surrounding_user_ids = sorted_surrounding_user_ids[:selection_num]

    return selected_surrounding_user_ids


# タイトル
st.title("ランダムid")
a_id = get_random_user()
surrounding_users = get_surrounding_users(a_id)
st.write(a_id)
st.write(surrounding_users)

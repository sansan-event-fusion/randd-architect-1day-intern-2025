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


def get_approachable_users(surrounding_user_ids, entire_limit=200, dict_limit=1000, selection_limit=20):
    # アプローチ可能なユーザ辞書を用意
    approachable_user_dict: dict[str, int] = {}
    # 各ユーザに対してアプローチ可能なユーザを取得
    for surrounding_user_id in surrounding_user_ids:
        url_approachable_users = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{surrounding_user_id}?offset=0&limit={entire_limit}"
        response_approachable_users = requests.get(url_approachable_users)
        sub_approachable_users = response_approachable_users.json()
        sub_approachable_users_ids = {user["user_id"]: 0 for user in sub_approachable_users}
        # 辞書にあるかどうかを確認し，あればカウントをインクリメント
        for approachable_user_id in sub_approachable_users_ids:
            if approachable_user_id in approachable_user_dict:
                approachable_user_dict[approachable_user_id] += 1
            # 辞書のサイズが上限未満なら，追加可能
            elif len(approachable_user_dict) < dict_limit:
                approachable_user_dict[approachable_user_id] = 1
    # 既にsurrounding_user_idsにいるユーザは除外
    for surrounding_user_id in surrounding_user_ids:
        approachable_user_dict.pop(surrounding_user_id, None)

    # 名刺の多い順にソート
    sorted_approachable_user_ids_with_count = sorted(approachable_user_dict.items(), key=lambda x: x[1], reverse=True)
    # 上位 {min(selection_limit, len(approachable_user_dict))} 人を取得
    selection_num = min(selection_limit, len(approachable_user_dict))
    selected_approachable_user_ids_with_count = sorted_approachable_user_ids_with_count[:selection_num]
    return selected_approachable_user_ids_with_count


# タイトル
st.title("ランダムid")
a_id = get_random_user()
surrounding_users = get_surrounding_users(a_id)
approachable_users = get_approachable_users(surrounding_users)
st.write(a_id)
st.write(surrounding_users)
st.write(approachable_users)

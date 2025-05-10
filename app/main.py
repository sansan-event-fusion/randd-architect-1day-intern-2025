import random

import requests
import streamlit as st


# ユーザを一人選ぶ
def get_random_user():
    # 名刺の総数を取得
    url_count_business_card = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count"
    response_count_business_card = requests.get(url_count_business_card, timeout=10)
    count_business_card = int(response_count_business_card.content)

    # ユーザをランダムに選ぶ
    user_index = random.randint(0, count_business_card - 1)
    url_user_card = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset={user_index}&limit=1"
    response_user_card = requests.get(url_user_card, timeout=10)
    user_card = response_user_card.json()[0]
    user_id = user_card["user_id"]
    return user_id, user_card["full_name"], user_card["company_name"]


def get_surrounding_users(owner_id, entire_limit=100):
    # 指定ユーザの周辺ユーザを100人取得
    url_surrounding_users = (
        f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{owner_id}?offset=0&limit={entire_limit}"
    )
    response_surrounding_users = requests.get(url_surrounding_users, timeout=10)
    surrounding_users = response_surrounding_users.json()
    surrounding_user_ids = [user["user_id"] for user in surrounding_users]

    return surrounding_user_ids


def get_approachable_users(surrounding_user_ids, entire_limit=100, selection_limit=20):
    # アプローチ可能なユーザ辞書を用意
    approachable_user_dict: dict[str, int] = {}
    # 各ユーザに対してアプローチ可能なユーザを取得
    for surrounding_user_id in surrounding_user_ids:
        url_approachable_users = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{surrounding_user_id}?offset=0&limit={entire_limit}"
        response_approachable_users = requests.get(url_approachable_users, timeout=10)
        sub_approachable_users = response_approachable_users.json()
        sub_approachable_users_ids = [user["user_id"] for user in sub_approachable_users]
        # 辞書にあるかどうかを確認, あればカウントをインクリメント
        for approachable_user_id in sub_approachable_users_ids:
            if approachable_user_id in approachable_user_dict:
                approachable_user_dict[approachable_user_id] += 1
            else:
                approachable_user_dict[approachable_user_id] = 1
    # 既にsurrounding_user_idsにいるユーザは除外
    for surrounding_user_id in surrounding_user_ids:
        approachable_user_dict.pop(surrounding_user_id, None)

    # 名刺の多い順にソート
    sorted_approachable_user_ids_with_count = sorted(approachable_user_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_approachable_user_ids_with_count[:selection_limit]


def make_approachable_user_table(approachable_users):
    # アプローチ可能なユーザのテーブルを作成
    table_data = []
    for user_id, count in approachable_users:
        url_user_card = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}"
        response_user_card = requests.get(url_user_card, timeout=10)
        user_card = response_user_card.json()[0]
        table_data.append(
            {"name": user_card["full_name"], "企業": user_card["company_name"], "知り合いとの繋がり数": count}
        )
    return table_data


a_id, a_name, a_company = get_random_user()
surrounding_users = get_surrounding_users(a_id)
approachable_users = get_approachable_users(surrounding_users)
# テーブルデータとして表示
table_df = make_approachable_user_table(approachable_users)


st.title("これから繋がるべきユーザ選抜🔥")

st.subheader("あなたの名刺")
st.markdown(f"**{a_name}**  \n{a_company}")

st.markdown("---")  # 区切り線

# アプローチ候補
st.subheader("アプローチ候補一覧📋 ")
st.table(table_df)

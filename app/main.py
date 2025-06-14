from pathlib import Path

import pandas as pd
import requests
import streamlit as st

url_cards = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
url_contacts = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/"


def main():
    # タイトル
    st.title("サンプルアプリ")

    get_user_info_by_id(1471907357)

    st.subheader("名前からユーザーIDを検索")
    name_input = st.text_input("名前を入力してください:", "")

    if name_input:
        user_id_result = search_user_by_name(name_input)
        if not user_id_result:
            st.error("該当するユーザーが見つかりませんでした")

    user_id_input = st.text_input("User IDを入力してください:", "")
    if user_id_input:
        get_exchanges(int(user_id_input))


def get_exchanges(user_id):

    params = {"offset": 0, "limit": 100}
    response = requests.get(f"{url_contacts}{user_id}", params=params)
    if response.status_code == 200:

        df = pd.DataFrame(response.json())
        exchange_num = df.shape[0]
        st.text(f"名刺交換回数{exchange_num}回")

        most_recent_person = recent_exchanges(df)
        create_ranking(df)
        get_similar_person(most_recent_person)

        return True
    else:
        st.error(f"APIリクエスト失敗: {response.status_code}")
        return False


def get_user_info_by_id(user_id):
    response = requests.get(f"{url_cards}{user_id}")
    if response.status_code == 200:
        user_info = response.json()
        if user_info and len(user_info) > 0:
            return user_info[0]  # 全ての情報を返すように修正
        return None
    else:
        st.error(f"APIリクエスト失敗: {response.status_code}")
        return None


def recent_exchanges(df):
    df["created_at"] = pd.to_datetime(df["created_at"])
    df_sorted = df.sort_values("created_at", ascending=False)

    # 最近の交換相手（最新10件）
    st.subheader("最近の名刺交換相手")
    recent_exchanges = df_sorted[["user_id", "company_id", "created_at"]].head(10)

    # 各user_idの詳細情報を取得して名前と会社名を表示
    detailed_exchanges = []
    for _, row in recent_exchanges.iterrows():
        user_id = row["user_id"]
        user_info = get_user_info_by_id(user_id)

        if user_info:
            detailed_exchanges.append(
                {
                    "full_name": user_info.get("full_name", "不明"),
                    "company_name": user_info.get("company_name", "不明"),
                    "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M"),
                }
            )
        else:
            detailed_exchanges.append(
                {
                    "full_name": "不明",
                    "company_name": "不明",
                    "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M"),
                }
            )

    if detailed_exchanges:
        df_detailed = pd.DataFrame(detailed_exchanges)
        st.dataframe(df_detailed)

    most_recent_person = recent_exchanges.iloc[0]["user_id"]
    return most_recent_person


def create_ranking(df):
    # 会社別のランキングも作成
    company_ranking = df["company_id"].value_counts().reset_index()
    company_ranking.columns = ["company_id", "exchange_count"]
    company_ranking.index = company_ranking.index + 1

    st.subheader("会社別名刺交換ランキング")
    st.dataframe(company_ranking.head(10))


def get_similar_person(user_id):
    response = requests.get(f"{url_cards}{user_id}/similar_top10_users")
    if response.status_code == 200:
        similar_users = response.json()

        if similar_users and len(similar_users) > 0:
            similar_user_data = []
            for user in similar_users:
                similar_user_data.append(
                    {
                        "user_id": user.get("user_id"),
                        "full_name": user.get("full_name", "不明"),
                        "company_name": user.get("company_name", "不明"),
                        "position": user.get("position", "不明"),
                        "similarity": user.get("similarity", 0),
                    }
                )

            st.subheader("おすすめ名刺交換人物")
            df_similar = pd.DataFrame(similar_user_data)
            st.dataframe(df_similar[["full_name", "company_name", "position"]])
        else:
            st.info("類似ユーザーが見つかりませんでした")
    else:
        st.error(f"APIリクエスト失敗: {response.status_code}")


def search_user_by_name(name):
    params = {"offset": 0, "limit": 100}

    response = requests.get(url_cards, params=params)
    if response.status_code == 200:
        users = response.json()
        if users and len(users) > 0:

            matching_users = []
            for user in users:
                full_name = user.get("full_name", "")
                if name in full_name:  # 部分一致検索
                    matching_users.append(user)

            if matching_users:
                df_candidates = pd.DataFrame(matching_users)
                st.subheader(f"'{name}'で検索した結果:")
                st.dataframe(df_candidates[["user_id", "full_name", "company_name", "position"]])

                # 最初にマッチしたユーザーのIDを返す
                return matching_users[0].get("user_id")
            else:
                return False
    return False


if __name__ == "__main__":
    main()


import pandas as pd
import requests
import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph


def fetch_api_data(url: str) -> pd.DataFrame:
    """指定されたURLからAPIデータを取得してDataFrameに変換"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"API呼び出しエラー: {e}")

def get_user_id_from_full_name(full_name: str) -> str | None:
    """氏名からuser_idを取得"""
    try:
        cards_df = fetch_api_data("https://circuit-trial.stg.rd.ds.sansan.com/api/cards/")
        if cards_df is not None and not cards_df.empty:
            user_row = cards_df[cards_df["full_name"] == full_name]
            if not user_row.empty:
                return str(user_row.iloc[0]["user_id"])
            st.error(f"氏名 {full_name} に対応するuser_idが見つかりませんでした")
            return None
        st.error(f"氏名 {full_name} に対応するuser_idが見つかりませんでした")
        return None
    except (KeyError, ValueError, AttributeError) as e:
        st.error(f"user_id取得エラー: {e}")
        return None

def get_full_name_from_user_id(user_id: str) -> str:
    """user_idから氏名を取得"""
    try:
        card_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + user_id
        cards_df = fetch_api_data(card_url)
        if cards_df is not None and not cards_df.empty:
            return str(cards_df["full_name"].iloc[0])
        return f"Unknown ({user_id})"
    except (KeyError, ValueError, AttributeError):
        return f"Unknown ({user_id})"

def fetch_similar_top10_users(user_id: str) -> pd.DataFrame:
    api_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + user_id + "/similar_top10_users"
    return fetch_api_data(api_url)

# 氏名からuser_idを取得する場合
full_name = st.text_input("氏名を入力してください")

if full_name:
    user_id = get_user_id_from_full_name(full_name)
    if user_id:
        similar_top10_users_df = fetch_similar_top10_users(user_id)
        st.dataframe(similar_top10_users_df)

        # コンタクト履歴を取得
        contact_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/" + user_id
        contact_df = fetch_api_data(contact_url)

        # similar_top10_users_dfのuser_idと一致するcontact_dfのエントリを表示
        if contact_df is not None and not contact_df.empty and not similar_top10_users_df.empty:
            similar_user_ids = similar_top10_users_df["user_id"].tolist()
            contact_user_ids = contact_df["user_id"].tolist()
            matching_contacts = contact_df[contact_df["user_id"].isin(similar_user_ids)]

            # コンタクト履歴のない類似ユーザーを表示
            no_contact_user_ids = [uid for uid in similar_user_ids if uid not in contact_user_ids]
            if no_contact_user_ids:
                st.subheader("あなたとのコンタクト履歴のない類似ユーザー")
                st.write(no_contact_user_ids)

                # グラフ表示
                st.subheader("コンタクト履歴のない類似ユーザーとの関係図")
                current_user_name = get_full_name_from_user_id(user_id)
                nodes = [Node(id=user_id, label=f"{current_user_name}", color="#FF6B6B")]
                edges = []

                for no_contact_id in no_contact_user_ids:
                    similar_user_name = get_full_name_from_user_id(no_contact_id)
                    nodes.append(Node(id=no_contact_id, label=f"{similar_user_name}", color="#4ECDC4"))
                    edges.append(Edge(source=user_id, target=no_contact_id, label="類似", color="#95A5A6"))

                config = Config(width=800, height=600, directed=False, physics=True, hierarchical=False)
                agraph(nodes=nodes, edges=edges, config=config)


        st.subheader("あなたの全コンタクト履歴")
        st.dataframe(contact_df)

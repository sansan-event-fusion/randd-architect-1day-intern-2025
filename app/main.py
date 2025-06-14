
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

def get_user_details(user_id: str) -> dict:
    """user_idからユーザー詳細情報を取得"""
    try:
        card_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + user_id
        cards_df = fetch_api_data(card_url)
        if cards_df is not None and not cards_df.empty:
            return {
                "full_name": str(cards_df["full_name"].iloc[0]),
                "position": str(cards_df.get("position", ["N/A"]).iloc[0]),
                "company_name": str(cards_df.get("company_name", ["N/A"]).iloc[0]),
                "address": str(cards_df.get("address", ["N/A"]).iloc[0]),
                "phone_number": str(cards_df.get("phone_number", ["N/A"]).iloc[0])
            }
        return {
            "full_name": f"Unknown ({user_id})",
            "position": "N/A",
            "company_name": "N/A",
            "address": "N/A",
            "phone_number": "N/A"
        }
    except (KeyError, ValueError, AttributeError):
        return {
            "full_name": f"Unknown ({user_id})",
            "position": "N/A",
            "company_name": "N/A",
            "address": "N/A",
            "phone_number": "N/A"
        }

def fetch_similar_top10_users(user_id: str) -> pd.DataFrame:
    api_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + user_id + "/similar_top10_users"
    return fetch_api_data(api_url)

# 氏名からuser_idを取得する場合
full_name = st.text_input("氏名を入力してください")

if full_name:
    user_id = get_user_id_from_full_name(full_name)
    if user_id:
        similar_top10_users_df = fetch_similar_top10_users(user_id)

        # コンタクト履歴を取得
        contact_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/" + user_id
        contact_df = fetch_api_data(contact_url)

        # similar_top10_users_dfのuser_idと一致するcontact_dfのエントリを表示
        if contact_df is not None and not contact_df.empty and not similar_top10_users_df.empty:
            similar_user_ids = similar_top10_users_df["user_id"].tolist()
            contact_user_ids = contact_df["user_id"].tolist()
            matching_contacts = contact_df[contact_df["user_id"].isin(similar_user_ids)]

            # すべての類似ユーザーとのグラフ表示
            st.subheader("すべての類似ユーザーとの関係図")
            current_user_name = get_full_name_from_user_id(user_id)
            nodes = [Node(id=user_id, label=f"{current_user_name}", color="#FF6B6B")]
            edges = []

            for similar_id in similar_user_ids:
                similar_user_name = get_full_name_from_user_id(similar_id)

                if similar_id in contact_user_ids:
                    # コンタクト履歴あり
                    nodes.append(Node(id=similar_id, label=f"{similar_user_name}"))
                    edges.append(Edge(source=user_id, target=similar_id, label="コンタクト済み", width = 3))
                else:
                    # コンタクト履歴なし
                    nodes.append(Node(id=similar_id, label=f"{similar_user_name}"))

            config = Config(width=800, height=600, directed=False, physics=True, hierarchical=False)
            return_value = agraph(nodes=nodes, edges=edges, config=config)

            # ノードがクリックされた場合の詳細表示
            if return_value:
                clicked_node_id = return_value
                if isinstance(clicked_node_id, str):
                    st.subheader("選択されたユーザーの詳細情報")
                    user_details = get_user_details(clicked_node_id)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**氏名**: {user_details['full_name']}")
                        st.write(f"**役職**: {user_details['position']}")
                        st.write(f"**会社名**: {user_details['company_name']}")
                    with col2:
                        st.write(f"**住所**: {user_details['address']}")
                        st.write(f"**電話番号**: {user_details['phone_number']}")

                    # コンタクト状況の表示
                    if clicked_node_id in contact_user_ids:
                        st.success("✅ コンタクト済み")
                    else:
                        st.info("📝 未コンタクト - コンタクトを検討してみませんか？")


        # st.subheader("あなたの全コンタクト履歴")
        # st.dataframe(contact_df)

from typing import Any

import pandas as pd
import requests
import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph


def get_business_cards(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    """ビジネスカードを取得する関数"""
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
    params = {"offset": offset, "limit": limit}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def get_similar_users(user_id: int) -> list[dict[str, Any]]:
    """似ているユーザーを取得する関数"""
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}/similar_top10_users"

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    st.title("ビジネスカード表示アプリ")

    # サイドバーにデータ取得設定を追加
    st.sidebar.header("データ取得設定")
    limit = st.sidebar.slider("表示件数", 1, 50, 10)
    offset = st.sidebar.number_input("オフセット", 0, 1000, 0)

    # APIからデータを取得
    with st.spinner("データを取得中..."):
        cards = get_business_cards(offset=offset, limit=limit)

    # DataFrameに変換
    df_cards = pd.DataFrame(cards)

    # データ表示
    st.subheader(f"ビジネスカード一覧 (全{len(df_cards)}件)")
    st.dataframe(df_cards)

    if not df_cards.empty:
        st.subheader("詳細情報")
        selected_name: str = st.selectbox("詳細を表示するカードを選択", options=df_cards["full_name"].tolist())

        # 選択されたカードの詳細を表示
        selected_user: dict[str, Any] = df_cards[df_cards["full_name"] == selected_name].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**氏名:** {selected_user['full_name']}")
            st.markdown(f"**役職:** {selected_user['position']}")
            st.markdown(f"**会社名:** {selected_user['company_name']}")
        with col2:
            st.markdown(f"**住所:** {selected_user['address']}")
            st.markdown(f"**電話番号:** {selected_user['phone_number']}")
            st.markdown(f"**ユーザーID:** {selected_user['user_id']}")
            st.markdown(f"**会社ID:** {selected_user['company_id']}")

        similar_users = get_similar_users(selected_user["user_id"])

        # タイトル
        st.title("類似⼈物検索")
        st.write("類似⼈物")
        # 描画するNodeの登録
        nodes = [Node(id=str(selected_user["user_id"]), label=selected_user["full_name"], shape="circle")]
        nodes.extend(
            [
                Node(id=str(similar_user["user_id"]), label=similar_user["full_name"], shape="circle")
                for similar_user in similar_users
            ]
        )
        # 描画するEdgeの登録
        edges = [
            Edge(source=str(selected_user["user_id"]), target=str(similar_user["user_id"]), label="0.9")
            for similar_user in similar_users
        ]
        # グラフの描画設定
        config = Config(
            height=500,
            directed=False,
            physics=True,
        )
        # 描画
        agraph(nodes, edges, config)

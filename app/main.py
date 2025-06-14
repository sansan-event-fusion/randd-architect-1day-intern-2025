from typing import Any

import pandas as pd
import requests
import streamlit as st


def get_business_cards(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    """ビジネスカードを取得する関数"""
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
    params = {"offset": offset, "limit": limit}

    response = requests.get(url, params=params, timeout=30)
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
        selected_card: dict[str, Any] = df_cards[df_cards["full_name"] == selected_name].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**氏名:** {selected_card['full_name']}")
            st.markdown(f"**役職:** {selected_card['position']}")
            st.markdown(f"**会社名:** {selected_card['company_name']}")
        with col2:
            st.markdown(f"**住所:** {selected_card['address']}")
            st.markdown(f"**電話番号:** {selected_card['phone_number']}")
            st.markdown(f"**ユーザーID:** {selected_card['user_id']}")
            st.markdown(f"**会社ID:** {selected_card['company_id']}")

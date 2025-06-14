import pandas as pd
import streamlit as st

from app.crud import BusinessCardCRUD
from app.crud.models import BusinessCardResponse


def display_business_cards() -> None:
    """名刺データの表示コンポーネント."""
    st.header("名刺データ")

    business_cards = BusinessCardCRUD()

    # 名刺データの件数を表示
    total_count = business_cards.get_cards_count()
    st.metric("総名刺数", total_count)

    # 名刺データ一覧を取得・表示
    limit = st.slider("表示件数", min_value=10, max_value=100, value=20)
    cards = business_cards.get_all_cards(limit=limit)

    if cards:
        # DataFrameに変換して表示
        cards_data = [card.model_dump() for card in cards]
        cards_df = pd.DataFrame(cards_data)
        st.dataframe(cards_df, use_container_width=True)

        # 類似ユーザー検索機能
        display_similar_user_search(business_cards, cards)
    else:
        st.info("名刺データが見つかりませんでした")


def display_similar_user_search(business_cards: BusinessCardCRUD, cards: list[BusinessCardResponse]) -> None:
    """類似ユーザー検索コンポーネント."""
    st.subheader("類似ユーザー検索")
    user_ids = [card.user_id for card in cards]
    selected_user_id = st.selectbox("ユーザーIDを選択", user_ids)

    if st.button("類似ユーザーを検索"):
        similar_users = business_cards.get_similar_users(int(selected_user_id))
        if similar_users:
            similar_data = [user.model_dump() for user in similar_users]
            similar_df = pd.DataFrame(similar_data)
            st.dataframe(similar_df, use_container_width=True)
        else:
            st.info("類似ユーザーが見つかりませんでした")

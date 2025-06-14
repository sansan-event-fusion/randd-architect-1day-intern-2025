import pandas as pd
import streamlit as st

try:
    # テスト実行時のabsolute import
    from app.crud import ContactHistoryCRUD
except ImportError:
    # Streamlit実行時のrelative import
    from crud import ContactHistoryCRUD


def display_contact_history() -> None:
    """交換履歴の表示コンポーネント."""
    st.header("交換履歴")

    contacts = ContactHistoryCRUD()

    # 交換履歴の件数を表示
    total_count = contacts.get_contacts_count()
    st.metric("総交換履歴数", total_count)

    # 交換履歴一覧を取得・表示
    limit = st.slider("表示件数", min_value=10, max_value=100, value=20)
    contact_history = contacts.get_all_contacts(limit=limit)

    if contact_history:
        # DataFrameに変換して表示
        history_data = [contact.model_dump() for contact in contact_history]
        history_df = pd.DataFrame(history_data)
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("交換履歴が見つかりませんでした")

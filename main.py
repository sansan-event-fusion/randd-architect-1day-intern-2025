# external imports


import streamlit as st

# internal imports
from app.components import display_analytics_dashboard, display_business_cards, display_contact_history


def main() -> None:  # noqa: C901
    """名刺・交換履歴管理アプリ"""
    st.title("名刺・交換履歴管理アプリ")

    # サイドバーでデータ選択
    data_type = st.sidebar.selectbox("表示するデータを選択", ["📊 アナリティクス", "👤 名刺データ", "📋 交換履歴"])

    try:
        if data_type == "📊 アナリティクス":
            display_analytics_dashboard()
        elif data_type == "👤 名刺データ":
            display_business_cards()
        elif data_type == "📋 交換履歴":
            display_contact_history()

    except (ConnectionError, TimeoutError) as e:
        st.error(f"データの取得中にエラーが発生しました: {e!s}")
        st.info("APIサーバーに接続できない可能性があります。")
    except Exception as e:  # noqa: BLE001
        st.error(f"予期しないエラーが発生しました: {e!s}")
        st.info("アプリケーションの実行中にエラーが発生しました。")


if __name__ == "__main__":
    main()

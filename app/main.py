import pandas as pd
import requests
import streamlit as st

# タイトル
st.title("Sansan Circuit Trial")

API_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/"
cards_endpoint = "cards"
contacts_endpoint = "contacts"
headers = {"Content-Type": "application/json"}

page = st.selectbox("アプリ選択", ["営業先リコメンドアプリ", "名刺交換履歴アプリ"])

if page == "営業先リコメンドアプリ":
    st.write("営業先リコメンドアプリを選択しました。")
    response = requests.get(API_URL + cards_endpoint + "/?offset=0&limit=10000", headers=headers, timeout=2000)
    if response.status_code == 200:
        data = response.json()
        cards_data = pd.DataFrame(data)

        # 空選択を含むユーザーセレクトボックス
        options = ["", *(cards_data["full_name"] + "(" + cards_data["user_id"] + ")").tolist()]
        # ユーザー選択のマルチセレクトボックス
        selected_user_list = st.multiselect("ユーザーを選択してください", options, max_selections=1)
        if selected_user_list:
            selected_user = selected_user_list[0]
            selected_user_id = selected_user.split("(")[-1].strip(")")
            # 選択されたユーザーのカード情報を取得
            user_cards = cards_data[cards_data["user_id"] == selected_user_id]
            if not user_cards.empty:
                st.write("選択されたユーザーのカード情報")
                for _, row in user_cards.iterrows():
                    with st.container():
                        st.markdown(
                            f"""
                        <div style="border: 1px solid #ccc; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                            <strong>名前:</strong> {row["full_name"]}<br>
                            <strong>ユーザーID:</strong> {row["user_id"]}<br>
                            <strong>役職:</strong> {row["position"]}<br>
                            <strong>電話番号:</strong> {row["phone_number"]}<br>
                            <strong>企業:</strong> {row["company_name"]}<br>
                            <strong>企業ID:</strong> {row["company_id"]}<br>
                            <strong>住所:</strong> {row["address"]}<br>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                # 類似ユーザーのリコメンド
                sim_url = f"{API_URL}cards/{selected_user_id}/similar_top10_users"
                sim_response = requests.get(sim_url, headers=headers, timeout=2000)

                if sim_response.status_code == 200:
                    sim_df = pd.DataFrame(sim_response.json())
                    st.subheader("営業先リコメンド候補")
                    for _, row in sim_df.iterrows():
                        with st.expander(f"{row['full_name']}"), st.container():
                            st.markdown(
                                f"""
                                <div style="border: 1px solid #ccc; padding: 10px; border-radius: 10px;
                                margin-bottom: 10px;">
                                    <strong>名前:</strong> {row["full_name"]}<br>
                                    <strong>ユーザーID:</strong> {row["user_id"]}<br>
                                    <strong>役職:</strong> {row["position"]}<br>
                                    <strong>電話番号:</strong> {row["phone_number"]}<br>
                                    <strong>企業:</strong> {row["company_name"]}<br>
                                    <strong>企業ID:</strong> {row["company_id"]}<br>
                                    <strong>住所:</strong> {row["address"]}<br>
                                    <strong>類似度:</strong> {row["similarity"]:.2f}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                else:
                    st.error(f"類似ユーザー取得エラー: {sim_response.status_code}")
        else:
            st.write("ユーザーが選択されていません。")
        st.subheader("全ユーザーのカード情報")
        st.dataframe(cards_data)

    else:
        st.error(f"APIリクエストに失敗しました。ステータスコード: {response.status_code}")
        st.error("詳細: " + response.text)
elif page == "名刺交換履歴アプリ":
    st.write("名刺交換履歴アプリを選択しました。")

    # 日付絞り込み機能を追加
    st.subheader("期間設定")
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "開始日", value=pd.to_datetime("2021-06-14").date(), help="名刺交換履歴の検索開始日を選択してください"
        )

    with col2:
        end_date = st.date_input(
            "終了日", value=pd.to_datetime("2025-06-14").date(), help="名刺交換履歴の検索終了日を選択してください"
        )

    # 日付の妥当性チェック
    if start_date > end_date:
        st.error("開始日は終了日より前の日付を選択してください。")
        st.stop()

    # APIリクエストのパラメータを構築
    cards_params = {"offset": 0, "limit": 3000}
    contacts_params = {
        "offset": 0,
        "limit": 3000,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    }

    # APIリクエスト実行
    cards_response = requests.get(
        API_URL + cards_endpoint + "/",
        headers=headers,
        params=cards_params,
        timeout=2000,
    )
    contacts_response = requests.get(
        API_URL + contacts_endpoint + "/",
        headers=headers,
        params=contacts_params,
        timeout=2000,
    )

    if cards_response.status_code == 200 and contacts_response.status_code == 200:
        cards_data = pd.DataFrame(cards_response.json())
        contacts_data = pd.DataFrame(contacts_response.json())

        # IDを文字情報に変換するための関数を定義
        def enrich_contacts_data(contacts_df, cards_df):
            enriched_contacts = contacts_df.copy()

            # cards_dataからマッピング用の辞書を作成
            if not cards_df.empty:
                user_mapping = dict(zip(cards_df["user_id"], cards_df["full_name"], strict=False))
                company_mapping = dict(zip(cards_df["company_id"], cards_df["company_name"], strict=False))

                # user_idを名前に変換
                if "user_id" in enriched_contacts.columns:
                    enriched_contacts["ユーザー名"] = (
                        enriched_contacts["user_id"].map(user_mapping).fillna(enriched_contacts["user_id"])
                    )

                # 相手のIDも変換
                if "contact_user_id" in enriched_contacts.columns:
                    enriched_contacts["相手ユーザー名"] = (
                        enriched_contacts["contact_user_id"]
                        .map(user_mapping)
                        .fillna(enriched_contacts["contact_user_id"])
                    )

                if "contact_company_id" in enriched_contacts.columns:
                    enriched_contacts["相手会社名"] = (
                        enriched_contacts["contact_company_id"]
                        .map(company_mapping)
                        .fillna(enriched_contacts["contact_company_id"])
                    )

            return enriched_contacts

        # contactsデータを文字情報で拡張
        contacts_data_enriched = enrich_contacts_data(contacts_data, cards_data)

        # 期間情報を表示
        st.info(f"検索期間: {start_date.strftime('%Y年%m月%d日')} ~ {end_date.strftime('%Y年%m月%d日')}")
        contacts_data_enriched = enrich_contacts_data(contacts_data, cards_data)

        # 期間情報を表示
        st.info(f"検索期間: {start_date.strftime('%Y年%m月%d日')} ~ {end_date.strftime('%Y年%m月%d日')}")

        # 空選択を含むユーザーセレクトボックス
        if not cards_data.empty:
            options = ["", *(cards_data["full_name"] + "(" + cards_data["user_id"] + ")").tolist()]
            selected_user_list = st.multiselect("ユーザーを選択してください", options, max_selections=1)

            if selected_user_list:
                selected_user = selected_user_list[0]
                selected_user_id = selected_user.split("(")[-1].strip(")")

                st.subheader("選択されたユーザーのカード情報")
                user_cards = cards_data[cards_data["user_id"] == selected_user_id]

                for _, row in user_cards.iterrows():
                    with st.container():
                        st.markdown(
                            f"""
                        <div style="border: 1px solid #ccc; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                            <strong>名前:</strong> {row["full_name"]}<br>
                            <strong>ユーザーID:</strong> {row["user_id"]}<br>
                            <strong>役職:</strong> {row["position"]}<br>
                            <strong>電話番号:</strong> {row["phone_number"]}<br>
                            <strong>企業:</strong> {row["company_name"]}<br>
                            <strong>企業ID:</strong> {row["company_id"]}<br>
                            <strong>住所:</strong> {row["address"]}<br>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                # 選択されたユーザーの名刺交換履歴を取得
                user_contacts = contacts_data_enriched[contacts_data_enriched["user_id"] == selected_user_id]

                if not user_contacts.empty:
                    st.subheader(f"選択されたユーザーの名刺交換履歴 ({len(user_contacts)}件)")
                    # 日付カラムがある場合は日付でソート
                    if "created_at" in user_contacts.columns:
                        user_contacts = user_contacts.sort_values("created_at", ascending=False)
                    elif "exchanged_at" in user_contacts.columns:
                        user_contacts = user_contacts.sort_values("exchanged_at", ascending=False)

                    # 表示用にカラムを整理
                    display_columns = [
                        col
                        for col in user_contacts.columns
                        if col
                        in [
                            "ユーザー名",
                            "会社名",
                            "相手ユーザー名",
                            "相手会社名",
                            "created_at",
                            "exchanged_at",
                        ]
                        or col not in ["user_id", "company_id", "contact_user_id", "contact_company_id"]
                    ]

                    if display_columns:
                        st.dataframe(user_contacts[display_columns])
                    else:
                        st.dataframe(user_contacts)
                else:
                    st.write("指定期間内に選択されたユーザーの名刺交換履歴はありません。")
            else:
                st.write("ユーザーが選択されていません。")
        else:
            st.warning("カードデータが取得できませんでした。")
        # 全ユーザーの名刺交換履歴
        st.subheader(f"全ユーザーの名刺交換履歴 ({len(contacts_data_enriched)}件)")

        if not contacts_data_enriched.empty:
            # 統計情報を表示
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("総交換数", len(contacts_data_enriched))
            with col2:
                unique_users = (
                    contacts_data_enriched["user_id"].nunique() if "user_id" in contacts_data_enriched.columns else 0
                )
                st.metric("参加ユーザー数", unique_users)
            with col3:
                # 1日あたりの平均交換数
                days_diff = (end_date - start_date).days + 1
                avg_per_day = len(contacts_data_enriched) / days_diff if days_diff > 0 else 0
                st.metric("1日平均交換数", f"{avg_per_day:.1f}")

            # 日付カラムがある場合は日付でソート
            display_contacts = contacts_data_enriched.copy()
            if "created_at" in display_contacts.columns:
                display_contacts = display_contacts.sort_values("created_at", ascending=False)
            elif "exchanged_at" in display_contacts.columns:
                display_contacts = display_contacts.sort_values("exchanged_at", ascending=False)

            # 表示用にカラムを整理(
            display_columns = []
            id_columns = []

            for col in display_contacts.columns:
                if col in [
                    "ユーザー名",
                    "会社名",
                    "相手ユーザー名",
                    "相手会社名",
                ]:
                    display_columns.append(col)
                elif col.endswith("_id"):
                    id_columns.append(col)
                else:
                    display_columns.append(col)

            # IDカラムは最後に追加
            final_columns = display_columns + id_columns

            # 表示オプションを追加
            show_ids = st.checkbox(
                "ID情報も表示する",
                value=False,
                help="チェックするとuser_idやcompany_idなどの元のID情報も表示されます",
            )

            if show_ids:
                st.dataframe(display_contacts[final_columns])
            else:
                st.dataframe(display_contacts[display_columns])
        else:
            st.write("指定期間内に名刺交換履歴がありません。")

    else:
        st.error(
            f"APIリクエストに失敗しました。ステータスコード: "
            f"Cards: {cards_response.status_code}, Contacts: {contacts_response.status_code}"
        )

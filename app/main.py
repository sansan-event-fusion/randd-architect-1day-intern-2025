import pandas as pd
import requests
import streamlit as st

#APIのURL
API_BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api"
REQUEST_TIMEOUT = 10

# APIエンドポイントの設定
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(f"APIリクエストタイムアウト: {endpoint}")
        return None
    except requests.exceptions.HTTPError as http_err:
        st.error(f"API HTTPエラー: {http_err} (エンドポイント: {endpoint})")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"APIリクエストエラー: {e}")
        return None
    except ValueError as e:
        st.error(f"JSONデコードエラー: {e}")
        return None

# 関連企業検索
# 1.入力企業従業員と関わりの深い従業員を検索し、その従業員が所属する企業をリストアップ
# 2.その企業の従業員の所属企業を検索し、間接的に関わりのある企業をリストアップ
with st.form("company_search_form", clear_on_submit=False):
    company_name_input = st.text_input(
        "関連企業検索-社名を入力するとその会社と関わりの深い会社がリストアップされます。"
    )
    submitted = st.form_submit_button("検索")

    if submitted:
        if company_name_input:
            with st.spinner("名刺データを取得・検索中..."):
                all_cards_data = fetch_data("/cards/?limit=2000") #デフォルトは100件
            if all_cards_data:
                cards_df = pd.DataFrame(all_cards_data)
                try:
                    filtered_cards_df = cards_df[
                        cards_df["company_name"].str.contains(
                            company_name_input, case=False, na=False
                        )
                    ]
                    if not filtered_cards_df.empty:
                        st.write(f"「{company_name_input}」の検索結果:")
                        columns_to_display_filtered = ["full_name", "company_name", "position", "address", "phone_number"]
                        existing_columns_to_display_filtered = [col for col in columns_to_display_filtered if col in filtered_cards_df.columns]
                        st.dataframe(filtered_cards_df[existing_columns_to_display_filtered])
                        st.write(f"件数: {len(filtered_cards_df)}")

                        try:
                            all_indirectly_related_companies = []
                            processed_user_ids = set()

                            st.markdown("---")
                            st.write(
                                f"「{company_name_input}」の全従業員に基づいて"
                                "間接的な関連企業を検索します。"
                            )

                            for index, row in filtered_cards_df.iterrows():
                                user_id = row.get("user_id")
                                if not user_id:
                                    st.caption(f"行 {index} のユーザーIDが見つかりません。スキップします。")
                                    continue

                                if user_id in processed_user_ids:
                                    continue
                                processed_user_ids.add(user_id)

                                with st.spinner(
                                    "ユーザーの類似ユーザーを取得中..."
                                ):
                                    top10_users_data_l1 = fetch_data(
                                        f"/cards/{user_id}/similar_top10_users"
                                    )

                                current_user_indirect_companies = []
                                if top10_users_data_l1:

                                    for l1_user in top10_users_data_l1:
                                        l1_user_id = l1_user.get("user_id")
                                        if l1_user_id:
                                            with st.spinner(
                                                " (Top 10) を取得中..."
                                            ):
                                                top10_users_data_l2 = fetch_data(
                                                    f"/cards/{l1_user_id}/similar_top10_users"
                                                )  # Renamed variable

                                            if top10_users_data_l2:
                                                for l2_user in top10_users_data_l2:
                                                    company_name = l2_user.get("company_name")
                                                    if company_name:
                                                        current_user_indirect_companies.append(company_name)
                                                    else:
                                                        st.caption(
                                                            f"ユーザー {l2_user.get('user_id', 'ID不明')} "
                                                            "の会社名が見つかりません。"
                                                        )
                                            else:
                                                st.caption(
                                                    f"類似ユーザー {l1_user_id} の関連ユーザーデータ取得に"
                                                    "失敗またはデータがありません。"
                                                )
                                        else:
                                            st.caption(
                                                f"最初の類似ユーザーリストのアイテムに 'user_id' がありません: "
                                                f"{l1_user}" # Split long line
                                            )
                                else:
                                    st.info("ユーザーの類似ユーザーは見つかりませんでした。")
                                all_indirectly_related_companies.extend(current_user_indirect_companies)

                            if all_indirectly_related_companies:
                                st.markdown("### 間接的に関わりのある企業リスト")
                                # Display unique companies and their counts directly
                                unique_companies_df = pd.DataFrame(
                                    all_indirectly_related_companies, columns=["company_name"]
                                )
                                st.markdown("#### 間接関連企業")
                                company_counts = unique_companies_df["company_name"].value_counts()
                                # 間接関連企業を関連数を関連度として表示
                                company_counts_df = company_counts.reset_index(name="関連度")
                                company_counts_df = company_counts_df.rename(columns={"index": "company_name"})
                                st.dataframe(company_counts_df)
                            else:
                                st.info("間接的に関わりのある企業は見つかりませんでした。")

                        except KeyError as e:
                            if ("user_id" in str(e).lower() and
                                "filtered_cards_df" in locals() and
                                "user_id" not in filtered_cards_df.columns):
                                st.error(
                                    "エラー: 最初の検索結果に 'user_id' カラムが見つかりません。"
                                    "データ構造を確認してください。"
                                )
                            else:
                                st.error(f"データ処理中にキーエラーが発生しました: {e}")
                        except IndexError:
                            st.error(
                                "エラー: 最初の検索結果からユーザー情報を取得できませんでした "
                                "(リストが空の可能性があります)。"
                            )

                    else:
                        st.info(f"「{company_name_input}」に該当する名刺データは見つかりませんでした。")
                except KeyError:
                    st.error(
                        "エラー: データに 'company_name' カラムが見つかりません。"
                        "APIから返されるデータ構造を確認してください。"
                    )
                except AttributeError:
                    st.error(
                        "エラー: 'company_name' カラムが文字列型ではありません。"
                        "データ型を確認してください。"
                    )
            else:
                st.error("名刺データの取得に失敗しました。")
        else:
            st.warning("社名を入力してから検索ボタンを押してください。")


st.markdown("## 名刺データ")
if st.button("名刺データを取得"):
    with st.spinner("取得中..."):
        all_cards_data_display = fetch_data("/cards/?limit=2000")

    if all_cards_data_display:
        cards_display_df = pd.DataFrame(all_cards_data_display)
        # 表示可能なもの ["user_id": "string", "company_id": "string", "full_name": "string", "position": "string", "company_name": "string", "address": "string", "phone_number": "string"]
        columns_to_display = ["full_name", "company_name", "position", "adress","phone_number"]
        existing_columns_to_display = [col for col in columns_to_display if col in cards_display_df.columns]
        if existing_columns_to_display:
            cards_display_df = cards_display_df[existing_columns_to_display]
            st.dataframe(cards_display_df)
        st.write(f"件数: {len(all_cards_data_display)}")

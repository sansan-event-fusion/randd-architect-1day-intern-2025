from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# タイトル
st.title("サンプルアプリ")

page = st.selectbox("アプリを選択してください", ["検索", "営業活動履歴表示", "ダミーデータ表示"])

if page == "検索":
    BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/"
    endpoint = "cards"
    headers = {"Content-Type": "application/json"}

    response = requests.get(BASE_URL + endpoint + "/?offset=0&limit=3000", headers=headers, timeout=2000)

    if response.status_code == 200:
        data = response.json()
        cards_data = pd.DataFrame(data)

        # 空選択を含むユーザーセレクトボックス
        options = ["", *(cards_data["full_name"] + "(" + cards_data["user_id"] + ")").tolist()]
        selected_user = st.selectbox("ユーザーを選択してください", options)

        # 選択されたときだけリコメンド表示
        if selected_user:
            selected_user_id = selected_user.split("(")[-1].replace(")", "")
            sim_url = f"{BASE_URL}cards/{selected_user_id}/similar_top10_users"
            sim_response = requests.get(sim_url, headers=headers, timeout=2000)

            if sim_response.status_code == 200:
                sim_data = sim_response.json()
                sim_df = pd.DataFrame(sim_data)
                st.subheader("営業先リコメンド候補")
                st.dataframe(sim_df)
            else:
                st.error(f"類似ユーザー取得エラー: {sim_response.status_code}")
    else:
        st.error(f"APIエラー: {response.status_code}")

elif page == "営業活動履歴表示":
    BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/"
    headers = {"Content-Type": "application/json"}

    # 全cards取得
    response = requests.get(BASE_URL + "cards/?offset=0&limit=3000", headers=headers, timeout=2000)
    if response.status_code == 200:
        data = response.json()
        cards_data = pd.DataFrame(data)

        # ユーザー選択
        options = ["", *(cards_data["full_name"] + "(" + cards_data["user_id"] + ")").tolist()]
        selected_user = st.selectbox("ユーザーを選択してください", options)

        if selected_user:
            selected_user_id = selected_user.split("(")[-1].replace(")", "")
            # 件数取得
            count_url = f"{BASE_URL}contacts/owner_users/{selected_user_id}/count"
            count_res = requests.get(count_url, headers=headers, timeout=2000)

            if count_res.status_code == 200:
                total_count = int(count_res.text)

                # 名刺交換データ取得
                contact_url = f"{BASE_URL}contacts/owner_users/{selected_user_id}?offset=0&limit={total_count}"
                contact_res = requests.get(contact_url, headers=headers, timeout=2000)

                if contact_res.status_code == 200:
                    contact_data = contact_res.json()
                    contact_df = pd.DataFrame(contact_data)
                    contact_df = contact_df[["user_id", "company_id", "created_at"]]

                    df_user = cards_data[["user_id", "full_name"]]
                    df_company = cards_data[["company_id", "company_name"]].drop_duplicates()

                    contact_df = contact_df.merge(df_user, on="user_id", how="left")
                    contact_df = contact_df.merge(df_company, on="company_id", how="left")

                    contact_df["created_at"] = pd.to_datetime(contact_df["created_at"], errors="coerce")

                    # ISO形式のcreated_atをUTC→naiveなdatetimeに変換
                    contact_df["created_at"] = pd.to_datetime(contact_df["created_at"], errors="coerce", utc=True)
                    contact_df["created_at"] = contact_df["created_at"].dt.tz_localize(None)
                    contact_df["交換日時"] = contact_df["created_at"].dt.strftime("%Y年%m月%d日 %H時%M分")

                    contact_df = contact_df[["full_name", "company_name", "交換日時", "created_at"]]

                    # 欠損除去
                    contact_df = contact_df.dropna(subset=["created_at"])

                    # 表示期間オプション
                    period_options = {
                        "直近1ヶ月": pd.Timestamp.today() - pd.DateOffset(months=1),
                        "直近3ヶ月": pd.Timestamp.today() - pd.DateOffset(months=3),
                        "直近6ヶ月": pd.Timestamp.today() - pd.DateOffset(months=6),
                        "直近1年": pd.Timestamp.today() - pd.DateOffset(years=1),
                        "全期間": pd.Timestamp.min,
                    }
                    selected_period = st.selectbox("表示期間を選択してください", list(period_options.keys()))

                    cutoff = pd.to_datetime(period_options[selected_period])
                    filtered_df = contact_df[contact_df["created_at"] >= cutoff]

                    st.subheader(f"名刺交換履歴({len(filtered_df)}件)")
                    # 日別交換件数の推移グラフ
                    daily_count = filtered_df["created_at"].dt.date.value_counts().sort_index()
                    daily_df = pd.DataFrame({"日付": daily_count.index, "交換件数": daily_count.to_numpy()})
                    daily_df = daily_df.sort_values("日付")
                    st.dataframe(filtered_df[["full_name", "company_name", "交換日時"]])
                    st.line_chart(daily_df.set_index("日付"))

                else:
                    st.error(f"交換データ取得エラー: {contact_res.status_code}")
            else:
                st.error(f"交換件数取得エラー: {count_res.status_code}")
    else:
        st.error(f"カード取得エラー: {response.status_code}")

elif page == "ダミーデータ表示":
    path = Path(__file__).parent / "dummy_data.csv"
    df_dummy = pd.read_csv(path, dtype=str)
    st.dataframe(df_dummy)

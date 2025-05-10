import json
import re
from pathlib import Path

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

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
        address_dict = dict(zip(cards_data["user_id"], cards_data["address"], strict=True))

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
                    contact_df_for_filter = contact_df[
                        ["user_id", "full_name", "company_name", "交換日時", "created_at"]
                    ].copy()
                    filtered_df = contact_df_for_filter[contact_df_for_filter["created_at"] >= cutoff].copy()

                    st.subheader(f"名刺交換履歴({len(filtered_df)}件)")
                    st.dataframe(filtered_df[["full_name", "company_name", "交換日時"]])
                    st.markdown("### 名刺交換件数の推移")

                    agg_unit = st.selectbox("集計単位を選択してください", ["月", "週", "日"])

                    if not filtered_df.empty:
                        df_chart = filtered_df.copy()
                        if agg_unit == "日":
                            df_chart["期間"] = df_chart["created_at"].dt.date
                            all_periods = pd.date_range(
                                start=df_chart["期間"].min(), end=df_chart["期間"].max(), freq="D"
                            ).date
                        elif agg_unit == "週":
                            df_chart["期間"] = (
                                df_chart["created_at"].dt.to_period("W").apply(lambda r: r.start_time.date())
                            )
                            all_periods = pd.date_range(
                                start=min(df_chart["期間"]), end=max(df_chart["期間"]), freq="W-MON"
                            ).date
                        elif agg_unit == "月":
                            df_chart["期間"] = (
                                df_chart["created_at"].dt.to_period("M").apply(lambda r: r.start_time.date())
                            )
                            all_periods = pd.date_range(
                                start=min(df_chart["期間"]), end=max(df_chart["期間"]), freq="MS"
                            ).date

                        daily_count = df_chart["期間"].value_counts().to_dict()
                        df_agg = pd.DataFrame({"期間": list(all_periods)})
                        df_agg["交換件数"] = df_agg["期間"].map(daily_count).fillna(0).astype(int)
                        st.line_chart(df_agg.set_index("期間"))

                        # 期間内の交換企業一覧
                        st.subheader("期間内に交換した企業一覧")
                        company_summary = (
                            filtered_df.groupby(["company_name"])
                            .size()
                            .reset_index(name="交換件数")
                            .sort_values("交換件数", ascending=False)
                        )
                        st.dataframe(company_summary)

                        st.subheader("名刺交換件数(都道府県別)")

                        def extract_prefecture(address):
                            match = re.match(r"^(北海道|東京都|京都府|大阪府|.{2,3}県)", str(address))
                            return match.group(0) if match else None

                        # filtered_df に user_id を用いて住所と紐付け
                        if "user_id" in filtered_df.columns:
                            filtered_df["address"] = filtered_df["user_id"].map(lambda x: address_dict.get(x))
                        else:
                            filtered_df["address"] = None

                        filtered_df["都道府県"] = filtered_df["address"].apply(extract_prefecture)

                        pref_summary = (
                            filtered_df["都道府県"]
                            .value_counts()
                            .reset_index(name="件数")
                            .rename(columns={"index": "都道府県"})
                        )

                        st.dataframe(pref_summary)

                        st.subheader("名刺交換件数(白黒地図)")
                        center_coords = [36.2048, 138.2529]
                        m = folium.Map(location=center_coords, zoom_start=5, tiles="cartodbpositron")

                        # GeoJSONの読み込みと整形
                        geojson_path = Path("app/japan.geojson")
                        with Path.open(geojson_path, "r", encoding="utf-8") as f:
                            japan_geojson = json.load(f)
                        for feature in japan_geojson.get("features", []):
                            props = feature.get("properties", {})
                            if "nam_ja" in props:
                                props["name"] = props["nam_ja"]

                        # Choroplethの追加
                        folium.Choropleth(
                            geo_data=japan_geojson,
                            data=pref_summary,
                            columns=["都道府県", "件数"],
                            key_on="feature.properties.name",
                            fill_color="YlOrRd",
                            fill_opacity=0.7,
                            line_opacity=0.05,
                            threshold_scale=[0, 1, 5, 10, 20, 50, 100],
                            nan_fill_color="white",
                            legend_name="名刺交換件数",
                        ).add_to(m)

                        # 都道府県ごとの企業名と件数の文字列をまとめた辞書を作成
                        company_info = (
                            filtered_df.groupby("都道府県")
                            .agg({"company_name": lambda x: "、".join(sorted(set(x.dropna()))), "都道府県": "count"})
                            .rename(columns={"都道府県": "件数"})
                            .reset_index()
                        )
                        company_info["tooltip"] = company_info.apply(
                            lambda row: f"件数: {row['件数']}件<br>企業: {row['company_name']}", axis=1
                        )
                        tooltip_dict = dict(zip(company_info["都道府県"], company_info["tooltip"], strict=True))

                        # GeoJSONにtooltipデータを埋め込む
                        for feature in japan_geojson.get("features", []):
                            name = feature["properties"].get("name")
                            feature["properties"]["tooltip"] = tooltip_dict.get(name, "件数: 0件<br>企業: なし")

                        folium.GeoJson(
                            japan_geojson, tooltip=folium.GeoJsonTooltip(fields=["tooltip"], aliases=[""], labels=False)
                        ).add_to(m)

                        from shapely.geometry import Point, shape

                        # 地図を表示しクリックイベントを取得
                        map_return = st_folium(m, use_container_width=True, height=600)

                        clicked_prefecture = None
                        if map_return and map_return.get("last_clicked"):
                            clicked_latlng = map_return["last_clicked"]
                            click_point = Point(clicked_latlng["lng"], clicked_latlng["lat"])

                            for feature in japan_geojson["features"]:
                                polygon = shape(feature["geometry"])
                                if polygon.contains(click_point):
                                    clicked_prefecture = feature["properties"]["name"]
                                    break

                        prefecture_options = ["", *sorted(company_info["都道府県"].dropna().unique().tolist())]
                        initial_index = 0
                        if clicked_prefecture and clicked_prefecture in prefecture_options:
                            initial_index = prefecture_options.index(clicked_prefecture)

                        # ▼▼▼ 地図の後に配置された都道府県セレクトボックス ▼▼▼
                        selected_prefecture = st.selectbox(
                            "表示対象の都道府県を選択してください(地図クリックまたは選択)",
                            prefecture_options,
                            index=initial_index,
                        )

                        if selected_prefecture:
                            st.subheader(f"{selected_prefecture}: 名刺交換済みの企業の名刺情報")

                            target_user_ids = (
                                filtered_df[filtered_df["都道府県"] == selected_prefecture]["user_id"].unique().tolist()
                            )
                            cards_subset = cards_data[cards_data["user_id"].isin(target_user_ids)]
                            st.dataframe(cards_subset[["user_id", "full_name", "company_name", "address"]])

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

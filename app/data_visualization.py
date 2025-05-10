import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib3

# SSLの警告を無視する設定
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# APIのベースURL
BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api"

# 都道府県の緯度経度データ
PREFECTURE_COORDINATES = {
    "北海道": [43.064615, 141.346807],
    "青森県": [40.824308, 140.740059],
    "岩手県": [39.703619, 141.152684],
    "宮城県": [38.268837, 140.872183],
    "秋田県": [39.718614, 140.102364],
    "山形県": [38.240436, 140.363633],
    "福島県": [37.750299, 140.467551],
    "茨城県": [36.341813, 140.446793],
    "栃木県": [36.565725, 139.883565],
    "群馬県": [36.390668, 139.060406],
    "埼玉県": [35.857428, 139.648933],
    "千葉県": [35.605058, 140.123308],
    "東京都": [35.689488, 139.691706],
    "神奈川県": [35.447507, 139.642345],
    "新潟県": [37.902552, 139.023095],
    "富山県": [36.695291, 137.211338],
    "石川県": [36.594682, 136.625573],
    "福井県": [36.065178, 136.221527],
    "山梨県": [35.664158, 138.568449],
    "長野県": [36.651299, 138.180956],
    "岐阜県": [35.391227, 136.722291],
    "静岡県": [34.976987, 138.383057],
    "愛知県": [35.180188, 136.906565],
    "三重県": [34.730283, 136.508588],
    "滋賀県": [35.004531, 135.86859],
    "京都府": [35.021247, 135.755597],
    "大阪府": [34.686316, 135.519711],
    "兵庫県": [34.691269, 135.183071],
    "奈良県": [34.685334, 135.832742],
    "和歌山県": [34.226034, 135.167506],
    "鳥取県": [35.503891, 134.237736],
    "島根県": [35.472295, 133.050499],
    "岡山県": [34.661751, 133.934406],
    "広島県": [34.396561, 132.459622],
    "山口県": [34.185956, 131.470649],
    "徳島県": [34.065718, 134.559303],
    "香川県": [34.340149, 134.043444],
    "愛媛県": [33.841624, 132.765681],
    "高知県": [33.559706, 133.531079],
    "福岡県": [33.606785, 130.418314],
    "佐賀県": [33.249442, 130.298822],
    "長崎県": [32.744839, 129.873756],
    "熊本県": [32.789827, 130.741667],
    "大分県": [33.238172, 131.612619],
    "宮崎県": [31.911090, 131.423855],
    "鹿児島県": [31.560146, 130.557978],
    "沖縄県": [26.212401, 127.680932],
}

# 主要都市の緯度経度データ
MAJOR_CITIES = {
    "東京": {"lat": 35.689488, "lon": 139.691706, "prefecture": "東京都"},
    "横浜": {"lat": 35.447507, "lon": 139.642345, "prefecture": "神奈川県"},
    "大阪": {"lat": 34.686316, "lon": 135.519711, "prefecture": "大阪府"},
    "名古屋": {"lat": 35.180188, "lon": 136.906565, "prefecture": "愛知県"},
    "福岡": {"lat": 33.606785, "lon": 130.418314, "prefecture": "福岡県"},
    "札幌": {"lat": 43.064615, "lon": 141.346807, "prefecture": "北海道"},
    "仙台": {"lat": 38.268837, "lon": 140.872183, "prefecture": "宮城県"},
    "広島": {"lat": 34.396561, "lon": 132.459622, "prefecture": "広島県"},
    "京都": {"lat": 35.021247, "lon": 135.755597, "prefecture": "京都府"},
    "神戸": {"lat": 34.691269, "lon": 135.183071, "prefecture": "兵庫県"},
}


def extract_prefecture(address):
    """住所から都道府県を抽出する"""
    if not isinstance(address, str):
        return None

    for prefecture in PREFECTURE_COORDINATES.keys():
        if prefecture in address:
            return prefecture
    return None


def create_prefecture_map(cards_df):
    """都道府県ごとの名刺数の分布を地図上に表示"""
    # 都道府県を抽出
    cards_df["prefecture"] = cards_df["address"].apply(extract_prefecture)

    # 都道府県ごとの集計
    prefecture_counts = cards_df["prefecture"].value_counts().reset_index()
    prefecture_counts.columns = ["prefecture", "count"]

    # 緯度経度データを追加
    prefecture_counts["lat"] = prefecture_counts["prefecture"].map(lambda x: PREFECTURE_COORDINATES[x][0])
    prefecture_counts["lon"] = prefecture_counts["prefecture"].map(lambda x: PREFECTURE_COORDINATES[x][1])

    # 地図の作成
    fig = px.scatter_mapbox(
        prefecture_counts,
        lat="lat",
        lon="lon",
        size="count",
        hover_name="prefecture",
        hover_data={"count": True, "lat": False, "lon": False},
        title="都道府県別名刺数の分布",
        mapbox_style="carto-positron",
        center={"lat": 37.5, "lon": 137},
        zoom=4,
    )

    # レイアウトの調整
    fig.update_layout(
        height=800,  # 高さを800ピクセルに
        width=None,  # 幅は自動調整（画面幅に合わせる）
        margin=dict(l=0, r=0, t=30, b=0),  # マージンを最小限に
    )

    return fig


def fetch_all_cards():
    """全ての名刺データを取得"""
    cards = []
    offset = 0
    limit = 100

    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/cards/",
                params={"offset": offset, "limit": limit},
                timeout=30,  # タイムアウトを30秒に設定
                verify=False,  # SSL証明書の検証をスキップ
            )
            response.raise_for_status()  # エラーレスポンスの場合は例外を発生
            data = response.json()
            if not data:
                break
            cards.extend(data)
            if len(data) < limit:
                break
            offset += limit
        except requests.exceptions.RequestException as e:
            st.error(f"名刺データの取得中にエラーが発生しました: {str(e)}")
            return pd.DataFrame()  # エラー時は空のDataFrameを返す

    return pd.DataFrame(cards)


def fetch_all_contacts():
    """全てのコンタクト履歴を取得"""
    contacts = []
    offset = 0
    limit = 100
    max_retries = 3
    retry_delay = 2  # seconds

    while True:
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(
                    f"{BASE_URL}/contacts/",
                    params={"offset": offset, "limit": limit},
                    timeout=30,  # タイムアウトを30秒に設定
                    verify=False,  # SSL証明書の検証をスキップ
                )
                response.raise_for_status()  # エラーレスポンスの場合は例外を発生
                data = response.json()
                if not data:
                    return pd.DataFrame(contacts)  # データがない場合は現在までのデータを返す
                contacts.extend(data)
                if len(data) < limit:
                    return pd.DataFrame(contacts)  # 最後のページの場合
                offset += limit
                break  # 成功したらリトライループを抜ける
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries == max_retries:
                    st.warning(f"コンタクト履歴の取得中にエラーが発生しました（offset={offset}）: {str(e)}")
                    if contacts:  # 一部のデータが取得できている場合
                        st.info(f"一部のデータのみ表示します（{len(contacts)}件取得済み）")
                        return pd.DataFrame(contacts)
                    return pd.DataFrame()  # データが1件も取得できていない場合は空のDataFrameを返す
                st.warning(
                    f"APIリクエストに失敗しました（{retries}/{max_retries}回目）。{retry_delay}秒後にリトライします..."
                )
                time.sleep(retry_delay)

    return pd.DataFrame(contacts)  # 通常はここには到達しない


def is_in_city(address, city_name, city_info):
    """住所が指定された都市に属しているかを判定"""
    if not isinstance(address, str):
        return False
    return city_info["prefecture"] in address and any(
        keyword in address for keyword in [city_name, city_info["prefecture"]]
    )


def create_major_cities_company_map(cards_df, selected_companies=None):
    """主要都市における会社ごとの名刺分布を地図上に表示"""
    # 都市ごとのデータを抽出
    city_data = []
    for city_name, city_info in MAJOR_CITIES.items():
        city_mask = cards_df["address"].apply(lambda x: is_in_city(x, city_name, city_info))
        city_cards = cards_df[city_mask]

        if len(city_cards) > 0:
            # 会社ごとの集計
            company_counts = city_cards["company_name"].value_counts()
            # 上位10社のみを抽出（選択された会社がない場合）
            if selected_companies is None:
                top_companies = company_counts.head(10)
            else:
                # 選択された会社のデータのみを抽出
                top_companies = company_counts[company_counts.index.isin(selected_companies)]

            for company, count in top_companies.items():
                city_data.append(
                    {
                        "city": city_name,
                        "company": company,
                        "count": count,
                        "lat": city_info["lat"],
                        "lon": city_info["lon"],
                    }
                )

    if not city_data:
        return None

    city_df = pd.DataFrame(city_data)

    # 地図の作成
    fig = px.scatter_mapbox(
        city_df,
        lat="lat",
        lon="lon",
        size="count",
        color="company",
        hover_name="company",
        hover_data={"city": True, "count": True, "lat": False, "lon": False, "company": False},
        title="主要都市における会社別名刺数の分布",
        mapbox_style="carto-positron",
        center={"lat": 37.5, "lon": 137},
        zoom=4,
    )

    # レイアウトの調整
    fig.update_layout(
        height=800,  # 高さを800ピクセルに
        width=None,  # 幅は自動調整（画面幅に合わせる）
        margin=dict(l=0, r=0, t=30, b=0),  # マージンを最小限に
        legend_title_text="会社名",
        showlegend=True,
        legend={"itemsizing": "constant"},
    )

    return fig


def get_top_companies(cards_df, n=30):
    """上位n社の会社名を取得"""
    return cards_df["company_name"].value_counts().head(n).index.tolist()


def show_visualization():
    """データの可視化を行う"""
    st.header("データ可視化")

    # データの取得
    with st.spinner("名刺データを取得中..."):
        cards_df = fetch_all_cards()

    if cards_df.empty:
        st.error("名刺データの取得に失敗しました。")
        return

    with st.spinner("コンタクト履歴を取得中..."):
        contacts_df = fetch_all_contacts()

    if contacts_df.empty:
        st.error("コンタクト履歴の取得に失敗しました。")
        return

    # タブの作成
    tab1, tab2, tab3 = st.tabs(["都道府県分布", "主要都市の企業分布", "コンタクト履歴分析"])

    with tab1:
        st.subheader("都道府県別名刺数の分布")
        fig = create_prefecture_map(cards_df)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("主要都市における企業分布")
        # 上位の会社を取得
        top_companies = get_top_companies(cards_df)
        # 選択された会社のみを表示
        selected_companies = st.multiselect(
            "表示する企業を選択（複数選択可）",
            options=top_companies,
            default=top_companies[:5],  # デフォルトで上位5社を選択
        )
        if selected_companies:
            fig = create_major_cities_company_map(cards_df, selected_companies)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("企業を1つ以上選択してください。")

    with tab3:
        st.subheader("コンタクト履歴の分析")
        # コンタクト履歴の時系列分析
        if not contacts_df.empty:
            # APIのレスポンス構造に応じて適切なカラムを使用
            try:
                # タイムスタンプのカラム名を確認
                time_column = next(
                    col
                    for col in contacts_df.columns
                    if any(x in col.lower() for x in ["timestamp", "time", "date", "created"])
                )

                contacts_df["timestamp"] = pd.to_datetime(contacts_df[time_column])
                contacts_df["date"] = contacts_df["timestamp"].dt.date
                daily_contacts = contacts_df["date"].value_counts().sort_index()

                # 時系列グラフの作成
                fig = px.line(
                    x=daily_contacts.index,
                    y=daily_contacts.values,
                    title="日別コンタクト数の推移",
                    labels={"x": "日付", "y": "コンタクト数"},
                )
                st.plotly_chart(fig, use_container_width=True)

                # データの詳細を表示
                st.write("### データの詳細")
                st.write(f"総コンタクト数: {len(contacts_df)}")
                st.write(f"期間: {daily_contacts.index.min()} から {daily_contacts.index.max()}")

                # 利用可能なカラムを確認
                if "type" in contacts_df.columns:
                    # コンタクトタイプの分布
                    contact_types = contacts_df["type"].value_counts()
                    fig = px.pie(
                        values=contact_types.values,
                        names=contact_types.index,
                        title="コンタクトタイプの分布",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # データフレームの最初の数行を表示
                st.write("### データサンプル")
                st.dataframe(contacts_df.head())

            except Exception as e:
                st.error(f"データの分析中にエラーが発生しました: {str(e)}")
                st.write("### 利用可能なカラム:")
                st.write(contacts_df.columns.tolist())
                st.write("### データサンプル:")
                st.dataframe(contacts_df.head())
        else:
            st.warning("コンタクト履歴のデータがありません。")


if __name__ == "__main__":
    show_visualization()

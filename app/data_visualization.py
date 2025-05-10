import time
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib3
from plotly.graph_objects import Figure

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

    for prefecture in PREFECTURE_COORDINATES:
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
        margin={"l": 0, "r": 0, "t": 30, "b": 0},  # マージンを最小限に
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
                verify=True,  # SSL検証を有効化
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
            st.error(f"名刺データの取得中にエラーが発生しました: {e!s}")
            return pd.DataFrame()  # エラー時は空のDataFrameを返す

    return pd.DataFrame(cards)


def _handle_contact_api_error(
    e: Exception, offset: int, contacts: list, retries: int, max_retries: int, retry_delay: int
) -> pd.DataFrame | None:
    """Handle API errors when fetching contacts."""
    if retries == max_retries:
        st.warning(f"コンタクト履歴の取得中にエラーが発生しました（offset={offset}）: {e!s}")
        if contacts:  # 一部のデータが取得できている場合
            st.info(f"一部のデータのみ表示します（{len(contacts)}件取得済み）")
            return pd.DataFrame(contacts)
        return pd.DataFrame()  # データが1件も取得できていない場合は空のDataFrameを返す
    st.warning(f"APIリクエストに失敗しました（{retries}/{max_retries}回目）。{retry_delay}秒後にリトライします...")
    time.sleep(retry_delay)
    return None


def _fetch_contacts_page(offset: int, limit: int) -> list | None:
    """Fetch a single page of contacts."""
    try:
        response = requests.get(
            f"{BASE_URL}/contacts/",
            params={"offset": offset, "limit": limit},
            timeout=30,
            verify=True,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def _fetch_page_with_retry(offset: int, limit: int, max_retries: int, retry_delay: int) -> list | None:
    """Fetch a single page with retry logic."""
    for _ in range(max_retries):
        data = _fetch_contacts_page(offset, limit)
        if data is not None:
            return data
        time.sleep(retry_delay)

    st.warning(f"Failed to fetch contacts at offset {offset} after {max_retries} retries")
    return None


def _process_contacts_data(contacts: list) -> pd.DataFrame:
    """Process the collected contacts data."""
    if not contacts:
        return pd.DataFrame()
    return pd.DataFrame(contacts)


def fetch_all_contacts() -> pd.DataFrame:
    """Fetch all contact history."""
    contacts = []
    offset = 0
    limit = 100
    max_retries = 3
    retry_delay = 2

    while True:
        data = _fetch_page_with_retry(offset, limit, max_retries, retry_delay)
        if data is None or not data:
            break

        contacts.extend(data)
        if len(data) < limit:
            break

        offset += limit

    return _process_contacts_data(contacts)


def is_in_city(address: str, city_name: str, city_info: dict) -> bool:
    """Check if an address is in the given city."""
    if not isinstance(address, str):
        return False
    return city_info["prefecture"] in address and city_name in address


def _process_city_companies(
    city_name: str,
    city_info: dict,
    cards_df: pd.DataFrame,
    selected_companies: list[str] | None = None,
) -> list[dict]:
    """Process company data for a specific city."""
    city_cards = cards_df[cards_df["address"].apply(lambda x, cn=city_name, ci=city_info: is_in_city(x, cn, ci))]

    if selected_companies:
        city_cards = city_cards[city_cards["company"].isin(selected_companies)]

    companies = city_cards["company"].value_counts()

    return [
        {
            "lat": city_info["lat"],
            "lon": city_info["lon"],
            "company": company,
            "count": count,
            "city": city_name,
        }
        for company, count in companies.items()
    ]


def create_major_cities_company_map(
    cards_df: pd.DataFrame, selected_companies: list[str] | None = None
) -> Figure | None:
    """Create a map showing company distribution across major cities."""
    all_city_data = []

    for city_name, city_info in MAJOR_CITIES.items():
        city_data = _process_city_companies(city_name, city_info, cards_df, selected_companies)
        all_city_data.extend(city_data)

    if not all_city_data:
        st.warning("No data available for visualization")
        return None

    df = pd.DataFrame(all_city_data)

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        size="count",
        color="company",
        hover_name="company",
        hover_data={"count": True, "city": True, "lat": False, "lon": False},
        title="Major Cities Company Distribution",
        mapbox_style="carto-positron",
        center={"lat": 37.5, "lon": 137},
        zoom=4,
    )

    fig.update_layout(
        height=800,
        width=None,
        margin={"l": 0, "r": 0, "t": 30, "b": 0},
        showlegend=True,
    )

    return fig


def get_top_companies(cards_df, n=30):
    """上位n社の会社名を取得"""
    return cards_df["company_name"].value_counts().head(n).index.tolist()


def _create_time_series_plot(contacts_df: pd.DataFrame) -> tuple[Any, pd.Series]:
    """Create time series plot for contacts."""
    time_column = next(
        col for col in contacts_df.columns if any(x in col.lower() for x in ["timestamp", "time", "date", "created"])
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
    return fig, daily_contacts


def _create_contact_type_plot(contacts_df: pd.DataFrame) -> Any | None:
    """Create contact type distribution plot."""
    if "type" not in contacts_df.columns:
        return None

    contact_types = contacts_df["type"].value_counts()
    return px.pie(
        values=contact_types.values,
        names=contact_types.index,
        title="コンタクトタイプの分布",
    )


def _display_company_selection(cards_df: pd.DataFrame) -> list[str] | None:
    """Display company selection widget and return selected companies."""
    top_companies = get_top_companies(cards_df)

    st.sidebar.markdown("### 会社の選択")
    select_all = st.sidebar.checkbox("全ての会社を表示", value=False)

    if select_all:
        return None

    selected_companies: list[str] = st.sidebar.multiselect(
        "表示する会社を選択してください",
        options=top_companies,
        default=top_companies[:5] if len(top_companies) > 5 else top_companies,
    )

    return selected_companies if selected_companies else None


def _display_contact_analysis(contacts_df: pd.DataFrame) -> None:
    """Display contact analysis visualizations."""
    if contacts_df.empty:
        st.warning("コンタクト履歴のデータがありません。")
        return

    st.markdown("## コンタクト履歴の分析")

    # Time series plot
    fig_time, daily_contacts = _create_time_series_plot(contacts_df)
    if fig_time:
        st.plotly_chart(fig_time, use_container_width=True)

        st.markdown("### 統計情報")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総コンタクト数", len(contacts_df))
        with col2:
            st.metric("1日あたりの平均", f"{daily_contacts.mean():.1f}")
        with col3:
            st.metric("最大コンタクト数/日", daily_contacts.max())

    # Contact type plot
    fig_type = _create_contact_type_plot(contacts_df)
    if fig_type:
        st.plotly_chart(fig_type, use_container_width=True)


def show_visualization():
    """Show data visualization dashboard."""
    st.title("名刺データの可視化")

    # Fetch data
    cards_df = fetch_all_cards()
    if cards_df.empty:
        st.error("名刺データを取得できませんでした。")
        return

    contacts_df = fetch_all_contacts()

    # Company selection
    selected_companies = _display_company_selection(cards_df)

    # Display maps
    st.markdown("## 地理的分布")

    tab1, tab2 = st.tabs(["都道府県マップ", "主要都市マップ"])

    with tab1:
        prefecture_map = create_prefecture_map(cards_df)
        st.plotly_chart(prefecture_map, use_container_width=True)

    with tab2:
        city_map = create_major_cities_company_map(cards_df, selected_companies)
        if city_map:
            st.plotly_chart(city_map, use_container_width=True)

    # Display contact analysis
    _display_contact_analysis(contacts_df)


if __name__ == "__main__":
    show_visualization()

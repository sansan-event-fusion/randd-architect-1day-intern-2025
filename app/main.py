from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# タイトル
st.title("Cards & Contacts Data Viewer")

# API設定
API_BASE_URL = st.sidebar.text_input("API Base URL", value="https://circuit-trial.stg.rd.ds.sansan.com")

# セッションステートの初期化
if "all_cards_data" not in st.session_state:
    st.session_state.all_cards_data = pd.DataFrame()
if "all_contacts_data" not in st.session_state:
    st.session_state.all_contacts_data = pd.DataFrame()
if "merged_data" not in st.session_state:
    st.session_state.merged_data = pd.DataFrame()
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "total_count" not in st.session_state:
    st.session_state.total_count = 0

# データ取得関数
@st.cache_data
def fetch_data(base_url: str, endpoint: str, offset: int = 0, limit: int = 50) -> dict[str, Any] | None:
    url = f"{base_url}/api/{endpoint}/"
    params = {"offset": offset, "limit": limit}
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

# 全データ取得関数
@st.cache_data
def fetch_all_data(base_url: str, endpoint: str) -> pd.DataFrame:
    all_data: list[dict[str, Any]] = []
    offset = 0
    limit = 1000

    progress_bar = st.progress(0)
    status_text = st.empty()

    while True:
        status_text.text(f"{endpoint} データ取得中... (取得済み: {len(all_data)}件)")

        data = fetch_data(base_url, endpoint, offset, limit)
        if not data:
            break

        # データの形式を判定
        if isinstance(data, list):
            current_batch = data
        elif isinstance(data, dict) and "results" in data:
            current_batch = data["results"]
        elif isinstance(data, dict):
            current_batch = [data]
        else:
            break

        if not current_batch:
            break

        all_data.extend(current_batch)

        # APIから返されたデータ数がlimitより少ない場合は終了
        if len(current_batch) < limit:
            break

        offset += limit
        progress_bar.progress(min(offset / 1000, 1.0))

    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

# データマージ関数
def merge_cards_contacts(cards_df: pd.DataFrame, contacts_df: pd.DataFrame) -> pd.DataFrame:
    if cards_df.empty or contacts_df.empty:
        return pd.DataFrame()

    # cardsデータに owner情報を追加
    merged = cards_df.merge(
        contacts_df[["user_id", "owner_user_id", "owner_company_id", "created_at"]],
        on="user_id",
        how="left",
        suffixes=("", "_contact")
    )

    # owner_user_idを使ってowner情報を取得
    owner_info = cards_df[["user_id", "full_name", "company_name", "position"]].rename(columns={
        "user_id": "owner_user_id",
        "full_name": "owner_full_name",
        "company_name": "owner_company_name",
        "position": "owner_position"
    })

    # owner情報をマージ
    final_merged = merged.merge(
        owner_info,
        on="owner_user_id",
        how="left"
    )

    return final_merged

# データ表示用の関数
def display_paginated_data(df: pd.DataFrame, page: int, items_per_page: int = 50) -> pd.DataFrame:
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    return df.iloc[start_idx:end_idx]

# メイン処理
st.subheader("データ取得")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Cardsデータを取得"):
        with st.spinner("Cardsデータを取得中..."):
            st.session_state.all_cards_data = fetch_all_data(API_BASE_URL, "cards")

        if not st.session_state.all_cards_data.empty:
            st.success(f"Cardsデータの取得が完了しました (合計: {len(st.session_state.all_cards_data)}件)")
        else:
            st.error("Cardsデータが取得できませんでした")

with col2:
    if st.button("Contactsデータを取得"):
        with st.spinner("Contactsデータを取得中..."):
            st.session_state.all_contacts_data = fetch_all_data(API_BASE_URL, "contacts")

        if not st.session_state.all_contacts_data.empty:
            st.success(f"Contactsデータの取得が完了しました (合計: {len(st.session_state.all_contacts_data)}件)")
        else:
            st.error("Contactsデータが取得できませんでした")

with col3:
    if st.button("データをマージ"):
        if not st.session_state.all_cards_data.empty and not st.session_state.all_contacts_data.empty:
            with st.spinner("データをマージ中..."):
                st.session_state.merged_data = merge_cards_contacts(
                    st.session_state.all_cards_data,
                    st.session_state.all_contacts_data
                )
                st.session_state.current_page = 0
                st.session_state.total_count = len(st.session_state.merged_data)

            if not st.session_state.merged_data.empty:
                st.success(f"データのマージが完了しました (合計: {st.session_state.total_count}件)")
            else:
                st.error("データのマージに失敗しました")
        else:
            st.error("CardsデータとContactsデータの両方を取得してからマージしてください")

# データクリア
if st.button("全データをクリア"):
    st.session_state.all_cards_data = pd.DataFrame()
    st.session_state.all_contacts_data = pd.DataFrame()
    st.session_state.merged_data = pd.DataFrame()
    st.session_state.current_page = 0
    st.session_state.total_count = 0
    st.success("全データをクリアしました")

# マージされたデータが存在する場合の表示
if not st.session_state.merged_data.empty:
    total_pages = (st.session_state.total_count - 1) // 50 + 1

    # ページネーション制御
    st.subheader("マージされたデータ一覧")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("前のページ") and st.session_state.current_page > 0:
            st.session_state.current_page -= 1

    with col2:
        st.write(f"ページ {st.session_state.current_page + 1} / {total_pages} (全{st.session_state.total_count}件)")

    with col3:
        if st.button("次のページ") and st.session_state.current_page < total_pages - 1:
            st.session_state.current_page += 1

    # 現在のページのデータを表示
    current_page_data = display_paginated_data(st.session_state.merged_data, st.session_state.current_page)

    # 表示カラムの選択
    all_columns = st.session_state.merged_data.columns.tolist()
    selected_columns: list[str] = st.multiselect(
        "表示するカラムを選択",
        all_columns,
        default=["user_id", "full_name", "company_name", "position",
                "owner_user_id", "owner_full_name", "owner_company_name", "owner_position"]
    )

    display_data = current_page_data[selected_columns] if selected_columns else current_page_data

    st.dataframe(display_data, use_container_width=True)

    # データの可視化
    st.subheader("データ可視化")

    # 名刺所有者の分布
    if "owner_full_name" in st.session_state.merged_data.columns:
        owner_counts = st.session_state.merged_data["owner_full_name"].value_counts().head(20)
        fig = px.bar(
            x=owner_counts.values,
            y=owner_counts.index,
            orientation="h",
            title="名刺所有者別の名刺数 (上位20名)",
            labels={"x": "名刺数", "y": "所有者名"}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    # 会社別の分布
    if "company_name" in st.session_state.merged_data.columns:
        company_counts = st.session_state.merged_data["company_name"].value_counts().head(15)
        fig = px.pie(
            values=company_counts.values,
            names=company_counts.index,
            title="会社別の名刺分布 (上位15社)"
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("「Cardsデータを取得」→「Contactsデータを取得」→「データをマージ」の順番でボタンをクリックしてください")

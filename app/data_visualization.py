import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# APIのベースURL
BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api"


def fetch_all_cards():
    """全ての名刺データを取得"""
    cards = []
    offset = 0
    limit = 100

    while True:  # テスト
        response = requests.get(
            f"{BASE_URL}/cards/", params={"offset": offset, "limit": limit}, timeout=30  # タイムアウトを30秒に設定
        )
        data = response.json()
        if not data:
            break
        cards.extend(data)
        if len(data) < limit:
            break
        offset += limit

    return pd.DataFrame(cards)


def fetch_all_contacts():
    """全てのコンタクト履歴を取得"""
    contacts = []
    offset = 0
    limit = 100

    while True:
        response = requests.get(
            f"{BASE_URL}/contacts/", params={"offset": offset, "limit": limit}, timeout=30  # タイムアウトを30秒に設定
        )
        data = response.json()
        if not data:
            break
        contacts.extend(data)
        if len(data) < limit:
            break
        offset += limit

    return pd.DataFrame(contacts)


def main():
    st.title("Sansan データ可視化ダッシュボード")

    # データ取得
    with st.spinner("名刺データを取得中..."):
        cards_df = fetch_all_cards()

    with st.spinner("コンタクト履歴を取得中..."):
        contacts_df = fetch_all_contacts()

    # 基本統計
    st.header("基本統計")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("総名刺数", len(cards_df))
    with col2:
        st.metric("総コンタクト数", len(contacts_df))

    # 会社ごとの名刺数の分布
    st.header("会社ごとの名刺数の分布")
    company_counts = cards_df["company_name"].value_counts().head(10)
    fig = px.bar(
        x=company_counts.index,
        y=company_counts.values,
        labels={"x": "会社名", "y": "名刺数"},
        title="Top 10 会社の名刺数",
    )
    st.plotly_chart(fig)

    # 役職の分布
    st.header("役職の分布")
    position_counts = cards_df["position"].value_counts().head(10)
    fig = px.pie(values=position_counts.values, names=position_counts.index, title="Top 10 役職の分布")
    st.plotly_chart(fig)

    # コンタクト履歴の時系列分析
    if not contacts_df.empty:
        st.header("コンタクト履歴の時系列分析")
        contacts_df["created_at"] = pd.to_datetime(contacts_df["created_at"])
        contacts_by_date = contacts_df.groupby(contacts_df["created_at"].dt.date).size()
        fig = px.line(
            x=contacts_by_date.index,
            y=contacts_by_date.values,
            labels={"x": "日付", "y": "コンタクト数"},
            title="日別コンタクト数の推移",
        )
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()

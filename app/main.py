"""
名刺・コンタクト可視化ダッシュボード（パフォーマンス最適化 + 重複列バグ修正）
====================================================================
100k 件規模でもフリーズせず、列名重複による `ValueError` を解決した最新版。
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

import networkx as nx
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from pyvis.network import Network
from requests.adapters import HTTPAdapter, Retry
from streamlit.components.v1 import html

# ------------------------------------------------------------
# ページ設定
# ------------------------------------------------------------
st.set_page_config(
    page_title="名刺・コンタクト可視化ダッシュボード",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 名刺・コンタクト可視化ダッシュボード")

# ------------------------------------------------------------
# 定数 & ユーティリティ
# ------------------------------------------------------------
BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api"
CARDS_ENDPOINT = f"{BASE_URL}/cards/"
CONTACTS_ENDPOINT = f"{BASE_URL}/contacts/"
DEFAULT_LIMIT = 100
TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # 秒

# HTTP リトライ付きセッション
_session = requests.Session()
retries = Retry(total=3, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=retries))

# 非同期 CSV 読込用スレッドプール
_executor = ThreadPoolExecutor(max_workers=2)

# ------------------------------------------------------------
# API 取得関数（キャッシュ）
# ------------------------------------------------------------


@st.cache_data(show_spinner=False)
def fetch_all(endpoint: str) -> List[Dict]:
    """limit/offset で全件取得してリスト返却"""
    offset, rows = 0, []
    while True:
        resp = _session.get(endpoint, params={"limit": DEFAULT_LIMIT, "offset": offset}, timeout=TIMEOUT)
        resp.raise_for_status()
        chunk = resp.json()
        if not chunk:
            break
        rows.extend(chunk)
        offset += DEFAULT_LIMIT
    return rows


@st.cache_data(show_spinner=False)
def df_from_rows(rows: List[Dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def read_csv_async(file) -> pd.DataFrame:
    return pd.read_csv(file)


# ------------------------------------------------------------
# データ取得（API → Fallback CSV）
# ------------------------------------------------------------


def get_resource(endpoint: str, label: str):
    with st.spinner(f"{label} 取得中…"):
        try:
            rows = fetch_all(endpoint)
            return df_from_rows(rows)
        except Exception as e:
            uploaded = st.sidebar.file_uploader(f"{label} CSV アップロード", type="csv")
            if uploaded:
                return _executor.submit(read_csv_async, uploaded).result()
            else:
                st.error(f"{label} の取得に失敗しました: {e}")
                st.stop()


# 実際の取得
_df_cards = get_resource(CARDS_ENDPOINT, "名刺データ")
_df_contacts = get_resource(CONTACTS_ENDPOINT, "コンタクト履歴データ")

st.success(f"名刺 データ ({len(_df_cards):,} 件) を取得しました。")
st.success(f"コンタクト履歴 データ ({len(_df_contacts):,} 件) を取得しました。")


# ------------------------------------------------------------
# 前処理 & キャッシュ
# ------------------------------------------------------------
@st.cache_data(show_spinner=False)
def enrich_contacts(df_cards: pd.DataFrame, df_contacts: pd.DataFrame) -> pd.DataFrame:
    df_contacts = df_contacts.copy()
    if "created_at" in df_contacts.columns:
        df_contacts["created_at"] = pd.to_datetime(df_contacts["created_at"], errors="coerce")
    master = df_cards.set_index("user_id")[["full_name", "company_name", "address"]]
    out = df_contacts
    for side, key in [("owner", "owner_user_id"), ("target", "user_id")]:
        out = out.merge(master.add_prefix(f"{side}_"), left_on=key, right_index=True, how="left")
    return out


contacts_enriched = enrich_contacts(_df_cards, _df_contacts)

# ------------------------------------------------------------
# サイドバー: 日付フィルタ
# ------------------------------------------------------------
min_d = contacts_enriched["created_at"].min().date()
max_d = contacts_enriched["created_at"].max().date()
start_d, end_d = st.sidebar.date_input("期間", [min_d, max_d], min_value=min_d, max_value=max_d)
if isinstance(start_d, list):
    start_d, end_d = start_d
mask = contacts_enriched["created_at"].dt.date.between(start_d, end_d)
contacts_filtered = contacts_enriched.loc[mask]
st.sidebar.caption(f"{len(contacts_filtered):,} 件を表示中")


# ------------------------------------------------------------
# 可視化 1: 日次頻度
# ------------------------------------------------------------
@st.cache_data(show_spinner=False)
def daily_counts(df: pd.DataFrame):
    return df[["created_at"]].set_index("created_at").resample("D").size().reset_index(name="count")


st.subheader("🗓️ 接点発生頻度 (日次)")
fig_daily = px.bar(
    daily_counts(contacts_filtered), x="created_at", y="count", labels={"created_at": "Date", "count": "Count"}
)
st.plotly_chart(fig_daily, use_container_width=True)

# ------------------------------------------------------------
# 可視化 2: ネットワークグラフ
# ------------------------------------------------------------
NODE_LIMIT, EDGE_LIMIT = 400, 1000
n_nodes = contacts_filtered[["owner_user_id", "user_id"]].stack().nunique()
unique_edges = contacts_filtered[["owner_user_id", "user_id"]].drop_duplicates().shape[0]

st.subheader("🔗 関係ネットワークグラフ")
if n_nodes > NODE_LIMIT or unique_edges > EDGE_LIMIT:
    st.warning(f"グラフ規模が大きいです (ノード {n_nodes:,} / エッジ {unique_edges:,})。期間を絞るなどしてください。")
else:
    G = nx.DiGraph()
    for _, r in contacts_filtered.iterrows():
        s, t = r["owner_user_id"], r["user_id"]
        if s == t:
            continue
        G.add_node(s, label=r.get("owner_full_name") or s)
        G.add_node(t, label=r.get("target_full_name") or t)
        if G.has_edge(s, t):
            G[s][t]["weight"] += 1
        else:
            G.add_edge(s, t, weight=1)
    net = Network(height="600px", width="100%", directed=True)
    net.from_nx(G)
    for e in net.edges:
        e["value"] = e.get("weight", 1)
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "graph.html")
        net.save_graph(p)
        html(open(p, encoding="utf-8").read(), height=650, scrolling=True)

# ------------------------------------------------------------
# 可視化 3: 集計テーブル
# ------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🥇 上位接触ペア")
    top_pairs = (
        contacts_filtered.groupby(["owner_full_name", "target_full_name"])
        .size()
        .reset_index(name="contact_count")
        .sort_values("contact_count", ascending=False)
    )
    st.dataframe(top_pairs.head(20), hide_index=True, use_container_width=True)

with col2:
    st.markdown("### 🏢 会社別接触数")
    # Duplicate column name bug fixed by explicitly naming contact_count
    top_companies = (
        contacts_filtered["target_company_name"].value_counts().rename_axis("company").reset_index(name="contact_count")
    )
    st.dataframe(top_companies.head(20), hide_index=True, use_container_width=True)

# ------------------------------------------------------------
# 詳細データ
# ------------------------------------------------------------
with st.expander("📄 フィルタ後データ"):
    st.dataframe(contacts_filtered, use_container_width=True)

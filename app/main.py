"""
みちび君 — 人脈ナビゲーションツール
(親密度 + 電話 + 役職 + 名刺交換日／経過日数)
------------------------------------------------------------
NEW (2025-06-14)
  • 「連絡したい相手」を役職でも選択可
  • 役職を指定した場合、その役職に該当する“全員分”の最短パスを一覧表示
------------------------------------------------------------
"""

# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import networkx as nx
import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter, Retry

# ------------------------------------------------------------
# Page config
# ------------------------------------------------------------
st.set_page_config(
    page_title="みちび君 | 人脈ナビゲーションツール",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("🤖 みちび君")

# ------------------------------------------------------------
# Constants & session
# ------------------------------------------------------------
BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api"
CARDS_ENDPOINT = f"{BASE_URL}/cards/"
CONTACTS_ENDPOINT = f"{BASE_URL}/contacts/"
DEFAULT_LIMIT = 100
TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
TODAY = pd.Timestamp(date.today())  # tz-naive

_session = requests.Session()
_session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1.5)))
_executor = ThreadPoolExecutor(max_workers=2)


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
@st.cache_data(ttl=3600, max_entries=20)
def fetch_all(endpoint: str) -> pd.DataFrame:
    rows, off = [], 0
    while True:
        r = _session.get(endpoint, params={"limit": DEFAULT_LIMIT, "offset": off}, timeout=TIMEOUT)
        r.raise_for_status()
        if not (chunk := r.json()):
            break
        rows.extend(chunk)
        off += DEFAULT_LIMIT
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600, max_entries=20)
def read_csv_async(f) -> pd.DataFrame:
    return pd.read_csv(f)


def acquire(endpoint: str, label: str) -> pd.DataFrame:
    with st.spinner(f"{label} を取得中…"):
        try:
            return fetch_all(endpoint)
        except Exception as e:
            up = st.sidebar.file_uploader(f"{label} CSV をアップロード", type="csv")
            if up:
                return _executor.submit(read_csv_async, up).result()
            st.error(f"{label} の取得に失敗しました: {e}")
            st.stop()


def badge(text: str, color: str) -> str:
    return (
        f'<span style="background:{color};color:#fff;padding:2px 6px;border-radius:6px;font-weight:bold;">{text}</span>'
    )


def intimacy_label(w: int, max_w: int) -> str:
    r = w / max_w if max_w else 0
    return "強" if r >= 0.7 else ("普" if r >= 0.4 else "弱")


# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------
cards_df = acquire(CARDS_ENDPOINT, "名刺データ")
contacts_df = acquire(CONTACTS_ENDPOINT, "名刺交換履歴")
st.success(f"名刺 {len(cards_df):,} 件 / 交換履歴 {len(contacts_df):,} 件 取得")

# ---- key columns
PHONE_COL = "phone_number" if "phone_number" in cards_df.columns else None
POSITION_COL = "position" if "position" in cards_df.columns else None

cols = ["full_name", "company_name"]
for c in [PHONE_COL, POSITION_COL]:
    if c:
        cols.append(c)

user_info: dict[str, dict[str, str]] = cards_df.set_index("user_id")[cols].fillna("").to_dict("index")
all_companies: list[str] = sorted(cards_df["company_name"].dropna().unique().tolist())

# contacts preprocessing (tz → naive)
contacts_df["created_at"] = pd.to_datetime(contacts_df["created_at"], errors="coerce").dt.tz_localize(None)

# ------------------------------------------------------------
# Sidebar UI
# ------------------------------------------------------------
st.sidebar.subheader("みちび君の設定")

# あなた選択
st.sidebar.write("### 🧑‍💼 あなた")
my_company = st.sidebar.selectbox("所属企業", options=all_companies)
my_candidates = cards_df.query("company_name == @my_company and full_name.notna()")
my_user_id: str = st.sidebar.selectbox(
    "あなたの名前",
    options=my_candidates["user_id"].tolist(),
    format_func=lambda x: user_info[x]["full_name"],
)
st.sidebar.info(f"あなた: {user_info[my_user_id]['full_name']} ({my_company})")

# 相手会社 & 役職フィルタ
st.sidebar.write("### 📞 連絡したい相手")
tg_company = st.sidebar.selectbox("相手の所属企業", options=all_companies)

# 役職フィルタ（オプション）
pos_options = []
if POSITION_COL:
    pos_options = sorted(cards_df.loc[cards_df["company_name"] == tg_company, POSITION_COL].dropna().unique())
select_role = None
if pos_options:
    select_role = st.sidebar.selectbox("役職で絞り込む (任意)", options=["(指定なし)"] + pos_options)

# 相手ユーザー選択（役職フィルタがない or 指定なしの場合のみ）
if not pos_options or select_role == "(指定なし)":
    tg_candidates = cards_df.query("company_name == @tg_company and full_name.notna()")
    tg_user_id: str = st.sidebar.selectbox(
        "相手の名前",
        options=tg_candidates["user_id"].tolist(),
        format_func=lambda x: user_info[x]["full_name"],
    )
    target_user_ids = [tg_user_id]
else:
    # 役職が指定された場合：該当者全員
    target_user_ids = cards_df.query("company_name == @tg_company and position == @select_role and full_name.notna()")[
        "user_id"
    ].tolist()
    st.sidebar.info(f"役職 '{select_role}' の該当者 {len(target_user_ids)} 名")

# ------------------------------------------------------------
# Validate
# ------------------------------------------------------------
if my_user_id in target_user_ids:
    st.warning("自分と相手が同じユーザーを含んでいます。除外します。")
    target_user_ids = [uid for uid in target_user_ids if uid != my_user_id]
if not target_user_ids:
    st.stop()

# ------------------------------------------------------------
# Build graph once
# ------------------------------------------------------------
G = nx.Graph()
for _, r in contacts_df.iterrows():
    a, b = r["owner_user_id"], r["user_id"]
    if a and b and a != b:
        G.add_edge(a, b, weight=G[a][b]["weight"] + 1 if G.has_edge(a, b) else 1)


# ------------------------------------------------------------
# Helper: first exchange date
# ------------------------------------------------------------
def first_exchange(uid: str) -> pd.Timestamp | None:
    filt = ((contacts_df["owner_user_id"] == my_user_id) & (contacts_df["user_id"] == uid)) | (
        (contacts_df["owner_user_id"] == uid) & (contacts_df["user_id"] == my_user_id)
    )
    s = contacts_df.loc[filt, "created_at"].dropna()
    return s.min() if not s.empty else None


# ------------------------------------------------------------
# Path calculation & display
# ------------------------------------------------------------
def build_path_df(path: list[str]) -> tuple[pd.DataFrame, str]:
    # max weight for intimacy scaling
    ws = [G[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1)] if len(path) > 1 else []
    max_w = max(ws) if ws else 1

    rows = []
    for i, uid in enumerate(path):
        info = user_info.get(uid, {})
        exch = first_exchange(uid)
        rows.append(
            {
                "ユーザーID": uid,
                "氏名": info.get("full_name", "不明"),
                "会社": info.get("company_name", "不明"),
                "役職": info.get(POSITION_COL, "") if POSITION_COL else "",
                "電話": info.get(PHONE_COL, "") if PHONE_COL else "",
                "名刺交換日": exch.strftime("%Y-%m-%d") if exch is not None else "",
                "交換からの日数": (TODAY - exch).days if exch is not None else "",
                "親密度": intimacy_label(G[uid][path[i + 1]]["weight"], max_w) if i < len(path) - 1 else "",
            }
        )
    df = pd.DataFrame(rows)

    # badge path
    b_list = []
    for uid in path:
        name = user_info.get(uid, {}).get("full_name", uid)
        if uid == my_user_id:
            b_list.append(badge(name, "#3b82f6"))
        elif uid in target_user_ids:
            b_list.append(badge(name, "#ef4444"))
        else:
            b_list.append(badge(name, "#f59e0b"))
    arrow_html = " ➡️ ".join(b_list)
    return df, arrow_html


# --- Iterate over targets -----------------------------------
for tgt in target_user_ids:
    try:
        path_nodes = nx.shortest_path(G, my_user_id, tgt)
    except nx.NetworkXNoPath:
        st.error(f"❌ {user_info[tgt]['full_name']} とのパスは見つかりませんでした。")
        continue

    df, arrow_html = build_path_df(path_nodes)

    with st.expander(
        f"📍 {user_info[tgt]['full_name']} へのルート（{len(path_nodes) - 1} ホップ）",
        expanded=len(target_user_ids) == 1,
    ):
        st.markdown(arrow_html, unsafe_allow_html=True)
        st.table(df)
        dl = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("CSV ダウンロード", dl, file_name=f"michibikun_path_{tgt}.csv", mime="text/csv")

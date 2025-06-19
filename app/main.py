import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import networkx as nx
import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter, Retry

st.set_page_config(
    page_title="みちび君 | 人脈ナビゲーション",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("# 🚀 みちび君\n### 最短ルートで “ご縁” をナビゲート！")

# ------------------------------------------------------------
# Constants & HTTP
# ------------------------------------------------------------
BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api"
CARDS_ENDPOINT = f"{BASE_URL}/cards/"
CONTACTS_ENDPOINT = f"{BASE_URL}/contacts/"
LIMIT = 100
TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
TODAY = pd.Timestamp(date.today())

sess = requests.Session()
sess.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1.5)))
pool = ThreadPoolExecutor(max_workers=2)


# ------------------------------------------------------------
# Utils
# ------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_all(url: str) -> pd.DataFrame:
    data, off = [], 0
    while True:
        r = sess.get(url, params={"limit": LIMIT, "offset": off}, timeout=TIMEOUT)
        r.raise_for_status()
        if not (chunk := r.json()):
            break
        data.extend(chunk)
        off += LIMIT
    return pd.DataFrame(data)


def badge(txt: str, color: str) -> str:
    return (
        f'<span style="background:{color};color:#fff;padding:2px 6px;border-radius:6px;font-weight:bold;">{txt}</span>'
    )


def intimacy(weight: int) -> str:
    return "強" if weight >= 10 else ("普" if weight >= 4 else "弱")


# ------------------------------------------------------------
# Data load
# ------------------------------------------------------------
cards_df = fetch_all(CARDS_ENDPOINT)
contacts_df = fetch_all(CONTACTS_ENDPOINT)
contacts_df["created_at"] = pd.to_datetime(contacts_df["created_at"], errors="coerce").dt.tz_localize(None)

PHONE_COL = next((c for c in cards_df.columns if "phone" in c.lower()), None)
POSITION_COL = next((c for c in cards_df.columns if c.lower() in ("position", "title", "役職")), None)

BASE_COLS = (
    ["full_name", "company_name"] + ([PHONE_COL] if PHONE_COL else []) + ([POSITION_COL] if POSITION_COL else [])
)
user_info: dict[str, dict[str, str]] = cards_df.set_index("user_id")[BASE_COLS].fillna("").to_dict("index")
companies = sorted(cards_df["company_name"].dropna().unique().tolist())

# ------------------------------------------------------------
# Step 1: あなたを session_state に保存
# ------------------------------------------------------------
if "my_user_id" not in st.session_state:
    st.sidebar.markdown("### 🧑‍💼 あなたのプロフィール設定")
    my_company = st.sidebar.selectbox("所属企業", options=companies, key="sel_my_company")
    my_candidates = cards_df.query("company_name == @my_company and full_name.notna()")
    my_user_id: str = st.sidebar.selectbox(
        "あなたの名前",
        options=my_candidates["user_id"],
        format_func=lambda x: user_info[x]["full_name"],
        key="sel_my_user",
    )
    if st.sidebar.button("確定して次へ ▶️"):
        st.session_state["my_user_id"] = my_user_id
        st.session_state["my_company"] = my_company
        st.rerun()
    st.stop()  # プロフィール未確定の間はここで終了

# プロフィール確定後ここに来る
my_user_id = st.session_state["my_user_id"]
my_company = st.session_state["my_company"]
profile = user_info[my_user_id]
st.sidebar.markdown("### 📌 あなたのプロフィール")
st.sidebar.success(f"{profile['full_name']} ({my_company})")

# ------------------------------------------------------------
# Step 2: ターゲット設定
# ------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 連絡したい相手を選択")

tg_company = st.sidebar.selectbox("相手企業", options=companies, key="sel_tg_company")
role_opts = (
    sorted(cards_df.query("company_name == @tg_company")[POSITION_COL].dropna().unique()) if POSITION_COL else []
)
role_choice = st.sidebar.selectbox("役職フィルタ (任意)", ["(指定なし)"] + role_opts, key="sel_role")

if role_choice != "(指定なし)":
    tgt_df = cards_df.query("company_name == @tg_company and position == @role_choice and full_name.notna()")
    target_ids = tgt_df["user_id"].tolist()
    st.sidebar.info(f"該当者 {len(target_ids)} 名")
else:
    cand = cards_df.query("company_name == @tg_company and full_name.notna()")
    sel_id: str = st.sidebar.selectbox(
        "相手の名前", cand["user_id"], format_func=lambda x: user_info[x]["full_name"], key="sel_tg_user"
    )
    target_ids = [sel_id]

# 自分除外
target_ids = [uid for uid in target_ids if uid != my_user_id]
if not target_ids:
    st.info("サイドバーで相手を選択してください。")
    st.stop()

# ------------------------------------------------------------
# Graph build
# ------------------------------------------------------------
G = nx.Graph()
for _, row in contacts_df.iterrows():
    a, b = row["owner_user_id"], row["user_id"]
    if a and b and a != b:
        G.add_edge(a, b, weight=G[a][b]["weight"] + 1 if G.has_edge(a, b) else 1)


def exchange_between(uid1: str, uid2: str) -> pd.Timestamp | None:
    m = ((contacts_df["owner_user_id"] == uid1) & (contacts_df["user_id"] == uid2)) | (
        (contacts_df["owner_user_id"] == uid2) & (contacts_df["user_id"] == uid1)
    )
    s = contacts_df.loc[m, "created_at"].dropna()
    return s.min() if not s.empty else None


def first_exchange(uid: str) -> pd.Timestamp | None:
    m = ((contacts_df["owner_user_id"] == my_user_id) & (contacts_df["user_id"] == uid)) | (
        (contacts_df["owner_user_id"] == uid) & (contacts_df["user_id"] == my_user_id)
    )
    s = contacts_df.loc[m, "created_at"].dropna()
    return s.min() if not s.empty else None


def path_details(path: list[str]) -> tuple[pd.DataFrame, str]:
    rows = []
    for i, uid in enumerate(path):
        info = user_info[uid]

        # --- 交換日: 先頭ノード以外は「前ノード」との最初の交換日を表示
        exch = exchange_between(path[i - 1], uid) if i > 0 else None
        date_disp = f"{exch:%Y-%m-%d}（{(TODAY - exch).days}日経過）" if exch is not None else ""

        rows.append(
            {
                "氏名": info["full_name"],
                "会社": info["company_name"],
                "役職": info.get(POSITION_COL, "") if POSITION_COL else "",
                "電話": info.get(PHONE_COL, "") if PHONE_COL else "",
                "名刺交換": date_disp,
                "親密度": intimacy(G[uid][path[i + 1]]["weight"]) if i < len(path) - 1 else "",
            }
        )

    df = pd.DataFrame(rows)

    # --- バッジ付きルート文字列
    badges = []
    for uid in path:
        name = user_info[uid]["full_name"]
        if uid == my_user_id:
            badges.append(badge(name, "#3b82f6"))
        elif uid in target_ids:
            badges.append(badge(name, "#ef4444"))
        else:
            badges.append(badge(name, "#f59e0b"))
    return df, " ➡️ ".join(badges)


# ------------------------------------------------------------
# Display paths
# ------------------------------------------------------------
for tgt in target_ids:
    try:
        p_nodes = nx.shortest_path(G, my_user_id, tgt)
    except nx.NetworkXNoPath:
        st.error(f"❌ {user_info[tgt]['full_name']} との経路は見つかりません。")
        continue

    df, route_html = path_details(p_nodes)
    with st.expander(
        f"📍 {user_info[tgt]['full_name']} へのルート（{len(p_nodes) - 1} ホップ）", expanded=len(target_ids) == 1
    ):
        st.markdown(route_html, unsafe_allow_html=True)
        st.table(df)
        st.download_button(
            "CSV ダウンロード",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"michibikun_{tgt}.csv",
            mime="text/csv",
        )

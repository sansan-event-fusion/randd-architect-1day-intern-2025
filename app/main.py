from typing import Any

import requests
import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph


def get_cards_count() -> int:
    """ビジネスカードの総数を取得"""
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_all_cards() -> list[dict[str, Any]]:
    """全ビジネスカードを取得"""
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
    response = requests.get(url, params={"offset": 0, "limit": get_cards_count()}, timeout=30)
    response.raise_for_status()
    return response.json()


def select_cards(cards: list[dict[str, Any]], company_name: str) -> list[dict[str, Any]]:
    """会社名でカードをフィルタ"""
    return [card for card in cards if card["company_name"] == company_name]


def get_all_contacts(owner_company_id: int) -> list[dict[str, Any]]:
    """コンタクト関係を取得"""
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/{owner_company_id}"
    response = requests.get(url, params={"offset": 0, "limit": 100}, timeout=30)
    response.raise_for_status()
    return response.json()


def create_connection_graph(cards: list[dict[str, Any]], contacts: list[dict[str, Any]], max_owners: int = 10) -> None:
    """owner_user_idとuser_idの関係をグラフで可視化"""
    user_id_to_name = {card["user_id"]: card["full_name"] for card in cards}

    # 接続先ユーザーの次数を計算
    target_degree = {}
    for contact in contacts:
        target_id = contact["user_id"]
        target_degree[target_id] = target_degree.get(target_id, 0) + 1

    # 次数2以上の接続先ユーザーのみフィルタ
    filtered_contacts = [c for c in contacts if target_degree[c["user_id"]] >= 2]

    # カード所有者を最大数まで制限
    owner_ids = list({c["owner_user_id"] for c in filtered_contacts})
    limited_owner_ids = owner_ids[:max_owners]

    # 制限された所有者の接続のみ使用
    final_contacts = [c for c in filtered_contacts if c["owner_user_id"] in limited_owner_ids]

    nodes = []
    edges = []

    for contact in final_contacts:
        owner_id = contact["owner_user_id"]
        target_id = contact["user_id"]

        owner_name = user_id_to_name.get(owner_id, f"User {owner_id}")
        target_name = user_id_to_name.get(target_id, f"User {target_id}")

        nodes.extend(
            [
                Node(
                    id=owner_id,
                    label=owner_name,
                    size=25,
                    shape="circle",
                    color="#FF6B6B",
                    font={"color": "white", "size": 12, "strokeWidth": 2, "strokeColor": "black"},
                ),
                Node(
                    id=target_id,
                    label=target_name,
                    size=20,
                    shape="circle",
                    color="#4ECDC4",
                    font={"color": "white", "size": 10, "strokeWidth": 2, "strokeColor": "black"},
                ),
            ]
        )

        edges.append(
            Edge(
                source=owner_id,
                target=target_id,
                color="#95A5A6",
                width=2,
                smooth={"type": "curvedCW", "roundness": 0.2},
            )
        )

    nodes = list({node.id: node for node in nodes}.values())

    config = Config(
        height=600,
        width=800,
        directed=True,
        physics={
            "enabled": True,
            "hierarchicalRepulsion": {
                "centralGravity": 0.3,
                "springLength": 100,
                "springConstant": 0.01,
                "nodeDistance": 200,
                "damping": 0.09,
            },
            "maxVelocity": 50,
            "minVelocity": 0.1,
            "solver": "hierarchicalRepulsion",
            "stabilization": {"enabled": True, "iterations": 1000, "updateInterval": 25},
            "timestep": 0.5,
            "adaptiveTimestep": True,
        },
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False,
        layout={"hierarchical": {"enabled": False}},
    )
    agraph(nodes, edges, config)


def main():
    st.title("📊 ビジネスカード接続関係の可視化")

    # データ取得
    with st.spinner("💳 ビジネスカードデータを読み込んでいます..."):
        all_cards = get_all_cards()

    # 全会社名を取得
    all_companies = sorted({card["company_name"] for card in all_cards})

    # サイドバー設定
    st.sidebar.header("⚙️ 設定")

    # 会社検索機能
    search_query = st.sidebar.text_input("🔍 会社名で検索", placeholder="例: 株式会社")

    # 検索結果をフィルタ
    if search_query:
        filtered_companies = [c for c in all_companies if search_query.lower() in c.lower()]
    else:
        filtered_companies = all_companies

    if not filtered_companies:
        st.sidebar.error("❌ 該当する会社が見つかりませんでした")
        return

    company_name = st.sidebar.selectbox("🏢 分析対象の会社を選択", filtered_companies)
    max_owners = st.sidebar.slider(
        "👥 表示する名刺所有者の最大数", 1, 50, 10, help="グラフの見やすさのため、表示する名刺所有者数を制限できます"
    )
    cards = select_cards(all_cards, company_name)

    if not cards:
        st.error(f"❌ {company_name}の名刺が見つかりませんでした")
        return

    contacts = get_all_contacts(cards[0]["company_id"])

    if not contacts:
        st.warning("⚠️ この会社の接続関係データが見つかりませんでした")
        return

    # 統計情報
    st.sidebar.subheader("📈 統計情報")
    st.sidebar.metric("💳 名刺数", len(cards), help="選択した会社の名刺総数")
    st.sidebar.metric("🔗 接続関係数", len(contacts), help="この会社から他社への接続関係の総数")

    # グラフ説明
    st.subheader(f"🌐 {company_name} の接続関係マップ")
    col1, col2 = st.columns(2)
    with col1:
        st.info("🔴 赤いノード: 名刺所有者\n (選択した会社の社員)")
    with col2:
        st.info("🔵 青いノード: 接続先の方\n (他社の方で複数の接続を持つ方)")
    st.caption("💡 ヒント: ノードをクリックしてハイライト表示、ドラッグで位置調整ができます")

    # グラフ表示
    create_connection_graph(all_cards, contacts, max_owners)

    # データ詳細
    with st.expander("📋 生データの詳細を表示"):
        st.subheader("💳 名刺データサンプル")
        st.json(cards[:2])
        st.subheader("🔗 接続データサンプル")
        st.json(contacts[:2])


if __name__ == "__main__":
    main()

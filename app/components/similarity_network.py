import pandas as pd
import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph

from app.crud import BusinessCardCRUD


def display_similarity_analysis(cards_crud: BusinessCardCRUD, card_limit: int) -> None:  # noqa: C901
    """インタラクティブ類似度ネットワーク分析."""
    st.subheader("🕸️ 類似度ネットワーク分析")

    # 説明文
    st.info("💡 ユーザーを選択すると **類似度上位10名** のネットワークを表示。ノードをクリックして探索できます!")

    # セッションステートの初期化
    if "network_nodes" not in st.session_state:
        st.session_state.network_nodes = {}
    if "network_edges" not in st.session_state:
        st.session_state.network_edges = []
    if "center_user_id" not in st.session_state:
        st.session_state.center_user_id = None

    # サンプルユーザー数の設定
    sample_limit = min(50, card_limit)
    sample_cards = cards_crud.get_all_cards(limit=sample_limit)

    if not sample_cards:
        st.warning("名刺データがありません")
        return

    # 初期ユーザー選択
    user_options = {f"{card.full_name} ({card.company_name})": card.user_id for card in sample_cards}
    selected_user_display = st.selectbox("開始ユーザーを選択", list(user_options.keys()))
    selected_user_id = user_options[selected_user_display]

    # ネットワーク初期化ボタン
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 ネットワーク構築"):
            st.session_state.network_nodes = {}
            st.session_state.network_edges = []
            st.session_state.center_user_id = selected_user_id
            build_similarity_network(cards_crud, selected_user_id)

    with col2:
        if st.button("🗑️ リセット"):
            st.session_state.network_nodes = {}
            st.session_state.network_edges = []
            st.session_state.center_user_id = None

    # ネットワーク表示
    if st.session_state.network_nodes:
        display_similarity_network(cards_crud)

        # ネットワーク統計
        display_network_statistics()
    else:
        st.info("「🔄 ネットワーク構築」ボタンを押してネットワークを開始してください")


def build_similarity_network(cards_crud: BusinessCardCRUD, user_id: str) -> None:  # noqa: C901
    """類似度ネットワークを構築."""
    try:
        # 中心ユーザーの情報を取得
        center_user = cards_crud.get_card_by_user_id(int(user_id))

        if user_id not in st.session_state.network_nodes:
            st.session_state.network_nodes[user_id] = {
                "id": user_id,
                "label": f"{center_user.full_name}\n({center_user.company_name})",
                "title": f"類似度分析の中心\n{center_user.full_name}\n{center_user.company_name}",
                "color": "#ff6b6b",  # 赤色で中心を強調
                "size": 30,
                "shape": "dot",
            }

        # 類似ユーザーを取得
        similar_users = cards_crud.get_similar_users(int(user_id))

        for user in similar_users:
            if user.user_id not in st.session_state.network_nodes:
                if user.similarity >= 0.9:
                    color = "#ff9f43"  # オレンジ(高類似度)
                    size = 25
                elif user.similarity >= 0.8:
                    color = "#10ac84"  # 緑(中類似度)
                    size = 20
                else:
                    color = "#3742fa"  # 青(標準類似度)
                    size = 15

                st.session_state.network_nodes[user.user_id] = {
                    "id": user.user_id,
                    "label": f"{user.full_name}\n({user.company_name})",
                    "title": f"類似度: {user.similarity:.3f}\n{user.full_name}\n{user.company_name}",
                    "color": color,
                    "size": size,
                    "shape": "dot",
                }

            edge_exists = any(
                (edge["from"] == user_id and edge["to"] == user.user_id)
                or (edge["from"] == user.user_id and edge["to"] == user_id)
                for edge in st.session_state.network_edges
            )

            if not edge_exists:
                width = max(1, int(user.similarity * 5))

                st.session_state.network_edges.append(
                    {
                        "from": user_id,
                        "to": user.user_id,
                        "label": f"{user.similarity:.3f}",
                        "width": width,
                        "color": {"color": "#95a5a6", "opacity": 0.7},
                    }
                )

    except Exception as e:  # noqa: BLE001
        st.error(f"ネットワーク構築エラー: {e!s}")


def display_similarity_network(cards_crud: BusinessCardCRUD) -> None:
    """類似度ネットワークを表示."""
    nodes = [
        Node(
            id=node_data["id"],
            label=node_data["label"],
            title=node_data["title"],
            color=node_data["color"],
            size=node_data["size"],
            shape=node_data["shape"],
        )
        for node_data in st.session_state.network_nodes.values()
    ]

    edges = [
        Edge(
            source=edge_data["from"],
            target=edge_data["to"],
            label=edge_data["label"],
            width=edge_data["width"],
            color=edge_data["color"],
        )
        for edge_data in st.session_state.network_edges
    ]

    # グラフ設定
    config = Config(
        height=600,
        width="100%",
        directed=False,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False,
    )

    # ネットワーク表示
    selected_node = agraph(nodes=nodes, edges=edges, config=config)

    # ノードクリック時の処理
    if selected_node:
        clicked_user_id = selected_node
        st.info(f"選択されたノード: {clicked_user_id}")

        # クリックされたノードを中心に新しいネットワークを展開
        if st.button(f"🔍 {clicked_user_id} を中心に展開"):
            build_similarity_network(cards_crud, clicked_user_id)
            st.rerun()


def display_network_statistics() -> None:
    """ネットワーク統計を表示."""
    st.subheader("📊 ネットワーク統計")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("ノード数", len(st.session_state.network_nodes))

    with col2:
        st.metric("エッジ数", len(st.session_state.network_edges))

    with col3:
        # 平均類似度を計算
        if st.session_state.network_edges:
            similarities = [float(edge["label"]) for edge in st.session_state.network_edges]
            avg_similarity = sum(similarities) / len(similarities)
            st.metric("平均類似度", f"{avg_similarity:.3f}")
        else:
            st.metric("平均類似度", "N/A")

    with col4:
        # 最高類似度を計算
        if st.session_state.network_edges:
            max_similarity = max(float(edge["label"]) for edge in st.session_state.network_edges)
            st.metric("最高類似度", f"{max_similarity:.3f}")
        else:
            st.metric("最高類似度", "N/A")

    # ノード詳細情報
    if st.session_state.network_nodes:
        st.subheader("🎯 ネットワーク内ノード")
        node_info = [
            {
                "ユーザーID": node_data["id"],
                "名前・会社": node_data["label"].replace("\n", " "),
                "ノード色": "🔴 中心"
                if node_data["color"] == "#ff6b6b"
                else "🟠 高類似"
                if node_data["color"] == "#ff9f43"
                else "🟢 中類似"
                if node_data["color"] == "#10ac84"
                else "🔵 標準",
            }
            for node_data in st.session_state.network_nodes.values()
        ]

        df_nodes = pd.DataFrame(node_info)
        st.dataframe(df_nodes, use_container_width=True)

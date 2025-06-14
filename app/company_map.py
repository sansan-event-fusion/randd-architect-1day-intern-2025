import pandas as pd
import requests
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# --- 定数定義 ---
# APIのベースURL
API_BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com"


@st.cache_data(ttl=600) # 10分間キャッシュ
def fetch_api_data(endpoint: str) -> list:
    """
    指定されたAPIエンドポイントからデータを取得します。
    """
    api_url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    return response.json()

def analyze_company_connections(contacts: list, cards: list) -> tuple:
    """
    名刺交換履歴と名刺情報から、企業間のつながりを分析します。
    """
    df_cards = pd.DataFrame(cards)
    unique_companies = df_cards[['company_id', 'company_name']].drop_duplicates().set_index('company_id')
    company_map = unique_companies['company_name'].to_dict()

    connection_counts = {}
    for contact in contacts:
        id1 = contact.get("owner_company_id")
        id2 = contact.get("company_id")
        if not id1 or not id2 or id1 == id2:
            continue
        pair = tuple(sorted((id1, id2)))
        connection_counts[pair] = connection_counts.get(pair, 0) + 1

    return connection_counts, company_map

# --- StreamlitのUIロジック ---
st.set_page_config(layout="wide")
st.title("企業間関係性分析マップ")
st.markdown("APIから取得した名刺交換履歴を基に、企業間のつながりの強さを可視化します。")

# Session Stateを初期化
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
    st.session_state.connection_counts = {}
    st.session_state.company_map = {}

# --- サイドバー ---
st.sidebar.header("操作パネル")
if st.sidebar.button("分析を実行する", type="primary"):
    with st.spinner("APIからデータを取得し、分析しています... (数十秒かかる場合があります)"):
        try:
            contacts_data = fetch_api_data("/api/contacts/")
            cards_data = fetch_api_data("/api/cards/")
            if contacts_data and cards_data:
                st.session_state.connection_counts, st.session_state.company_map = analyze_company_connections(contacts_data, cards_data)
                st.session_state.analysis_done = True
                st.success("分析が完了しました。")
            else:
                st.warning("APIから十分なデータを取得できませんでした。")
                st.session_state.analysis_done = False
        except requests.exceptions.RequestException as e:
            st.error(f"APIの呼び出しに失敗しました: {e}")
            st.session_state.analysis_done = False
        except Exception as e:
            st.error(f"予期せぬエラーが発生しました: {e}")
            st.session_state.analysis_done = False

# --- メインコンテンツ（分析後に表示） ---
if st.session_state.analysis_done:
    if not st.session_state.connection_counts:
        st.warning("分析の結果、企業間の関係性が見つかりませんでした。")
    else:
        # スライダーの最大値とデフォルト値を安全に設定
        max_val = max(st.session_state.connection_counts.values())
        default_val = min(10, max_val)
        
        st.sidebar.header("表示フィルタ")
        min_exchanges = st.sidebar.slider(
            "表示する最小交換回数:",
            min_value=1,
            max_value=max_val,
            value=default_val,
            step=1
        )

        # フィルタリングされたグラフデータを準備
        nodes = []
        edges = []
        company_nodes = set()
        for pair, count in st.session_state.connection_counts.items():
            if count >= min_exchanges:
                id1, id2 = pair
                name1 = st.session_state.company_map.get(id1, str(id1))
                name2 = st.session_state.company_map.get(id2, str(id2))

                if id1 not in company_nodes:
                    nodes.append(Node(id=str(id1), label=name1, size=15))
                    company_nodes.add(id1)
                if id2 not in company_nodes:
                    nodes.append(Node(id=str(id2), label=name2, size=15))
                    company_nodes.add(id2)
                
                edges.append(Edge(source=str(id1), target=str(id2), value=count, label=str(count)))

        if not nodes:
            st.info(f"交換回数が {min_exchanges} 回以上の関係性はありませんでした。")
        else:
            # グラフの描画設定
            config = Config(
                width="100%",
                height=800,
                directed=False,
                physics=True,
                hierarchical=False,
                node={'labelProperty':'label'},
                link={'labelProperty': 'label', 'renderLabel': True}
            )
            # グラフを描画
            agraph(nodes=nodes, edges=edges, config=config)

else:
    st.info("サイドバーの「分析を実行する」ボタンを押して、分析を開始してください。")

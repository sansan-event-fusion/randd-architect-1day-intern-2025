from datetime import datetime, timezone
from pathlib import Path

import networkx as nx
import streamlit as st
import streamlit.components.v1 as components
from api import BusinessCardAPI
from datatype import BusinessCard, ExchangeHistory
from pyvis.network import Network

# タイトル
st.title("名刺リレーション表示アプリv0.0.2")

api = BusinessCardAPI("https://circuit-trial.stg.rd.ds.sansan.com/api")

cards: list[BusinessCard] = api.get_all_cards()
contacts: list[ExchangeHistory] = api.get_all_contacts()
di = {}
single_file_cards = []


for i, card in enumerate(cards):
    di[card.user_id] = i
    single_file_cards.append(card)


def card_display(card: BusinessCard):
    return f"""user_id:{card.user_id}
名前: {card.full_name}
会社名: {card.company_name}
役職: {card.position}
住所: {card.address}
電話番号: {card.phone_number}
類似度: {card.similarity}
"""


def history(u: int, v: int, date: datetime):
    # 文字列をdatetimeオブジェクトに変換
    dt = datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

    # "年月日 時間分"形式でフォーマット
    formatted_date = dt.strftime("%Y年%m月%d日 %H時%M分")
    return f"""WHEN
{formatted_date}

FROM
{card_display(single_file_cards[v])}

TO
{card_display(single_file_cards[u])}
"""


def display_graph(name: str, nodes=None):  # noqa: C901 これはロジックを大きく変える必要が出るので今回の時間では対応不可能
    key_toggle = f"show_graph_{name}"

    if name != "":
        top_cards = api.get_similar_users(name)

        se_top = {card.user_id for card in top_cards}

    if key_toggle not in st.session_state:
        st.session_state[key_toggle] = True  # 初期表示状態

    if st.session_state[key_toggle]:
        # グラフ作成
        gg = nx.DiGraph()
        if nodes is None:
            nodes = set()

        for i, card in enumerate(cards):
            if name == "" or card.user_id in se_top:
                gg.add_node(i, title=card_display(card), color="red")
                nodes.add(i)
            if card.user_id == name:
                gg.add_node(i, title=card_display(card), color="yellow")
                nodes.add(i)

        for contact in contacts:
            u = di.get(contact.owner_user_id)
            v = di.get(contact.user_id)
            if u in nodes or v in nodes:
                gg.add_node(u, title=card_display(card))
                gg.add_node(v, title=card_display(card))
                if u is not None and v is not None:
                    gg.add_edge(u, v, title=history(u, v, contact.created_at))

        # Pyvisで描画
        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
        net.barnes_hut(gravity=-1, central_gravity=0, spring_length=200)
        net.from_nx(gg)
        net.show_buttons(filter_=["physics"])
        net.save_graph(f"{name}.html")

        # with Path.open(f"{name}.html", encoding="utf-8") as f:
        with Path(f"{name}.html").open(encoding="utf-8") as f:
            html_content = f.read()

        # 非表示ボタン
        if st.button(f"{name}グラフを非表示にする", key=f"hide_btn_{name}"):
            st.session_state[key_toggle] = False
            st.rerun()
        components.html(html_content, height=600, scrolling=True)
    elif st.button(f"{name}グラフを再表示する", key=f"show_btn_{name}"):
        st.session_state[key_toggle] = True
        st.rerun()


if "graph_names" not in st.session_state:
    st.session_state.graph_names = []

# 新しい name 入力
new_name = st.text_input("新しいグラフ名を入力", key="name_input")
if st.button("追加", key="add_btn"):
    if new_name.strip():
        st.session_state.graph_names.append(new_name.strip())
    else:
        st.warning("グラフ名を入力してください。")

# 既存のグラフを表示
for name in st.session_state.graph_names:
    st.markdown("---")
    st.subheader(f"グラフ: {name}")
    display_graph(name)

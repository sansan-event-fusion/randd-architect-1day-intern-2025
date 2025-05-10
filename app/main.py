from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from api import BusinessCardAPI
from datatype import BusinessCard, ExchangeHistory
from pyvis.network import Network

# タイトル
st.title("mattsunkunアプリ")

api = BusinessCardAPI("https://circuit-trial.stg.rd.ds.sansan.com/api")

# print("asdf")
# st.title("カードAPIにアクセスする")
# cards = api.get_similar_users("9230809757")
# for card in cards:
#     st.write(f"名前: {card.full_name}")
#     st.write(f"会社名: {card.company_name}")
#     st.write(f"役職: {card.position}")
#     st.write(f"住所: {card.address}")
#     st.write(f"電話番号: {card.phone_number}")
#     st.markdown("---")




# # グラフを作成
# G = nx.erdos_renyi_graph(10, 0.3)  # 10ノード、各辺が存在する確率0.3のエルデシュ・レーニーグラフ

# # グラフの描画
# plt.figure(figsize=(8, 6))
# nx.draw(G, with_labels=True, node_size=500, node_color='skyblue', font_size=12, font_weight='bold')
# plt.title("Random Graph")

# # Streamlitにグラフを表示
# st.title('グラフ理論の表示例')
# st.pyplot(plt)


# グラフ作成
G = nx.DiGraph()
di = {}

for i, card in enumerate(api.get_all_cards()):
    G.add_node(i, title=f"{card.address}")
    di[card.user_id] = i

for i, contact in enumerate(api.get_all_contacts()):
    try:
        u = di[contact.owner_user_id]
        v = di[contact.user_id]

        G.add_edge(u, v, title=f"{contact.created_at}")
    except:
        pass



# G.add_node(1, title="ノード1の詳細情報")
# G.add_node(2, title="ノード2の詳細情報")
# G.add_node(3, title="ノード3の詳細情報")
# G.add_edge(1, 2, title="aaaa")
# G.add_edge(2, 3)
# G.add_edge(3, 1)

# Pyvisで描画
net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
net.barnes_hut(gravity=-1, central_gravity=0, spring_length=200)  # 必要ならチューニング

net.from_nx(G)
net.show_buttons(filter_=['physics'])  # 物理設定UIも表示される（必要に応じて）

# HTMLファイルとして保存
net.save_graph("graph.html")

# Streamlitに埋め込む
with open("graph.html", "r", encoding="utf-8") as f:
    html_content = f.read()

st.title("インタラクティブなグラフ表示")
components.html(html_content, height=600, scrolling=True)
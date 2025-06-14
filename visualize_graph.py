import json

import matplotlib.pyplot as plt
import networkx as nx

with open("cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

with open("contacts.json", "r", encoding="utf-8") as f:
    contacts = json.load(f)

G = nx.Graph()

# ノード（人物）追加
for card in cards:
    G.add_node(card["user_id"], name=card["full_name"], company=card["company_name"])

# エッジ（名刺交換）追加
for contact in contacts:
    G.add_edge(contact["owner_user_id"], contact["user_id"])

nx.draw(G, with_labels=True)
plt.show()

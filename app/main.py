import requests

import pandas as pd
from pathlib import Path
import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph

# タイトル
st.title("関係ネットワーク")

path = Path(__file__).parent / "dummy_data.csv"
df_dummy = pd.read_csv(path, dtype=str)

url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/"
params = {
    "offset":0,
}

headers = {"content-type": "application/json"}

nodes = []
already = set()
cnt = {}
edges = []

response = requests.get(url, params=params, headers=headers, timeout = (10, 20))
df = pd.DataFrame(response.json())
for user, owner_user in zip(df["user_id"], df["owner_user_id"]):
    if user not in cnt:
        cnt[user] = 1
    else:
        cnt[user] += 1

"""response2 = requests.get(url2, params = params, headers = headers)
df2 = pd.DataFrame(response2.json())
st.dataframe(df2.head())"""

for user, owner_user, dat in zip(df["user_id"], df["owner_user_id"], df["created_at"]):
    if user not in already and cnt[user] >= 10:
        param = {"user_id": user}
        url2 = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + user
        response = requests.get(url2, params=params, headers=headers, timeout=(10, 20))
        name = response.json()[0]["full_name"]
        pos = response.json()[0]["position"]
        nodes.append(Node(id=user, label=name + pos, shape="circle", color="red", size=10))
        already.add(user)
    elif user not in already:
        param = {"user_id": user}
        url2 = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + user
        response = requests.get(url2, params=params, headers=headers, timeout=(10, 20))
        name = response.json()[0]["full_name"]
        nodes.append(Node(id=user, label=name, shape ="circle", size=10))
        already.add(user)
    if owner_user not in already and owner_user in cnt and cnt[owner_user] >= 10:
        param = {"user_id": owner_user}
        url2 = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + owner_user
        response = requests.get(url2, params=params, headers=headers, timeout=(10, 20))
        name = response.json()[0]["full_name"]
        pos = response.json()[0]["position"]
        nodes.append(Node(id=owner_user, label=name + pos, shape="circle", color="red", size=10))
        already.add(owner_user)
    elif owner_user not in already:
        param = {"user_id": owner_user}
        url2 = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + owner_user
        response = requests.get(url2, params=params, headers=headers, timeout=(10, 20))
        name = response.json()[0]["full_name"]
        nodes.append(Node(id=owner_user, label=name, shape="circle", size=10))
        already.add(owner_user)
    edges.append(Edge(source=user, target=owner_user, label=dat[0:5]))
config = Config(
    height=1000,
    directed=False,
    physics=True,
)
# 描画
agraph(nodes, edges, config)

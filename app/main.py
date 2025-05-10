import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# circuitAPI
def get_user_id(offset):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset={offset}&limit=1"
    res = requests.get(url, timeout=(3, 10))
    if res.status_code == 200:
        return res.json()[0]["user_id"]
    st.error("API request failed.")
    return None


def get_similar_top10_user(user_id):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}/similar_top10_users"
    res = requests.get(url, timeout=(3, 10))
    if res.status_code == 200:
        return res.json()
    st.error("API request failed.")
    return None


# user_idを入力
if "user_id_input" not in st.session_state:
    st.session_state.user_id_input = "9230809757"
    user_id = st.session_state.user_id_input
user_id = st.text_input("Enter User ID:", key="user_id_input")


# user_idの候補をランダムに生成
def set_random_user_id():
    rng = np.random.default_rng()
    offset = rng.integers(0, 2000)
    st.session_state.user_id_input = get_user_id(offset)


st.button("Generate Random User ID", on_click=set_random_user_id)


top10_json = get_similar_top10_user(user_id)

# 国土地理院API
GeospatialUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="

lons = []
lats = []
names = []
company_names = []
phone_numbers = []
similarlity_scores = []

for i in range(len(top10_json)):
    res = requests.get(GeospatialUrl + top10_json[i]["address"], timeout=(3, 10))
    # 緯度経度を取得
    lon, lat = res.json()[0]["geometry"]["coordinates"]
    lons.append(lon)
    lats.append(lat)
    names.append(top10_json[i]["full_name"])
    company_names.append(top10_json[i]["company_name"])
    phone_numbers.append(top10_json[i]["phone_number"])
    similarlity_scores.append(top10_json[i]["similarity"])

# Normalize the similarity scores to a range of 0 to 1
min_score = min(similarlity_scores)
max_score = max(similarlity_scores)
normalized_scores = [(score - min_score) / (max_score - min_score) for score in similarlity_scores]
normalized_scores = np.exp(np.array(normalized_scores))  # Apply exponential scaling


similar_user_df = pd.DataFrame(
    {
        "lat": lats,
        "lon": lons,
        "name": names,
        "company_name": company_names,
        "phone_number": phone_numbers,
        "size": normalized_scores,
    }
)

fig = px.scatter_map(
    similar_user_df,
    lat="lat",
    lon="lon",
    hover_data=[
        "name",
        "company_name",
        "phone_number",
    ],
    size="size",
    zoom=4,
    height=700,
    width=1500,
)

fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)

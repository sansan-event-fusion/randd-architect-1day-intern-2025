import requests
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px


# circuitAPI
def get_similar_top10_user(user_id):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}/similar_top10_users"
    res = requests.get(url, timeout=(3, 10))
    if res.status_code == 200:
        return res.json()
    st.error("API request failed.")
    return None


top10_json = get_similar_top10_user("2171722069")

# 国土地理院API
GeospatialUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="

lons = []
lats = []
names = []
company_names = []
phone_numbers = []
similarlity_scores = []
for i in range(len(top10_json)):
    res = requests.get(GeospatialUrl + top10_json[i]["address"])
    # 緯度経度を取得
    lon, lat = res.json()[0]["geometry"]["coordinates"]
    lons.append(lon)
    lats.append(lat)
    names.append(top10_json[i]["full_name"])
    company_names.append(top10_json[i]["company_name"])
    phone_numbers.append(top10_json[i]["phone_number"])
    similarlity_scores.append((top10_json[i]["similarity"]))

size = similarlity_scores
# Normalize the similarity scores to a range of 0 to 1
min_score = min(size)
max_score = max(size)
normalized_scores = [(score - min_score) / (max_score - min_score) for score in size]


df = pd.DataFrame(
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
    df,
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

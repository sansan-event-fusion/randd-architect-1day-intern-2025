import requests
import streamlit as st

# タイトル
API_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/"

user_id = st.number_input("ユーザーIDを入力してください", min_value=0, max_value=10**10, value=0, step=1)

if st.button("検索"):
    cards_url = API_URL + f"cards/{user_id}?offset=0&limit=10"
    r = requests.get(cards_url, timeout=10)
    owner_data = r.json()
    for owner_data_item in owner_data:
        st.write("会社名:" + owner_data_item["company_name"])
        st.write("名前:" + owner_data_item["full_name"])
        st.write("")

    st.write("おすすめの相手")
    cards_recommendation_url = API_URL + f"cards/{user_id}/similar_top10_users"
    r = requests.get(cards_recommendation_url, timeout=10)
    data_recommendation = r.json()
    for data_recommendation_item in data_recommendation:
        st.write("会社名:" + data_recommendation_item["company_name"])
        st.write("名前:" + data_recommendation_item["full_name"])
        st.write("")

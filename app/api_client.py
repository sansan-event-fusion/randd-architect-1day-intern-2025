import pandas as pd
import requests
import streamlit as st

# APIのベースURL
API_BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com"

@st.cache_data(ttl=600) # 10分間キャッシュ
def fetch_api_data(endpoint: str) -> list:
    """汎用的なAPIデータ取得関数"""
    api_url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_similar_users(user_id: str) -> list:
    """類似ユーザーを取得する (キャッシュしない)"""
    try:
        # user_idも文字列として渡すことを保証
        return fetch_api_data(f"/api/cards/{str(user_id)}/similar_top10_users")
    except requests.exceptions.RequestException as e:
        st.warning(f"類似ユーザーの取得に失敗しました: {e}")
        return []

@st.cache_data(ttl=600)
def load_all_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """起動時に必要な全データを取得し、DataFrameに変換する"""
    cards_data = fetch_api_data("/api/cards/")
    contacts_data = fetch_api_data("/api/contacts/")
    
    if not cards_data or not contacts_data:
        return pd.DataFrame(), pd.DataFrame()

    df_cards = pd.DataFrame(cards_data)
    df_contacts = pd.DataFrame(contacts_data)
    
    
    id_cols_cards = ['user_id', 'company_id']
    id_cols_contacts = ['owner_user_id', 'owner_company_id', 'user_id', 'company_id']

    for col in id_cols_cards:
        if col in df_cards.columns:
            df_cards[col] = df_cards[col].astype(str)

    for col in id_cols_contacts:
        if col in df_contacts.columns:
            df_contacts[col] = df_contacts[col].astype(str)

    return df_cards, df_contacts


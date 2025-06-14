import streamlit as st
import pandas as pd
import requests

@st.cache_data
def get_cards() -> pd.DataFrame:
    """
    Fetches the owner cards for a given owner ID.

    Args:
        owner_id (str): The ID of the owner whose cards are to be fetched.

    Returns:
        dict: The JSON response containing the owner cards.
    """
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/'
    headers = {'accept': 'application/json'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching owner cards: {response.status_code} - {response.text}")
    
    return pd.DataFrame(response.json())

@st.cache_data
def get_owner_have_cards(owner_id: str) -> pd.DataFrame:
    """
    Fetches the owner cards for a given owner ID.

    Args:
        owner_id (str): The ID of the owner whose cards are to be fetched.

    Returns:
        dict: The JSON response containing the owner cards.
    """
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{owner_id}'
    headers = {'accept': 'application/json'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching owner cards: {response.status_code} - {response.text}")
    
    df = pd.DataFrame(response.json())

    return df

@st.cache_data
def get_users_info(user_ids: list) -> pd.DataFrame:
    """
    Fetches user information for a list of user IDs.

    Args:
        user_ids (list): List of user IDs to fetch information for.

    Returns:
        pd.DataFrame: DataFrame containing user information.
    """

    users_df = get_cards()
    users_df = users_df[users_df['user_id'].isin(user_ids)]

    return users_df


    

st.title("所持している名刺の検索")

with st.form("search_form"):
    owner_id = st.text_input("オーナーIDを入力してください", "9230809757")
    get_button = st.form_submit_button("検索")
    cancel_button = st.form_submit_button("キャンセル")
    if get_button:
        try:
            owner_have_cards = get_owner_have_cards(owner_id)
            st.success("名刺情報を取得しました。")
            st.dataframe(owner_have_cards)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
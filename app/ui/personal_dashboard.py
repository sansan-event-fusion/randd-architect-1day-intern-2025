import streamlit as st
import pandas as pd
from api_client import get_similar_users
from data_processor import get_personal_connections
from visualizations import personal_network_graph

def show(person_info: pd.Series, df_cards: pd.DataFrame, df_contacts: pd.DataFrame):
    """個人ダッシュボードのUIを表示する"""
    st.header(f"👤 {person_info['full_name']} の分析ダッシュボード")
    
    # --- 1. プロフィール ---
    st.subheader("プロフィール")
    st.table(person_info.to_frame().T[['full_name', 'company_name', 'position']])

    # --- 2. 人脈ネットワーク ---
    st.subheader("ネットワーク")
    connections_df = get_personal_connections(person_info, df_contacts)
    if not connections_df.empty:
        # つながりのある人物の情報をdf_cardsから取得
        connections_info = pd.merge(connections_df, df_cards, on='user_id', how='left').to_dict('records')
        personal_network_graph(person_info.to_dict(), connections_info)
    else:
        st.info("名刺交換履歴はありません。")

    # --- 3. AIリコメンド ---
    st.subheader("リコメンド | 類似ユーザー")
    with st.spinner("類似ユーザーを検索中..."):
        similar_users = get_similar_users(person_info['user_id'])
    
    if similar_users:
        st.dataframe(pd.DataFrame(similar_users)[['full_name', 'company_name', 'position']], hide_index=True)
    else:
        st.info("類似する人物は見つかりませんでした。")


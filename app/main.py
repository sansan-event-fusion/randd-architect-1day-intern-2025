# from pathlib import Path

# import pandas as pd
# import streamlit as st

# # タイトル
# st.title("サンプルアプリ")

# path = Path(__file__).parent / "dummy_data.csv"
# df_dummy = pd.read_csv(path, dtype=str)

# st.dataframe(df_dummy)


import streamlit as st
from api_client import load_all_data
from ui import sidebar, personal_dashboard, corporate_dashboard

# --- ページ設定 ---
st.set_page_config(layout="wide")
st.title("ダッシュボード")

# --- Session Stateの初期化 ---
if 'selected_entity' not in st.session_state:
    st.session_state.selected_entity = None


# --- データ読み込み ---
# st.cache_dataを使ってAPIからのデータ読み込みをキャッシュする
try:
    df_cards, df_contacts = load_all_data()
except Exception as e:
    st.error(f"データの読み込みに失敗しました: {e}")
    st.stop() # データがなければアプリを停止

# --- サイドバー (検索機能) ---
sidebar.show(df_cards)


# --- メインコンテンツの表示 ---
if st.session_state.selected_entity:
    entity_type = st.session_state.selected_entity['type']
    entity_id = st.session_state.selected_entity['id']
    
    if entity_type == 'person':
        # 個人ダッシュボードを表示
        person_info = df_cards[df_cards['user_id'] == entity_id].iloc[0]
        personal_dashboard.show(person_info, df_cards, df_contacts)
        
    elif entity_type == 'company':
        # 企業ダッシュボードを表示
        company_info = df_cards[df_cards['company_id'] == entity_id].iloc[0]
        corporate_dashboard.show(company_info, df_cards, df_contacts)

else:
    st.info("サイドバーから分析したい人物または企業を検索・選択してください。")


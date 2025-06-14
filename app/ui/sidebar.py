import streamlit as st
import pandas as pd

def show(df_cards: pd.DataFrame):
    """サイドバーの検索UIを表示する"""
    st.sidebar.header("検索")

    # 人物リストを作成
    person_options = {f"👤 {row['full_name']} ({row['company_name']})": {'type': 'person', 'id': row['user_id']} 
                      for index, row in df_cards.iterrows()}
    
    # 企業リストを作成（重複排除）
    company_options = {f"🏢 {name}": {'type': 'company', 'id': cid}
                       for cid, name in df_cards[['company_id', 'company_name']].drop_duplicates().set_index('company_id').to_dict()['company_name'].items()}
    
    # 検索オプションを結合
    options = {"": None, **person_options, **company_options}
    
    selection = st.sidebar.selectbox(
        "人物または企業を検索",
        options.keys()
    )
    
    # 選択された内容をSession Stateに保存
    st.session_state.selected_entity = options[selection]


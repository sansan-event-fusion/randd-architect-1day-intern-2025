import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

@st.cache_data
def get_user_cards(user_ids: list) -> pd.DataFrame:
    """
    指定したユーザーIDリストのすべての名刺データを取得します。

    Args:
        user_ids (list): 名刺データを取得するユーザーIDのリスト

    Returns:
        pd.DataFrame: 指定したすべてのユーザーの名刺データを含むデータフレーム
    """
    all_cards = []  # すべての名刺データを格納するリスト
    
    for user_id in user_ids:
        url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}'
        headers = {'accept': 'application/json'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            card_data = response.json()
            # APIのレスポンス形式に応じて処理を分ける
            if isinstance(card_data, list):
                all_cards.extend(card_data)  # リスト形式の場合は拡張
            else:
                all_cards.append(card_data)  # 単一オブジェクトの場合は追加
    
    # すべての名刺データを含むデータフレームを返す
    return pd.DataFrame(all_cards)

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
def get_owner_cards_info(owner_id: str) -> pd.DataFrame:
    """
    Fetches the owner cards for a given owner ID and adds owner's information.

    Args:
        owner_id (str): The ID of the owner whose cards are to be fetched.

    Returns:
        pd.DataFrame: DataFrame containing owner cards with detailed information.
    """
    
    # オーナーの所持している名刺情報を取得
    owner_cards = get_owner_have_cards(owner_id)
    print(len(owner_cards))
    print(owner_cards['owner_user_id'].unique())

    user_ids = owner_cards['user_id'].unique().tolist()
    user_ids.append(owner_cards['owner_user_id'].unique()[0])  # オーナー自身のIDも追加
    cards = get_user_cards(user_ids)

    # デバッグ情報を追加
    print("Cards columns:", cards.columns.tolist())
    
    # 名刺情報とオーナーの所持している名刺情報を結合
    owner_cards_info = pd.merge(owner_cards, cards, on='user_id', how='inner')
    
    # 結合後のカラム名を確認
    print("Merged columns:", owner_cards_info.columns.tolist())
    
    # カラム名の衝突を解決
    if 'company_id_y' in owner_cards_info.columns:
        owner_cards_info = owner_cards_info.drop(["company_id_y"], axis=1)
    if 'company_id_x' in owner_cards_info.columns:
        owner_cards_info = owner_cards_info.rename(columns={'company_id_x': 'company_id'})
    
    # オーナー自身の情報を取得するための準備
    owner_info = cards[cards['user_id'] == owner_cards['owner_user_id'].unique()[0]].copy()
    
    if len(owner_info) > 0:
        # カラム名をリネーム
        owner_info = owner_info.rename(columns={
            'user_id': 'owner_user_id', 
            'full_name': 'owner_full_name', 
            'company_id': 'owner_company_id', 
            'company_name': 'owner_company_name', 
            'position': 'owner_position', 
            'phone_number': 'owner_phone_number', 
            'address': 'owner_address'
        })
        
        # オーナー自身の情報を結合
        owner_cards_info = pd.merge(
            owner_cards_info, 
            owner_info[['owner_user_id', 'owner_full_name', 'owner_company_id', 'owner_company_name', 
                        'owner_position', 'owner_phone_number', 'owner_address']], 
            on='owner_user_id',
            how='left'
        )
    else:
        # オーナー情報が取得できなかった場合、空の値を持つカラムを追加
        owner_cards_info['owner_full_name'] = ''
        owner_cards_info['owner_company_id'] = ''
        owner_cards_info['owner_company_name'] = ''
        owner_cards_info['owner_position'] = ''
        owner_cards_info['owner_phone_number'] = ''
        owner_cards_info['owner_address'] = ''
    
    # 最終的なカラム一覧を表示
    print("Final columns:", owner_cards_info.columns.tolist())
    
    # 存在するカラムのみを選択
    available_columns = owner_cards_info.columns.tolist()
    desired_columns = [
        'owner_user_id', 'owner_full_name', 
        'owner_company_id', 'owner_company_name',
        'owner_position', 'owner_phone_number',
        'owner_address',
        'user_id', 'full_name', 
        'phone_number', 'address', 'position', 
        'company_id', 'company_name', 
        'created_at'
    ]
    
    # 存在するカラムのみを選択
    select_columns = [col for col in desired_columns if col in available_columns]
    
    return owner_cards_info[select_columns]


st.title("所持している名刺の検索")

with st.form("search_form"):
    owner_id = st.text_input("ユーザIDを入力してください", "9230809757")
    get_button = st.form_submit_button("検索")
    cancel_button = st.form_submit_button("キャンセル")
    if get_button:
        owner_have_cards = get_owner_cards_info(owner_id)
        st.success("名刺情報を取得しました。")
        st.write(f"ユーザID: {owner_id} 情報")
        st.write(f"名前: {owner_have_cards['owner_full_name'].unique()[0]}")
        st.write(f"会社名: {owner_have_cards['owner_company_name'].unique()[0]}")
        st.write(f"ポジション: {owner_have_cards['owner_position'].unique()[0]}")
        st.write(f"電話番号: {owner_have_cards['owner_phone_number'].unique()[0]}")
        st.write(f"住所: {owner_have_cards['owner_address'].unique()[0]}")
        st.write(f"交換した名刺の総数: {len(owner_have_cards)}")
        st.write("名刺情報:")
        st.dataframe(owner_have_cards[['user_id', 'full_name', 'phone_number', 'address', 'position', 'company_id', 'company_name', 'created_at']])
        # グラフの描画
        # potionごとの名刺数をカウント
        position_counts = owner_have_cards['position'].value_counts()
        fig = go.Figure(data=[go.Bar(x=position_counts.index, y=position_counts.values)])
        fig.update_layout(title='ポジションごとの名刺数', xaxis_title='ポジション', yaxis_title='名刺数')
        st.plotly_chart(fig)

        # 会社ごとの名刺数をカウント
        company_counts = owner_have_cards['company_name'].value_counts()
        fig_company = go.Figure(data=[go.Bar(x=company_counts.index, y=company_counts.values)])
        fig_company.update_layout(title='会社ごとの名刺数', xaxis_title='会社名', yaxis_title='名刺数')
        st.plotly_chart(fig_company)

        # created_atごとの名刺数をカウント
        owner_have_cards['year'] = pd.to_datetime(owner_have_cards['created_at']).dt.year
        year_counts = owner_have_cards['year'].value_counts().sort_index()

        fig_year = go.Figure(data=[go.Bar(x=year_counts.index.astype(str), y=year_counts.values)])
        fig_year.update_layout(
            title='年別の名刺交換数', 
            xaxis_title='年', 
            yaxis_title='名刺数',
            xaxis=dict(tickmode='linear')  # 軸の目盛りを全て表示
        )
        st.plotly_chart(fig_year)



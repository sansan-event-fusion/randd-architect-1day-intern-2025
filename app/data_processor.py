import pandas as pd

def get_personal_connections(person_info: pd.Series, df_contacts: pd.DataFrame) -> pd.DataFrame:
    """個人の直接的なつながり（名刺交換相手）を取得する"""
    user_id = person_info['user_id']
    given_to = df_contacts[df_contacts['owner_user_id'] == user_id]
    received_from = df_contacts[df_contacts['user_id'] == user_id]
    connected_user_ids = set(given_to['user_id']).union(set(received_from['owner_user_id']))
    connected_user_ids.discard(user_id)
    return pd.DataFrame({'user_id': list(connected_user_ids)})


def analyze_corporate_connections(df_contacts: pd.DataFrame) -> pd.DataFrame:
    """企業間の名刺交換回数を集計する（全体分析用）"""
    df = df_contacts[['owner_company_id', 'company_id']].dropna()
    df = df[df['owner_company_id'] != df['company_id']]
    df['pair'] = df.apply(lambda row: tuple(sorted((row['owner_company_id'], row['company_id']))), axis=1)
    connection_counts = df['pair'].value_counts().reset_index()
    connection_counts.columns = ['pair', 'count']
    return connection_counts

def get_company_top_connections(focus_company_id: str, df_contacts: pd.DataFrame) -> pd.DataFrame:
    """
    【新機能】指定された企業に接続している企業を、名刺交換回数でランク付けして返す
    """
    # focus_company_id を含む交換履歴に絞り込む
    df_focused = df_contacts[
        (df_contacts['owner_company_id'] == focus_company_id) |
        (df_contacts['company_id'] == focus_company_id)
    ].copy()

    # パートナー企業のIDを特定する
    def get_partner_id(row):
        return row['company_id'] if row['owner_company_id'] == focus_company_id else row['owner_company_id']

    df_focused['partner_id'] = df_focused.apply(get_partner_id, axis=1)

    # パートナー企業ごとの交換回数をカウント
    top_connections = df_focused['partner_id'].value_counts().reset_index()
    top_connections.columns = ['partner_id', 'count']
    
    # 自分自身との接続は除外
    top_connections = top_connections[top_connections['partner_id'] != focus_company_id]
    
    return top_connections

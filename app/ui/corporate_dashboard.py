import streamlit as st
import pandas as pd
from data_processor import get_company_top_connections
import visualizations

def show(company_info: pd.Series, df_cards: pd.DataFrame, df_contacts: pd.DataFrame):
    """企業ダッシュボードのUIを表示する（最終改善版）"""
    st.header(f"🏢 {company_info['company_name']} の分析ダッシュボード")
    
    with st.expander("企業情報・登録社員一覧", expanded=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("企業ID", company_info['company_id'])
        with col2:
            st.dataframe(
                df_cards[df_cards['company_id'] == company_info['company_id']][['full_name', 'position']],
                hide_index=True,
                use_container_width=True
            )
    
    st.divider()

    st.subheader(f"🤝 {company_info['company_name']} のトップコネクション")
    

    
    focus_id = company_info['company_id']
    top_connections_df = get_company_top_connections(focus_id, df_contacts)
    
    if top_connections_df.empty:
        st.info("この企業に関する他社との名刺交換履歴は見つかりませんでした。")
        return

    company_map = df_cards[['company_id', 'company_name']].drop_duplicates().set_index('company_id').to_dict()['company_name']
    
    # 接続先が1社のみの場合
    if len(top_connections_df) == 1:
        connection = top_connections_df.iloc[0]
        partner_id = connection['partner_id']
        partner_name = company_map.get(partner_id, f"不明な企業({partner_id})")
        
        st.metric(label="接続先企業", value=partner_name)
        st.metric(label="交換回数", value=f"{connection['count']} 回")
        
        visualizations.focused_corporate_network_graph(
            company_info.to_dict(),
            top_connections_df.to_dict('records'),
            company_map
        )
        
    # 接続先が2社以上の場合
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("##### 表示オプション")
            top_n = st.slider(
                "上位何社との関係を表示しますか？", 1, len(top_connections_df), min(10, len(top_connections_df)), 1)
            
            display_df = top_connections_df.head(top_n).copy()
            
            # --- 改善点：状態列を追加 ---
            display_df['企業名'] = display_df['partner_id'].apply(lambda pid: company_map.get(pid, f"不明({pid})"))
            display_df['状態'] = display_df['partner_id'].apply(lambda pid: "✅" if pid in company_map else "⚠️ 名称不明")

            st.markdown("##### トップコネクションリスト")
            st.dataframe(
                display_df[['企業名', 'count', '状態']],
                column_config={"企業名": "接続先の企業名", "count": "交換回数", "状態": "ステータス"},
                hide_index=True,
                use_container_width=True
            )

        with col2:
            st.markdown("##### コネクションマップ")
            visualizations.focused_corporate_network_graph(
                company_info.to_dict(),
                display_df.to_dict('records'),
                company_map
            )

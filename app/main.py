from pathlib import Path
import requests
import pandas as pd
import streamlit as st
import re

API_BASE_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api"

#APIエンドポイントの設定
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"エラー: {e}")
        return None

with st.form("company_search_form", clear_on_submit=False):
    company_name_input = st.text_input('検索したい社名を入力してください')
    submitted = st.form_submit_button("検索")

    if submitted:
        if company_name_input:
            with st.spinner("名刺データを取得・検索中..."):
                data = fetch_data("/cards/")
            if data:
                df = pd.DataFrame(data)
                try:
                    # 'company_name' カラムでフィルタリング (大文字・小文字を区別せず、部分一致)
                    # 実際のカラム名が異なる場合は、'company_name' の部分を修正してください。
                    filtered_df = df[df['company_name'].str.contains(company_name_input, case=False, na=False)]
                    if not filtered_df.empty:
                        st.write(f"「{company_name_input}」の検索結果:")
                        st.write(f"「{company_name_input}」に完全一致:")
                        st.dataframe(filtered_df)
                        st.write(f"件数: {len(filtered_df)}")
                    else:
                        st.info(f"「{company_name_input}」に該当する名刺データは見つかりませんでした。")
                except KeyError:
                    st.error("エラー: データに 'company_name' カラムが見つかりません。APIから返されるデータ構造を確認してください。")
                except AttributeError: # .str アクセサーが使えない場合 (例: company_name が数値型など)
                    st.error("エラー: 'company_name' カラムが文字列型ではありません。データ型を確認してください。")

            else:
                st.error("名刺データの取得に失敗しました。")
        else:
            st.warning("社名を入力してから検索ボタンを押してください。")


st.markdown("## 名刺データ")
if st.button("名刺データを取得"):
    with st.spinner("取得中..."):
        data = fetch_data("/cards/")

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.write(f"件数: {len(data)}")

# コンタクト履歴データを取得して表示
st.header("コンタクト履歴データ")
if st.button("コンタクト履歴を取得"):
    with st.spinner("取得中..."):
        data = fetch_data("/contacts/")
    
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.write(f"件数: {len(data)}")

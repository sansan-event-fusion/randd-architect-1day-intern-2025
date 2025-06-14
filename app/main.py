import pandas as pd
import streamlit as st
import requests

st.title("名刺交換情報の表示")
url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" # 仮のエンドポイント

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data)

    st.dataframe(df)
except Exception as e:
    st.error(f"データの取得に失敗しました。{e}")

url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/" # 仮のエンドポイント

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    df_contact = pd.DataFrame(data)

    #st.dataframe(df_contact)
except Exception as e:
    st.error(f"データの取得に失敗しました。{e}")

# st.write(df_contact[df_contact["owner_company_id"] == df_contact["company_id"]])

company = st.text_input("会社名を入力してください", "Sansan")
if st.button("送信"):
    st.write(f"{company}の情報です")
    df_company = df[df["company_name"] == company]
    if df_company.empty:
        st.error("該当する会社が見つかりませんでした。")
    else:
        company_id = df_company["company_id"].values[0]
        st.write(df_company)
        df_contact = df_contact[df_contact["owner_company_id"] == company_id]
        # st.write(df_contact)
        user_id = df_company["user_id"].tolist()
        for i in user_id:
            df_contact_each_user = df_contact[df_contact["owner_user_id"] == i]
            # st.write(df_contact_each_user)
            name = df_company[df_company["user_id"] == i]["full_name"].values[0]
            if df_contact_each_user.empty:
                st.write(f"ユーザーID {name} さんの名刺交換情報は見つかりませんでした。")
            else:
                st.write(f"ユーザーID {name} さんの名刺交換会社:")
                contact_user_id = df_contact_each_user["user_id"].tolist()
                for j in contact_user_id:
                    user_for_each = df[df["user_id"] == j]
                    st.write(user_for_each)
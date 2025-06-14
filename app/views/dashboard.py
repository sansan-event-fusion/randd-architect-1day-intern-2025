import os
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

from app.models import Company, CompanyRelation
from app.models.contacts import Contact


def get_transaction_history(company_name):
    """
    指定された企業の取引履歴を取得する
    """
    data_num = 10
    df = pd.DataFrame(
        {
            "企業名": [company_name] * data_num,
            "取引日": [(datetime.now(ZoneInfo("Asia/Tokyo")) - timedelta(days=i)).date() for i in range(data_num)],
            "取引数": [random.randint(1, 100) for _ in range(10)],
        }
    )
    company_df = df[df["企業名"] == company_name].copy()
    company_df = company_df.sort_values("取引日")

    return company_df


def calculate_dependency(contacts_count: int, total_contacts_count: int):
    return round(contacts_count / total_contacts_count * 100, 2)


def get_user_info(user_id: int):
    response = requests.get(f"{os.getenv('BASE_URL')}/api/cards/{user_id}")
    response_json = response.json()
    # レスポンスがリストの場合、最初の要素を使用
    if isinstance(response_json, list) and len(response_json) > 0:
        return response_json[0]
    return response_json


def get_contacts():
    with open("app/data/contacts.csv", "r") as f:
        header = f.readline()
        contacts = [
            Contact(
                owner_user_id=int(line.split(",")[0]),
                owner_company_id=int(line.split(",")[1]),
                user_id=int(line.split(",")[2]),
                company_id=int(line.split(",")[3]),
                created_at=line.split(",")[4],
            )
            for line in f.readlines()
        ]
    return contacts


def get_company_relation(contacts: list[Contact], company_id: int):
    contacts.sort(key=lambda x: x.created_at, reverse=True)
    contacts = [contact for contact in contacts if contact.company_id == company_id]
    cliped_contacts = contacts[:30]

    user_info = {contact.user_id: get_user_info(contact.user_id) for contact in cliped_contacts}
    owner_user_info = {contact.owner_user_id: get_user_info(contact.owner_user_id) for contact in cliped_contacts}
    company_relation = [
        CompanyRelation(
            company_id=contact.company_id,
            user_id=contact.user_id,
            user_name=user_info[contact.user_id].get("full_name", ""),
            user_position=user_info[contact.user_id].get("position", ""),
            owner_user_id=contact.owner_user_id,
            owner_user_name=owner_user_info[contact.owner_user_id].get("full_name", ""),
        )
        for contact in cliped_contacts
    ]
    return company_relation


def dashboard_view(selected_company: Company):
    contacts = get_contacts()
    filtered_contacts = [contact for contact in contacts if contact.company_id == selected_company.id]
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"## 🏢 {selected_company.name}")
        st.write("")
        st.write("")

        st.write("### 企業情報")
        st.table(
            {
                "企業名": f"{selected_company.name} (ID: {selected_company.id})",
                "住所": selected_company.address,
                "電話番号": selected_company.phone,
            }
        )
    with col2:
        st.write(f"### 繋がりの強さ: {calculate_dependency(len(filtered_contacts), len(contacts))}%")
        st.write("繋がりの強さは、自社全体の取引に占める、対象企業の取引の割合です。")

        st.write("### 直近の取引履歴")
        # 取引履歴データの取得
        transaction_history = get_transaction_history(selected_company.name)

        if not transaction_history.empty:
            st.line_chart(
                transaction_history.set_index("取引日")["取引数"],
                x_label="取引日",
                y_label="取引数",
            )
        else:
            st.info("直近の取引履歴がありません")

    company_relation = get_company_relation(contacts, selected_company.id)
    st.write("## 企業とのつながり")
    st.table(
        {
            "取引先担当者名": [relation.user_name for relation in company_relation],
            "役職": [relation.user_position for relation in company_relation],
            "自社担当者名": [relation.owner_user_name for relation in company_relation],
        }
    )

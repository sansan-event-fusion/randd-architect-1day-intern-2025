import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from app.models import Company


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


def calculate_dependency():
    return 0.5


def dashboard_view(selected_company: Company):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"## 🏢 {selected_company.name}")
        st.write("")
        st.write("")

        st.write("### 企業情報")
        st.table({"住所": selected_company.address, "電話番号": selected_company.phone})
    with col2:
        st.write(f"### 繋がりの強さ: {calculate_dependency()}")
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

    st.write("## 企業とのつながり")
    st.table(
        {
            "人名": ["山田太郎", "山田花子"],
            "役職": ["社長", "社長"],
            "関係": ["AAさん", "BBさん"],
            "取引日": ["2025-01-01", "2025-01-02"],
        }
    )

import pandas as pd
import requests
import streamlit as st

API_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/"


def plot_contact_history_by_date(data):
    created_at_list = [item["created_at"] for item in data if "created_at" in item]
    df_created_at_list = pd.DataFrame({"created_at": pd.to_datetime(created_at_list)})

    df_created_at_list["week_start"] = df_created_at_list["created_at"].dt.to_period("W").apply(lambda r: r.start_time)

    df_count = df_created_at_list.groupby("week_start").size().reset_index(name="交換回数")
    df_count["week_start"] = pd.to_datetime(df_count["week_start"])

    # グラフ表示
    st.bar_chart(data=df_count.set_index("week_start"))


def plot_contact_history_by_time(data):
    created_at_list = [item["created_at"] for item in data if "created_at" in item]
    df_created_at_list = pd.DataFrame({"created_at": pd.to_datetime(created_at_list)})
    df_created_at_list["created_at"] = df_created_at_list["created_at"].dt.tz_convert("Asia/Tokyo")

    # 時刻(hour単位)を抽出
    df_created_at_list["hour"] = df_created_at_list["created_at"].dt.hour

    # 時間ごとの交換回数を集計
    df_count = df_created_at_list.groupby("hour").size().reset_index(name="交換回数")

    df_count["時刻"] = df_count["hour"].apply(lambda x: f"{x:02d}:00")
    df_count = df_count.sort_values("hour")

    # グラフ表示
    st.bar_chart(data=df_count.set_index("時刻")["交換回数"])


# 一番交換回数が多い時間帯を取得
def get_max_contact_time(data):
    created_at_list = [item["created_at"] for item in data if "created_at" in item]
    df_created_at_list = pd.DataFrame({"created_at": pd.to_datetime(created_at_list)})
    df_created_at_list["created_at"] = df_created_at_list["created_at"].dt.tz_convert("Asia/Tokyo")

    # 時刻(hour単位)を抽出
    df_created_at_list["hour"] = df_created_at_list["created_at"].dt.hour

    # 時間ごとの交換回数を集計
    df_count = df_created_at_list.groupby("hour").size().reset_index(name="交換回数")

    max_row = df_count.loc[df_count["交換回数"].idxmax()]
    return max_row


def get_contact_histories_by_user_id(user_id):
    cards_owner_url = API_URL + f"contacts/owner_users/{user_id}"
    r = requests.get(cards_owner_url, timeout=10)
    data = r.json()
    return data


def get_cards_info(user_id):
    cards_url = API_URL + f"cards/{user_id}"
    r = requests.get(cards_url, timeout=10)
    data = r.json()
    return data


def get_contact_histories_count(user_id):
    cards_owner_count_url = API_URL + f"contacts/owner_users/{user_id}/count"
    r = requests.get(cards_owner_count_url, timeout=10)
    data_owner_count = r.json()
    return data_owner_count


def get_recommendation_users(user_id):
    cards_recommendation_url = API_URL + f"cards/{user_id}/similar_top10_users"
    r = requests.get(cards_recommendation_url, timeout=10)
    data_recommendation = r.json()
    return data_recommendation


def get_owner_companies_by_company_id(company_id):
    cards_company_url = API_URL + f"contacts/owner_companies/{company_id}"
    r = requests.get(cards_company_url, timeout=10)
    data_company = r.json()
    return data_company

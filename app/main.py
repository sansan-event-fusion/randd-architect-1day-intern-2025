from pathlib import Path
import pandas as pd
import streamlit as st
from collections import Counter
import requests
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import calendar
import re
import matplotlib_fontja

st.title("名刺情報の概要")

# １ヶ月ごとの日付を生成する函数
def weekly_date_range(start_date, end_date):
    current = start_date
    result = []
    while current <= end_date:
        result.append(current)
        current += timedelta(weeks=1)
    return result

def monthly_date_range(start_date, end_date):
    current = start_date
    result = []
    while current <= end_date:
        result.append(current)
        # 翌月の同じ日を計算
        year = current.year + (current.month // 12)
        month = current.month % 12 + 1
        day = min(current.day, calendar.monthrange(year, month)[1])  # 翌月にその日が存在するかチェック
        current = date(year, month, day)
    return result

# 名刺一覧の獲得
def get_cards(offset=0, limit=2000):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset={offset}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("APIの取得に失敗しました。")
        return []
    return response.json()

def get_one_card(card_id):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{card_id}/"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("存在しない名刺IDです。")
        return {}
    return response.json()

def get_contacts_count(start_date, end_date):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/count?start_date={start_date}&end_date={end_date}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("APIの取得に失敗しました。")
        return 0
    return response.json()
# get_contacts_countの結果を週ごとに集計してグラフ化
def plot_contacts_count_graph_by_week(start_date, end_date):
    week_list = weekly_date_range(start_date, end_date)
    contacts_count_list = []
    for i in range(len(week_list) - 1):
        start = week_list[i].strftime("%Y-%m-%d")
        end = week_list[i + 1].strftime("%Y-%m-%d")
        count = get_contacts_count(start, end)
        contacts_count_list.append(count)
    result = pd.DataFrame({
        "週": [f"{week_list[i].strftime('%Y-%m-%d')} - {week_list[i + 1].strftime('%Y-%m-%d')}" 
              for i in range(len(week_list) - 1)],
        "名刺交換数": contacts_count_list
    })
    fig, ax = plt.subplots()
    ax.plot(result["週"], result["名刺交換数"], marker="o")
    ax.set_title("週ごとの名刺交換数")
    ax.set_xlabel("週")
    ax.set_ylabel("名刺交換数")
    st.pyplot(fig)

def plot_contacts_count_graph_by_month(start_date, end_date):
    month_list = monthly_date_range(start_date, end_date)
    contacts_count_list = []

    for i in range(len(month_list) - 1):
        start = month_list[i].strftime("%Y-%m-%d")
        end = month_list[i + 1].strftime("%Y-%m-%d")
        count = get_contacts_count(start, end)
        contacts_count_list.append(count)

    result = pd.DataFrame({
        "月": [f"{month_list[i].strftime('%Y-%m-%d')} - {month_list[i + 1].strftime('%Y-%m-%d')}" 
                for i in range(len(month_list) - 1)],
        "名刺交換数": contacts_count_list
    })

    fig, ax = plt.subplots()
    ax.plot(result["月"], result["名刺交換数"], marker='o')
    ax.set_title("The number of contacts by month")
    ax.set_xlabel("month")
    ax.set_ylabel("contacts count")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    
def get_similar_top10_users(user_id):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}/similar_top10_users"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Not found user ID.")
        return []
    return response.json()

def get_contacts_data_len():
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/count"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("APIの取得に失敗しました。")
        return 0
    return response.json()

def get_contacts_data(offset=0, limit=99439):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/?offset={offset}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("APIの取得に失敗しました。")
        return []
    return response.json()

def extract_prefecture(address):
    # 都道府県の正規表現パターン（都・道・府・県で終わる最初の部分を抽出）
    match = re.match(r'^(.+?[都道府県])', address)
    if match:
        return match.group(1)
    else:
        return None
    
###### メイン部分 #######
cards_list = get_cards()
company_id2name = {}
company_id2address = {}
for card in cards_list:
    if card["company_id"] not in company_id2name:
        company_id2name[card["company_id"]] = card["company_name"]
    if card["company_id"] not in company_id2address:
        company_id2address[card["company_id"]] = card["address"]

cards_df = pd.DataFrame(cards_list)
st.dataframe(cards_df)

# 会社ごとの出現順位
company_name_count = Counter(cards_df["company_name"])
company_name_count_df = pd.DataFrame(company_name_count.items(), columns=["会社名", "回数"])
company_name_count_df = company_name_count_df.sort_values(by="回数", ascending=False).reset_index(drop=True)
st.write("会社ごとの出現数のランキング")
with st.form(key='rank_setting_form'):
    min_num = st.number_input("出現回数の最小値", min_value=0, max_value=2000, step=1)
    max_num = st.number_input("出現回数の最大値", min_value=0, max_value=2000, step=1)
    submitted_ranking = st.form_submit_button("送信")
    
if submitted_ranking:
    company_name_count_df = company_name_count_df[(company_name_count_df["回数"] >= min_num) & (company_name_count_df["回数"] <= max_num)].reset_index(drop=True)
    st.write(f"出現回数が{min_num}以上、{max_num}以下の会社名のランキング")
    st.dataframe(company_name_count_df)

st.write("時期ごとの名刺交換の傾向")
with st.form(key='trending_setting_form'):
    start_date = st.date_input("時期の始まり")
    end_date = st.date_input("時期の終わり")
    submitted_trending = st.form_submit_button("送信")
if submitted_trending:
    if start_date > end_date:
        st.error("開始日が終了日より後になっています。")
    else:
        contacts_count = get_contacts_count(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        st.write(f"{start_date}から{end_date}までの名刺交換数: {contacts_count}")
        plot_contacts_count_graph_by_month(start_date, end_date)

st.write("県ごとのつながり（500件以上のものは500とする）")
contacts_data = get_contacts_data(offset=0, limit=get_contacts_data_len())
if contacts_data:
    contacts_df = pd.DataFrame(contacts_data)
    owner_prefecture_list = []
    prefecture_list = []
    for idx, row in contacts_df.iterrows():
        owner_prefecture_list.append(extract_prefecture(company_id2address[row["owner_company_id"]]))
        prefecture_list.append(extract_prefecture(company_id2address[row["company_id"]]))
    count_df = pd.DataFrame({
        "owner_prefecture": owner_prefecture_list,
        "prefecture": prefecture_list
    })
    
    pivot = count_df.groupby(["owner_prefecture","prefecture"]).size().unstack(fill_value=0)
    pivot.clip(upper=500, inplace=True)  # 上限を500に設定
    # --- 3. matplotlib でヒートマップを描画 ---
    fig, ax = plt.subplots()
    im = ax.imshow(pivot.values, aspect="auto",cmap='Blues')

    # 軸ラベルの設定
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right",fontsize=5)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index,fontsize=5)
    fig.colorbar(im, ax=ax, label="交換回数")
    st.pyplot(fig)
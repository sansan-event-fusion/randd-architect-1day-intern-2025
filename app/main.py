import pandas as pd
import streamlit as st
import requests
from datetime import datetime


# タイトル
st.title("他企業との接点調査")

# owner_company_id = 9266414469  # 自社


owner_company_id = st.number_input("自社のcompany_idを入力してください", step=1)
st.write(f"owner_company_id: {owner_company_id}")

response = requests.get(
    f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/{owner_company_id}",
    # params={"offset": 0, "limit": 500},
    headers={"accept": "application/json"},
)

json_data = response.json()

# レスポンスからcompany_idの出現回数をカウント
st.write("各企業との名刺交換回数（上位10社）")
company_counts = {}
for data in json_data:
    company_id = data.get("company_id")
    if company_id:
        company_counts[company_id] = company_counts.get(company_id, 0) + 1

# 出現回数でソート
sorted_counts = dict(sorted(company_counts.items(), key=lambda x: x[1], reverse=True))

# 結果を表示
# for company_id, count in sorted_counts.items():
#     st.write(f"company_id: {company_id} - 出現回数: {count}")

# グラフで可視化（トップ10）
df = pd.DataFrame(sorted_counts.items(), columns=["company_id", "count"])
df_top10 = df.head(10)  # 上位10件のみを抽出
st.write(df_top10)
st.bar_chart(df_top10, x="company_id", y="count")


target_company_id = st.number_input("取引先のcompany_idを入力してください", step=1)

if target_company_id == 0:
    pass
else:
    st.write(f"target_company_id: {target_company_id}")
    # target_company_idのデータのみを抽出
    target_company_data = [
        data for data in json_data if data.get("company_id") == str(target_company_id)
    ]

    # 企業名を取得
    target_company_user_id = target_company_data[0].get("user_id")
    response_company_name = requests.get(
        f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{target_company_user_id}",
        headers={"accept": "application/json"},
    )
    company_name_json_data = response_company_name.json()
    target_company_name = company_name_json_data[0].get("company_name")
    st.write(f"target_company_name: {target_company_name}")

    # owner_user_idの出現回数をカウント
    st.write(f"各社員の{target_company_name}との名刺交換回数（上位10名）")
    owner_user_counts = {}
    owner_user_received_ids = {}
    for data in target_company_data:
        owner_user_id = data.get("owner_user_id")
        if owner_user_id:
            owner_user_counts[owner_user_id] = (
                owner_user_counts.get(owner_user_id, 0) + 1
            )
            if owner_user_id not in owner_user_received_ids.keys():
                owner_user_received_ids[owner_user_id] = []
            owner_user_received_ids[owner_user_id].append(data.get("user_id"))
    # 出現回数でソート
    sorted_counts = dict(
        sorted(owner_user_counts.items(), key=lambda x: x[1], reverse=True)
    )

    # 結果を表示
    # for owner_user_id, count in sorted_counts.items():
    #     st.write(f"owner_user_id: {owner_user_id} - 出現回数: {count}")

    # グラフで可視化
    df = pd.DataFrame(sorted_counts.items(), columns=["owner_user_id", "count"])
    st.bar_chart(df, x="owner_user_id", y="count")

    # 最近名刺交換した人を表示
    st.write("最近名刺交換した人（上位10名）")
    owner_user_dates = {}
    for data in target_company_data:
        owner_user_id = data.get("owner_user_id")
        if owner_user_id:
            owner_user_dates[owner_user_id] = data.get("created_at")

    # 交換日時でソート
    sorted_counts = dict(
        sorted(
            owner_user_dates.items(),
            key=lambda x: datetime.fromisoformat(x[1].replace("Z", "+00:00")),
            reverse=True,
        )
    )

    # 結果を表示
    for owner_user_id, date in list(sorted_counts.items())[:10]:
        st.write(f"owner_user_id: {owner_user_id} - 名刺交換日: {date[:10]}")


# 名刺交換の詳細
user_id = st.number_input(f"名刺交換の詳細を表示するuser_idを入力してください", step=1)

response_user_detail = requests.get(
    f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}",
    headers={"accept": "application/json"},
)
if user_id == 0:
    pass
else:
    st.write("user_id: ", str(user_id))
    if response_user_detail.status_code == 200:
        user_detail_json_data = response_user_detail.json()[0]
        st.write(f"---名前：{user_detail_json_data.get('full_name')}")
        st.write(f"---役職：{user_detail_json_data.get('position')}")
        st.write(f"---電話番号：{user_detail_json_data.get('phone_number')}")
        received_user_ids = owner_user_received_ids[str(user_id)]
        for i, received_user_id in enumerate(received_user_ids):
            st.write(f"名刺交換した人({i+1})：{received_user_id}")
            response_received_user_detail = requests.get(
                f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{received_user_id}",
                headers={"accept": "application/json"},
            )
            if response_received_user_detail.status_code == 200:
                received_user_detail_json_data = response_received_user_detail.json()[0]
                st.write(
                    f"---会社名：{received_user_detail_json_data.get('company_name')}"
                )
                st.write(f"---名前：{received_user_detail_json_data.get('full_name')}")
                st.write(f"---役職：{received_user_detail_json_data.get('position')}")
                st.write(
                    f"---電話番号：{received_user_detail_json_data.get('phone_number')}"
                )
            else:
                st.write("データがありません")
    else:
        st.write("データがありません")


# # チーム編成
# # id_1 = 18527820
# # id_2 = 230390267
# num_members = st.number_input(
#     "チームの中心メンバーの人数を入力してください", min_value=1, max_value=10, step=1
# )
# user_ids = []

# for i in range(num_members):
#     user_id = st.number_input(
#         f"チームの中心メンバー{i+1}のuser_idを入力してください", step=1
#     )
#     user_ids.append(user_id)
# st.write("中心メンバーのuser_id:")
# for i, user_id in enumerate(user_ids, 1):
#     st.write(f"メンバー{i}: {user_id}")

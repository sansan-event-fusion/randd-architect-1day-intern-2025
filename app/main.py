import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import requests
import plotly.express as px


# タイトル
st.title("新規事業開時に助けになりそうな人")

#path = Path(__file__).parent / "dummy_data.csv"
#df_dummy = pd.read_csv(path, dtype=str)

#url = 'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count'
#response = requests.get(url)
#print(response.json())

#response = requests.post(url, json={"key": "value"})
def get_data():
    url = 'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/'
    params = {
        "offset": 0,
        "limit": 100
    }
    headers = {
    "accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)
    return response.json()


# API: 個人の名刺データ取得
def show_user_data(user_id):
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}'
    headers = {
        "accept": "application/json"
    }
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        return None


#show_card_data(show_user_data(18527820))
#こんな感じで使う
#IDに対してその人のデータを表示させるもの
def show_card_data(user_data):
    st.text("ユーザー名: " + user_data[0]['full_name'])
    st.text("役職: " + user_data[0]['position'])
    st.text("会社名: " + user_data[0]['company_name'])
    st.text("住所: " + str(user_data[0]['address']))
    st.text("電話番号: " + str(user_data[0]['phone_number']))
    


#100件分、期間で全ての情報を取得する件数
def get_contacts_data():
    url = 'https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/'
    params = {
        "offset": 0,
        "limit": 10000,
        "start_date": "2023-01-01",
        "end_date": "2024-01-01"
    }
    headers = {
        "accept": "application/json"
    }
    response = requests.get(url, headers=headers, params=params, timeout=10)
    return response.json()






# Streamlit表示
data = get_contacts_data()
df = pd.DataFrame(data)
st.dataframe(df)

ranking = df['user_id'].value_counts().reset_index()
ranking.columns = ['user_id', 'count']

st.subheader("Ranking")
st.write("ユーザーIDのランキング")
st.dataframe(ranking)

# 上位10人だけに絞る
top10 = ranking.head(15)
assert len(top10) == 15, "Top 10のデータが取得できていません。"

# Plotly グラフ表示
fig = px.bar(top10,
             x='user_id',
             y='count',
             title='Top 10 名刺を渡した人',
             labels={'user_id': 'User ID', 'count': '渡した枚数'},
             text='count')
fig.update_traces(textposition='outside')
fig.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig)

top1 = top10.iloc[0]['user_id']




st.write("意欲的に交流を行っているユーザー Top 10")

for i in range(11):
    user_id = top10.iloc[i]['user_id']
    user_data = show_user_data(user_id)
    st.write(f"{i+1}人目")
    if user_data:
        show_card_data(user_data)
    else:
        st.warning(f"{i+1}人目（user_id: {user_id}）のデータ取得に失敗しました。")





#output = show_user_data(top1['user_id'])
#output[0]['full_name']
#output[0]['position']

#print(output[0]['full_name'])
#print(output[0]['position'])

#st.text("ユーザー名: " + output[0]['full_name'])



#show_card_data(show_user_data(18527820))




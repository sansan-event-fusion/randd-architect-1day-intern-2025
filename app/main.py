from datetime import date, timedelta

import altair as alt
import pandas as pd
import requests
import streamlit as st

# タイトル
st.title("名刺データ")

url = "https://circuit-trial.stg.rd.ds.sansan.com/api/"

# GETリクエスト
response = requests.get(url + "cards/?offset=0&limit=100", timeout=10)

# JSONレスポンスを辞書として取得
res_json = response.json()

# DataFrameに変換（空なら空のテーブル）
df = pd.DataFrame(res_json)

# 表示
st.dataframe(df)

# タイトル
st.title("名刺交換数の推移（指定期間）")

# 日付入力
start_date = st.date_input("開始日", date.today() - timedelta(days=7))
end_date = st.date_input("終了日", date.today())

if start_date > end_date:
    st.error("開始日は終了日より前にしてください。")
else:
    base_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/"
    params: dict[str, str | int] = {
        "offset": 0,
        "limit": 1000,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    # API呼び出し
    response = requests.get(base_url, params=params, timeout=100)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        if df.empty or "created_at" not in df.columns:
            st.warning("データが見つかりませんでした。")
        else:
            # created_at から日付を抽出
            df["exchange_date"] = pd.to_datetime(df["created_at"]).dt.date

            # 日別に集計
            count_by_date = df.groupby("exchange_date").size().reset_index(name="count")

            # Altair で棒グラフを作成
            chart = (
                alt.Chart(count_by_date)
                .mark_bar()
                .encode(
                    x=alt.X("exchange_date:T", title="交換日"),
                    y=alt.Y("count:Q", title="名刺交換数"),
                    tooltip=["exchange_date:T", "count:Q"],
                )
                .properties(
                    width=600,
                    height=400,
                    title="日別の名刺交換件数",
                )
            )

            st.altair_chart(chart, use_container_width=True)
    else:
        st.error(f"API取得に失敗しました（ステータスコード: {response.status_code}）")

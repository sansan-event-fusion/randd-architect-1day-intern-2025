import asyncio
from collections import defaultdict

import httpx
import pandas as pd
import plotly.express as px
import streamlit as st

# タイトル
st.title("おすすめの訪問先")

# テキストボックス
owner_user_id = st.text_input("user_idを使用して訪問先を探す")


async def fetch_json(client: httpx.AsyncClient, url: str):
    try:
        resp = await client.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


async def main(user_id: str):
    base_url = "https://circuit-trial.stg.rd.ds.sansan.com/api"

    async with httpx.AsyncClient() as client:
        # 類似ユーザーの取得
        similar_user_url = f"{base_url}/cards/{user_id}/similar_top10_users"
        similar_user_results = await fetch_json(client, similar_user_url)

        # 自分が訪問済みの会社を取得
        user_url = f"{base_url}/contacts/owner_users/{user_id}?offset=0&limit=100"
        user_results = await fetch_json(client, user_url)
        already_visited = {r["company_id"] for r in user_results}

        # プログレスバー
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 類似ユーザーの会社訪問履歴を並列取得
        tasks = []
        for similar_user in similar_user_results:
            suid = similar_user["user_id"]
            url = f"{base_url}/contacts/owner_users/{suid}?offset=0&limit=100"
            tasks.append(fetch_json(client, url))
        results_list = await asyncio.gather(*tasks)

        # 推薦候補の集計
        recommended: defaultdict[str, dict] = defaultdict(dict)
        for i, results in enumerate(results_list):
            status_text.text(f"{i + 1} / {len(results_list)} 完了")
            progress_bar.progress((i + 1) * 100 // len(results_list))
            for r in results:
                cid = r["company_id"]
                uid = r["user_id"]
                if cid not in recommended and cid not in already_visited:
                    recommended[cid] = {"user_id": uid, "cnt": 1}
                elif cid in recommended:
                    recommended[cid]["cnt"] += 1

        # 会社名の取得も並列処理
        card_tasks = []
        for data in recommended.values():
            uid = data["user_id"]
            card_url = f"{base_url}/cards/{uid}"
            card_tasks.append(fetch_json(client, card_url))
        card_results = await asyncio.gather(*card_tasks)

        # 名前の埋め込み
        for data, card in zip(recommended.values(), card_results, strict=False):
            if card and isinstance(card, list):
                data["company_name"] = card[0].get("company_name", "Unknown")
            else:
                data["company_name"] = "Unknown"

        st.write("おすすめの会社は以下の通りです。")
        # グラフ表示
        sorted_recommended = sorted(recommended.values(), key=lambda x: x["cnt"], reverse=True)
        result_df = pd.DataFrame(sorted_recommended, columns=["company_id", "company_name", "cnt"])
        result_df = result_df.rename(columns={"company_name": "会社名", "cnt": "おすすめ度"})
        result_df = result_df[result_df["会社名"] != "Unknown"]
        st.dataframe(result_df.head(10)[["会社名", "おすすめ度"]])

        # グラフ表示
        fig = px.bar(
            result_df.head(30),
            x="会社名",
            y="おすすめ度",
            labels={"x": "会社名", "y": "おすすめ度"},
            title="結果の詳細",
        )
        st.plotly_chart(fig)


# ボタン処理
if st.button("実行"):
    if owner_user_id:
        asyncio.run(main(owner_user_id))
    else:
        st.warning("user_idを入力してください。")

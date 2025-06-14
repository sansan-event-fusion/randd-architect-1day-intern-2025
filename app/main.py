# from pathlib import Path

# import pandas as pd
# import streamlit as st

# # タイトル
# st.title("サンプルアプリ")

# path = Path(__file__).parent / "dummy_data.csv"
# df_dummy = pd.read_csv(path, dtype=str)

# st.dataframe(df_dummy)









# import requests
# import pandas as pd

# url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
# params = {
#     "offset": 0,
#     "limit": 10000
# }
# headers = {
#     "accept": "application/json"
# }

# response = requests.get(url, params=params, headers=headers)

# data = response.json()


# import streamlit as st
# import matplotlib.pyplot as plt
# import pandas as pd
# import requests
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans
# from sklearn.decomposition import PCA

# # APIから名刺データ取得
# url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
# params = {"offset": 0, "limit": 100}
# headers = {"accept": "application/json"}
# response = requests.get(url, params=params, headers=headers)
# data = response.json()

# # DataFrameへ変換
# df = pd.DataFrame(data)
# df['text'] = df['company_name'] + ' ' + df['position']

# # TF-IDFベクトル化
# vectorizer = TfidfVectorizer(max_features=1000)
# X = vectorizer.fit_transform(df['text'])

# # クラスタリング
# n_clusters = st.sidebar.slider("クラスタ数", min_value=2, max_value=10, value=5)
# kmeans = KMeans(n_clusters=n_clusters, random_state=42)
# df['cluster'] = kmeans.fit_predict(X)

# # 次元削減（PCAで2次元）
# pca = PCA(n_components=2)
# X_pca = pca.fit_transform(X.toarray())
# df['x'], df['y'] = X_pca[:, 0], X_pca[:, 1]

# # プロット描画
# fig, ax = plt.subplots(figsize=(10, 7))
# for i in range(n_clusters):
#     cluster_df = df[df['cluster'] == i]
#     ax.scatter(cluster_df['x'], cluster_df['y'], label=f'Cluster {i}', alpha=0.6)
# ax.set_title("Type of Industry Clustering")
# ax.legend()

# # Streamlitに表示
# st.pyplot(fig)

# # オプション: データ表示
# if st.checkbox("クラスタ付データを表示"):
#     st.dataframe(df[['full_name', 'company_name', 'position', 'cluster']])






# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import pandas as pd
# import requests
# import streamlit as st
# from sklearn.cluster import KMeans
# from sklearn.feature_extraction.text import TfidfVectorizer

# # 日本語フォント設定
# mpl.rcParams["font.family"]        = "sans-serif"
# mpl.rcParams["font.sans-serif"]   = ["IPAPGothic","Meiryo","Yu Gothic","TakaoPGothic"]
# mpl.rcParams["axes.unicode_minus"] = False

# # API取得
# API_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
# HEADERS = {"accept":"application/json"}
# resp = requests.get(API_URL, params={"offset":0,"limit":10000}, headers=HEADERS)
# df   = pd.DataFrame(resp.json())

# # 会社名前処理
# df["clean_name"] = (
#     df["company_name"]
#       .str.replace(r"(株式会社|有限会社|合同会社|（.*?）)", "", regex=True)
#       .str.strip()
# )

# # ベクトル化とクラスタリング
# vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,6), max_features=2000)
# X          = vectorizer.fit_transform(df["clean_name"])
# n_clusters = st.sidebar.slider("クラスタ数（業種数）", 2, 10, 5)
# kmeans     = KMeans(n_clusters=n_clusters, random_state=42).fit(X)
# df["cluster"] = kmeans.labels_

# # クラスタ名生成
# terms  = vectorizer.get_feature_names_out()
# order  = kmeans.cluster_centers_.argsort()[:, ::-1]
# cluster_names = ["／".join(terms[order[i,:5]]) for i in range(n_clusters)]

# # UI: 業種→会社選択 → 可視化
# sel_ind       = st.sidebar.selectbox("業種を選択", cluster_names)
# sel_cluster   = cluster_names.index(sel_ind)
# candidates    = df[df["cluster"]==sel_cluster]["company_name"].unique()
# sel_company   = st.sidebar.selectbox("会社を選択", candidates)

# # 選択会社の company_id を取得
# sel_company_id = df[df['company_name'] == sel_company]['company_id'].iloc[0]

# # API でその会社の「取引先カード」を取得
# resp2 = requests.get(
#     API_URL,
#     params={"offset": 0, "limit": 10000, "company_id": sel_company_id},
#     headers=HEADERS
# )
# partner_df = pd.DataFrame(resp2.json())

# # 取得先にクラスタ予測を割り当て
# X2 = vectorizer.transform(partner_df['company_name'])
# partner_df['cluster'] = kmeans.predict(X2)

# # クラスタ（業種）ごとに取引件数を集計
# trade_cnt = (
#     partner_df.groupby("cluster")
#     .size()
#     .reset_index(name='count')
# )
# trade_cnt['industry'] = trade_cnt['cluster'].map(lambda i: cluster_names[i])

# # 可視化
# st.write(f"### {sel_company} の取引業種分布")
# fig, ax = plt.subplots(figsize=(8,5))
# ax.bar(trade_cnt["industry"], trade_cnt["count"])
# ax.set_ylabel("取引件数（カード交換数）")
# ax.set_xticklabels(trade_cnt["industry"], rotation=45, ha="right")
# st.pyplot(fig)

# # 元データプレビュー
# if st.checkbox("クラスタ結果を表示"):
#     st.dataframe(df[["company_name","cluster"]])




import streamlit as st
import pandas as pd
import requests
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# — 日本語フォント設定 —
mpl.rcParams["font.family"]       = "sans-serif"
mpl.rcParams["font.sans-serif"]   = ["IPAPGothic","Meiryo","Yu Gothic","TakaoPGothic"]
mpl.rcParams["axes.unicode_minus"] = False

API_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
HEADERS = {"accept": "application/json"}

@st.cache_data
def fetch_cards(company_id=None, offset=0, limit=10000):
    params = {"offset": offset, "limit": limit}
    if company_id is not None:
        params["company_id"] = company_id
    resp = requests.get(API_URL, params=params, headers=HEADERS)
    resp.raise_for_status()
    return pd.DataFrame(resp.json())

@st.cache_data
def build_clusters(df, n_clusters):
    df = df.copy()
    df["clean_name"] = (
        df["company_name"]
          .str.replace(r"(株式会社|有限会社|合同会社|（.*?）)", "", regex=True)
          .str.strip()
    )
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,6), max_features=2000)
    X = vectorizer.fit_transform(df["clean_name"])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(X)
    df["cluster"] = kmeans.labels_
    terms = vectorizer.get_feature_names_out()
    order = kmeans.cluster_centers_.argsort()[:, ::-1]
    cluster_names = ["／".join(terms[idx][:5]) for idx in order]
    return df, vectorizer, kmeans, cluster_names

def main():
    st.title("取引先業種分布分析")

    # 全カード取得＆クラスタリング
    df_all = fetch_cards()
    n_clusters = st.sidebar.slider("クラスタ数（業種数）", 2, 10, 5)
    df_clustered, vectorizer, kmeans, cluster_names = build_clusters(df_all, n_clusters)

    # 業種選択
    sel_ind = st.sidebar.selectbox("業種を選択", cluster_names)
    sel_idx = cluster_names.index(sel_ind)
    sel_ids = df_clustered[df_clustered["cluster"] == sel_idx]["company_id"].unique()
    st.write(f"**選択した業種（{sel_ind}）に属する会社数：** {len(sel_ids)}")

    # 選択業種の各社取引先を取得→クラスタ予測→集計
    partners = []
    for cid in sel_ids:
        df_p = fetch_cards(company_id=cid)
        if not df_p.empty:
            partners.append(df_p)
    if partners:
        df_part = pd.concat(partners, ignore_index=True)
        df_part["clean_name"] = (
            df_part["company_name"]
              .str.replace(r"(株式会社|有限会社|合同会社|（.*?）)", "", regex=True)
              .str.strip()
        )
        X2 = vectorizer.transform(df_part["clean_name"])
        df_part["cluster"] = kmeans.predict(X2)
        trade_cnt = (
            df_part.groupby("cluster")
            .size()
            .reset_index(name="count")
        )
        trade_cnt["industry"] = trade_cnt["cluster"].map(lambda i: cluster_names[i])

        # 図の生成
        st.write(f"### {sel_ind} 業種の取引件数分布")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(trade_cnt["industry"], trade_cnt["count"])
        ax.set_ylabel("取引件数（カード交換数）")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

        if st.checkbox("集計結果テーブルを表示"):
            st.dataframe(trade_cnt[["industry", "count"]].sort_values("count", ascending=False))
    else:
        st.write("選択した業種に属する会社の取引先データが存在しません。")

    # クラスタ結果プレビュー
    if st.sidebar.checkbox("クラスタ結果プレビュー"):
        st.dataframe(df_clustered[["company_id", "company_name", "cluster"]])

if __name__ == "__main__":
    main()




# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import pandas as pd
# import requests
# import streamlit as st
# from sklearn.cluster import KMeans
# from sklearn.feature_extraction.text import TfidfVectorizer

# # 日本語フォント設定
# mpl.rcParams["font.family"]        = "sans-serif"
# mpl.rcParams["font.sans-serif"]   = ["IPAPGothic","Meiryo","Yu Gothic","TakaoPGothic"]
# mpl.rcParams["axes.unicode_minus"] = False

# # --- 1. 名刺データ取得 & DataFrame化 ---
# API_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
# HEADERS = {"accept": "application/json"}
# resp = requests.get(API_URL, params={"offset": 0, "limit": 10000}, headers=HEADERS)
# df = pd.DataFrame(resp.json())

# # --- 2. 会社名クリーン化 ---
# df["clean_name"] = (
#     df["company_name"]
#       .str.replace(r"(株式会社|有限会社|合同会社|（.*?）)", "", regex=True)
#       .str.strip()
# )

# # --- 3. TF-IDF＆KMeans 学習 ---
# vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,6), max_features=2000)
# X = vectorizer.fit_transform(df["clean_name"])

# n_clusters = st.sidebar.slider("クラスタ数（業種数）", 2, 10, 5)
# kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(X)
# df["cluster"] = kmeans.labels_

# # --- 4. クラスタ名（業種名）生成 ---
# terms = vectorizer.get_feature_names_out()
# order = kmeans.cluster_centers_.argsort()[:, ::-1]
# cluster_names = ["／".join(terms[order[i, :5]]) for i in range(n_clusters)]

# # --- 5. UI: 業種→会社 選択 ---
# sel_ind     = st.sidebar.selectbox("業種を選択", cluster_names)
# sel_cluster = cluster_names.index(sel_ind)
# candidates  = df[df["cluster"] == sel_cluster]["company_name"].unique()
# sel_company = st.sidebar.selectbox("会社を選択", candidates)

# # --- 6. 選択会社の取引先取得 & DataFrame化 ---
# sel_company_id = df.loc[df["company_name"] == sel_company, "company_id"].iloc[0]
# resp2 = requests.get(
#     API_URL,
#     params={"offset": 0, "limit": 10000, "company_id": sel_company_id},
#     headers=HEADERS
# )
# partner_df = pd.DataFrame(resp2.json())

# # --- 7. 取引先の会社名クリーン化 & クラスタ予測 ---
# partner_df["clean_name"] = (
#     partner_df["company_name"]
#       .str.replace(r"(株式会社|有限会社|合同会社|（.*?）)", "", regex=True)
#       .str.strip()
# )
# X2 = vectorizer.transform(partner_df["clean_name"])
# partner_df["cluster"] = kmeans.predict(X2)

# # --- 8. クラスタごとに取引件数集計 ---
# trade_cnt = (
#     partner_df
#       .groupby("cluster")
#       .size()
#       .reset_index(name="count")
# )
# trade_cnt["industry"] = trade_cnt["cluster"].map(lambda i: cluster_names[i])

# # --- 9. 可視化 ---
# st.write(f"### {sel_company} の取引業種分布")
# fig, ax = plt.subplots(figsize=(8, 5))
# ax.bar(trade_cnt["industry"], trade_cnt["count"])
# ax.set_ylabel("取引件数（カード交換数）")
# ax.set_xticklabels(trade_cnt["industry"], rotation=45, ha="right")
# st.pyplot(fig)

# # --- 10. 元データプレビュー ---
# if st.checkbox("クラスタ結果を表示"):
#     st.dataframe(df[["company_name", "cluster"]])

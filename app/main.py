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






import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

# 日本語フォント設定
mpl.rcParams["font.family"]        = "sans-serif"
mpl.rcParams["font.sans-serif"]   = ["IPAPGothic","Meiryo","Yu Gothic","TakaoPGothic"]
mpl.rcParams["axes.unicode_minus"] = False

# API取得
API_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
HEADERS = {"accept":"application/json"}
resp = requests.get(API_URL, params={"offset":0,"limit":10000}, headers=HEADERS)
df   = pd.DataFrame(resp.json())

# 会社名前処理
df["clean_name"] = (
    df["company_name"]
      .str.replace(r"(株式会社|有限会社|合同会社|（.*?）)", "", regex=True)
      .str.strip()
)

# ベクトル化とクラスタリング
vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,6), max_features=2000)
X          = vectorizer.fit_transform(df["clean_name"])
n_clusters = st.sidebar.slider("クラスタ数（業種数）", 2, 10, 5)
kmeans     = KMeans(n_clusters=n_clusters, random_state=42).fit(X)
df["cluster"] = kmeans.labels_

# クラスタ名生成
terms  = vectorizer.get_feature_names_out()
order  = kmeans.cluster_centers_.argsort()[:, ::-1]
cluster_names = ["／".join(terms[order[i,:5]]) for i in range(n_clusters)]

# UI: 業種→会社選択 → 可視化
sel_ind       = st.sidebar.selectbox("業種を選択", cluster_names)
sel_cluster   = cluster_names.index(sel_ind)
candidates    = df[df["cluster"]==sel_cluster]["company_name"].unique()
sel_company   = st.sidebar.selectbox("会社を選択", candidates)

# 選択会社の company_id を取得
sel_company_id = df[df['company_name'] == sel_company]['company_id'].iloc[0]

# API でその会社の「取引先カード」を取得
resp2 = requests.get(
    API_URL,
    params={"offset": 0, "limit": 10000, "company_id": sel_company_id},
    headers=HEADERS
)
partner_df = pd.DataFrame(resp2.json())

# 取得先にクラスタ予測を割り当て
X2 = vectorizer.transform(partner_df['company_name'])
partner_df['cluster'] = kmeans.predict(X2)

# クラスタ（業種）ごとに取引件数を集計
trade_cnt = (
    partner_df.groupby("cluster")
    .size()
    .reset_index(name='count')
)
trade_cnt['industry'] = trade_cnt['cluster'].map(lambda i: cluster_names[i])

# 可視化
st.write(f"### {sel_company} の取引業種分布")
fig, ax = plt.subplots(figsize=(8,5))
ax.bar(trade_cnt["industry"], trade_cnt["count"])
ax.set_ylabel("取引件数（カード交換数）")
ax.set_xticklabels(trade_cnt["industry"], rotation=45, ha="right")
st.pyplot(fig)

# 元データプレビュー
if st.checkbox("クラスタ結果を表示"):
    st.dataframe(df[["company_name","cluster"]])












# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# import requests
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans

# # — 日本語フォント設定 —
# mpl.rcParams["font.family"]      = "sans-serif"
# mpl.rcParams["font.sans-serif"] = ["IPAPGothic","Meiryo","Yu Gothic","TakaoPGothic"]
# mpl.rcParams["axes.unicode_minus"] = False

# # — 全カードデータ取得・前処理 —
# @st.cache_data
# def load_cards(offset=0, limit=10000):
#     API_URL  = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
#     resp     = requests.get(API_URL, params={"offset": offset, "limit": limit}, headers={"accept": "application/json"})
#     df_all   = pd.DataFrame(resp.json())
#     # 会社名から「株式会社／有限会社／合同会社」「(…)」を削除
#     df_all["clean_name"] = (
#         df_all["company_name"]
#               .str.replace(r"(株式会社|有限会社|合同会社|（.*?）)", "", regex=True)
#               .str.strip()
#     )
#     return df_all

# df = load_cards()

# # — ユニーク企業だけ抽出してクラスタリングモデル作成 —
# unique_companies = (
#     df[["company_id", "clean_name"]]
#     .drop_duplicates(subset="company_id")
#     .reset_index(drop=True)
# )

# # TF-IDF＋KMeans
# vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2,4), max_features=1500)
# X_uniques   = vectorizer.fit_transform(unique_companies["clean_name"])

# n_clusters = st.sidebar.slider("クラスタ数（想定業種数）", min_value=2, max_value=10, value=5)
# kmeans     = KMeans(n_clusters=n_clusters, random_state=42)
# kmeans.fit(X_uniques)

# # クラスタ名（上位5特徴語をスラッシュ区切りで）
# terms  = vectorizer.get_feature_names_out()
# order  = kmeans.cluster_centers_.argsort()[:, ::-1]
# cluster_names = ["／".join(terms[order[i, :5]]) for i in range(n_clusters)]
# cluster_map   = {i: name for i, name in enumerate(cluster_names)}

# unique_companies["cluster"]  = kmeans.labels_
# unique_companies["industry"] = unique_companies["cluster"].map(cluster_map)

# # — サイドバー：業種→企業選択 —
# sel_industry = st.sidebar.selectbox("業種を選択", cluster_names)
# sel_cluster  = cluster_names.index(sel_industry)
# candidates   = unique_companies[unique_companies["cluster"] == sel_cluster]
# sel_company  = st.sidebar.selectbox("会社を選択", candidates["clean_name"].tolist())

# # 選択企業のID取得
# sel_company_id = candidates.loc[candidates["clean_name"] == sel_company, "company_id"].iloc[0]

# # — パートナー（取引先）カードフィルタリング —
# # 全カードから company_id が sel_company_id のレコードのみ抽出
# partner_df = df[df["company_id"] == sel_company_id].reset_index(drop=True)

# # クラスタ予測＆集計
# X_partners      = vectorizer.transform(partner_df["clean_name"])
# partner_labels  = kmeans.predict(X_partners)
# trade_cnt       = (
#     pd.Series(partner_labels)
#       .value_counts(sort=False)
#       .rename_axis("cluster")
#       .reset_index(name="count")
# )
# trade_cnt["industry"] = trade_cnt["cluster"].map(cluster_map)

# # — 可視化 —
# st.write(f"### 「{sel_company}」の取引先業種分布 (カード交換件数)")
# fig, ax = plt.subplots(figsize=(8, 5))
# ax.bar(trade_cnt["industry"], trade_cnt["count"])
# ax.set_xlabel("業種")
# ax.set_ylabel("カード交換数")
# ax.set_xticklabels(trade_cnt["industry"], rotation=45, ha="right")
# plt.tight_layout()
# st.pyplot(fig)

# # — データプレビュー（オプション） —
# if st.checkbox("クラスタリング結果を一覧表示"):
#     st.dataframe(unique_companies[["clean_name", "industry"]].sort_values("industry"))

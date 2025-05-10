import pandas as pd
import requests
import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# === Page Setting ===
st.set_page_config(page_title="名刺交換分析", layout="wide")
st.title("📇 Circuit Business Card Analytics Dashboard")

# === API Setting ===
API_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=2000"
SIMILAR_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/7051851097/similar_top10_users"
HEADERS = {
    "Content-Type": "application/json",
}

# === Data Getting ===
@st.cache_data(show_spinner=True)
def load_card_data():
    res = requests.get(API_URL, headers=HEADERS)
    if res.status_code == 200:
        return pd.DataFrame(res.json())
    else:
        st.error("❌ Failed to load card data.")
        return pd.DataFrame()

@st.cache_data(show_spinner=True)
def load_similar_users():
    res = requests.get(SIMILAR_URL, headers=HEADERS)
    if res.status_code == 200:
        return pd.DataFrame(res.json())
    else:
        st.warning("Couldn't load similar users data.")
        return pd.DataFrame()

# @st.cache_data(show_spinner=False)
# def get_company_info(company_id):
#     url = f"hhttps://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/{company_id}/offset=0&limit=500"
#     res = requests.get(url, headers=HEADERS)
#     if res.status_code == 200:
#         return res.json()
#     else:
#         return None


# === Data Loading ===
with st.spinner("🔄 Loading card data..."):
    df = load_card_data()

with st.spinner("🔄 Loading similar users..."):
    df_similar = load_similar_users()

# === Pages ===
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧑‍🤝‍🧑 Similar Users", "🔗 Business Card Exchange Network"])

# === tab1 ===
with tab1:
    st.subheader("🔍 Raw Business Card Data")
    st.dataframe(df, use_container_width=True)

    st.subheader("🏢 Top 10 Companies by Card Count")
    if "company_name" in df.columns:
        top_companies = df["company_name"].value_counts().head(10)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.bar_chart(top_companies)
        with col2:
            st.markdown("### 🔝 Company Ranking")
            st.write(top_companies)

    if "position" in df.columns:
        st.subheader("💼 Top 10 Positions")
        position_count = df["position"].value_counts().head(10)
        st.bar_chart(position_count)


# === tab2 ===
with tab2:
    st.subheader("🧑‍💼 Find Similar Users by User ID")

    if "input_user_id" not in st.session_state:
        st.session_state.input_user_id = "00000000000"  # default

    input_id = st.text_input("Enter a user_id:", value=st.session_state.input_user_id)
    st.session_state.input_user_id = input_id  # Save to session
    
    def get_similar_users(uid):
        url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{uid}/similar_top10_users"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return pd.DataFrame(res.json())
        else:
            return pd.DataFrame()

    if st.button("🔍 Search"):
        with st.spinner("Fetching similar users..."):
            similar_df = get_similar_users(input_id)

        if not similar_df.empty:
            st.success(f"Found {len(similar_df)} similar users for user_id: {input_id}")
            st.dataframe(similar_df, use_container_width=True)

            st.subheader("📈 Similarity Score Chart")
            chart_df = similar_df.sort_values("similarity", ascending=True)
            st.bar_chart(chart_df.set_index("user_id")["similarity"])
        else:
            st.warning("No similar users found.")

# === tab3===
with tab3:
    st.subheader("🔗 Exchange Network for Selected User (From /contacts API)")

    user_id = st.session_state.get("input_user_id", None)

    if not user_id:
        st.warning("Please enter a user ID in tab 2 first.")
        st.stop()

    # contacts API
    @st.cache_data(show_spinner=True)
    def fetch_user_contacts(uid):
        url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{uid}?offset=0&limit=100"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return pd.DataFrame(res.json())
        else:
            return pd.DataFrame()

    contact_df = fetch_user_contacts(user_id)

    if contact_df.empty:
        st.warning("No contacts found for this user.")
        st.stop()

    st.success(f"Found {len(contact_df)} contacts for user {user_id}")
    

    import networkx as nx
    from pyvis.network import Network
    import streamlit.components.v1 as components


    if "cards_df" not in st.session_state:
        st.session_state.cards_df = load_card_data()

    name_map = dict(zip(
    st.session_state.cards_df["user_id"].astype(str),
    st.session_state.cards_df["full_name"]
))

    G = nx.DiGraph()
    for row in contact_df.itertuples():
        from_user = name_map.get(str(row.owner_user_id), str(row.owner_user_id))
        to_user = name_map.get(str(row.user_id), str(row.user_id))
        G.add_edge(from_user, to_user)

    net = Network(height="700px", width="100%", directed=True)
    net.from_nx(G)
    net.repulsion(node_distance=150, central_gravity=0.2)

    net.save_graph("contact_network.html")
    components.html(open("contact_network.html", "r", encoding="utf-8").read(), height=750)

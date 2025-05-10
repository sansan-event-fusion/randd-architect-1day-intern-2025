from pathlib import Path

import pandas as pd
import streamlit as st

# タイトル
st.title("mattsunkunアプリ")

path = Path(__file__).parent / "dummy_data.csv"
df_dummy = pd.read_csv(path.as_uri(), dtype=str)

st.dataframe(df_dummy)

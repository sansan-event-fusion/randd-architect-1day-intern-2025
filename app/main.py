import os
import random
import re
from pathlib import Path

import pydeck as pdk
import requests
import streamlit as st
from dotenv import load_dotenv
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

load_dotenv(Path(__file__).parent.parent / ".env")

_geolocator = Nominatim(user_agent="sample_app", timeout=10)
_geocode = RateLimiter(
    _geolocator.geocode,
    min_delay_seconds=1.1, # Nominatim ポリシー準拠
    max_retries=3, # タイムアウト時に自動リトライ
    error_wait_seconds=2.0 # 失敗時の待機
)

CARDS_USER_API_URL = os.getenv("CARDS_USER_API_URL", default="https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}")
CONTACTS_API_URL = os.getenv("CONTACTS_API_URL", default="https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/")
CONTACTS_OWNER_COMPANY_API_URL = os.getenv("CONTACTS_OWNER_COMPANY_API_URL", default="https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/{owner_company_id}")

if not CONTACTS_API_URL or not CONTACTS_OWNER_COMPANY_API_URL or not CARDS_USER_API_URL:
    st.write("環境変数が設定されていません。")
    st.stop()

st.set_page_config(
    page_title="サンプルアプリ",
    page_icon=":guardsman:",
    layout="wide",
)
st.title("サンプルアプリ")

# 1. contactsからランダムに1件選択
contacts_res = requests.get(CONTACTS_API_URL, timeout=5)
if contacts_res.status_code != 200:
    st.write("contacts取得失敗")
    st.stop()
contacts = contacts_res.json()
if not contacts:
    st.write("contactsが空です")
    st.stop()
contact = random.choice(contacts)
owner_company_id = contact.get("owner_company_id")

# 2. owner_company_idでcontacts_owner_company_api_urlを利用して名刺を取得
contacts_owner_company_url = CONTACTS_OWNER_COMPANY_API_URL.format(owner_company_id=owner_company_id)
owner_contacts_res = requests.get(contacts_owner_company_url, timeout=5)
if owner_contacts_res.status_code != 200:
    st.write("owner companyのcontacts取得失敗")
    st.stop()
owner_contacts = owner_contacts_res.json()

# 3. 取引相手user_idを取得
user_ids = set(c.get("user_id") for c in owner_contacts if c.get("user_id"))

# 4. user_idでcardsからaddressを取得
def geocode_address(address: str) -> tuple[float | None, float | None]:
    """住所文字列から (lat, lon) を返す。失敗時は (None, None)。"""
    if not address:
        return None, None
    # 数値を除去
    address_no_num = re.sub(r"\d+", "", address)
    # 改行や余分な空白を除去
    normalized = " ".join(address_no_num.split())
    try:
        location = _geocode(normalized)
        if location is not None:
            return float(location.latitude), float(location.longitude)
    except Exception as e: # geopy の GeocoderTimedOut など
        st.write(f"[Geocoding] エラー: {e}")
    return None, None

addresses = []
user_id_list = list(user_ids) # set → list に変換
sample_user_ids = user_id_list[:30] # 先頭30件をサンプルとして取得
for user_id in sample_user_ids:
    if not user_id:
        continue
    user_cards_url = CARDS_USER_API_URL.format(user_id=user_id)
    user_cards_res = requests.get(user_cards_url, timeout=5)
    if user_cards_res.status_code != 200:
        continue
    user_card = user_cards_res.json()
    if isinstance(user_card, list):
        user_card = user_card[0] if user_card else {}
    if isinstance(user_card, dict):
        addr_str = user_card.get("address")

    if not addr_str:
        continue
    # 住所が空でない場合、geocode_addressを呼び出す
    if addr_str:
        lat, lon = geocode_address(addr_str)
        if lat and lon:
            addresses.append({"lat": lat, "lon": lon})

if not addresses:
    st.write("住所が取得できませんでした")
    st.stop()
st.write(f"取得した住所数: {len(addresses)}")

# 5. addressのヒートマップを表示
if addresses:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=sum(a["lat"] for a in addresses) / len(addresses),
            longitude=sum(a["lon"] for a in addresses) / len(addresses),
            zoom=5,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HeatmapLayer",
                data=addresses,
                get_position="[lon, lat]",
                aggregation="MEAN",
                opacity=0.9,
            ),
        ],
    ))
else:
    st.write("ヒートマップ表示用の住所データがありません")


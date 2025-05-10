import streamlit as st
from utils import (
    get_cards_info,
    get_contact_histories_by_user_id,
    get_contact_histories_count,
    get_max_contact_time,
    get_owner_companies_by_company_id,
    get_recommendation_users,
    plot_contact_history_by_date,
    plot_contact_history_by_time,
)

menu = st.sidebar.radio("メニューを選択してください", ("名刺交換履歴", "おすすめの相手"))

if menu == "名刺交換履歴":
    st.title("ユーザー名刺検索ツール")
    st.caption("ユーザーIDの例: 7558936248")

    user_id = st.number_input("ユーザーIDを入力してください", min_value=0, max_value=10**10, value=0, step=1)

    if st.button("検索"):
        # 名刺情報取得
        owner_data = get_cards_info(user_id)

        if len(owner_data) == 0:
            st.write("ユーザーが存在しませんでした。")
        else:
            st.subheader("ユーザー情報")
            owner_name = owner_data[0]["full_name"]
            company_name = owner_data[0]["company_name"]
            company_id = owner_data[0]["company_id"]

            st.write(f"👤 **名前**: {owner_name}")
            st.write(f"🏢 **会社名**: {company_name}")

            # 名刺枚数取得
            data_owner_count = get_contact_histories_count(user_id)
            st.write(f"💼 **交換した名刺の枚数**: {data_owner_count}")

            # 名刺情報取得
            st.subheader("ユーザーの名刺交換情報")
            data_owner = get_contact_histories_by_user_id(user_id)
            st.write("日付ごとの名刺交換回数")
            plot_contact_history_by_date(data_owner)
            st.write("時間帯ごとの名刺交換回数")
            plot_contact_history_by_time(data_owner)

            # 会社の名刺情報取得
            st.subheader("ユーザーの会社の名刺交換情報")
            data_company = get_owner_companies_by_company_id(company_id)
            st.write("日付ごとの名刺交換回数")
            plot_contact_history_by_date(data_company)
            st.write("時間帯ごとの名刺交換回数")
            plot_contact_history_by_time(data_company)

            with st.expander("名刺交換相手を表示"):
                if len(data_owner) == 0:
                    st.write("名刺情報は見つかりませんでした。")
                else:
                    for data_owner_item in data_owner:
                        card_user_id = data_owner_item["user_id"]
                        owner_data = get_cards_info(card_user_id)
                        st.write(f"👤 **名前**: {owner_data[0]['full_name']}")
                        st.write(f"🏢 **会社名**: {owner_data[0]['company_name']}")
                        st.write("")
else:
    st.title("おすすめの相手")
    st.caption("ユーザーIDの例: 7558936248")

    user_id = st.number_input("ユーザーIDを入力してください", min_value=0, max_value=10**10, value=0, step=1)
    # おすすめユーザー
    data_recommendation = get_recommendation_users(user_id)

    if len(data_recommendation) == 0:
        st.info("おすすめの相手は見つかりませんでした。")
    else:
        st.write("")
        for data_recommendation_item in data_recommendation:
            recommendation_user_id = data_recommendation_item["user_id"]
            data_owner = get_contact_histories_by_user_id(recommendation_user_id)
            st.write(f"🏢 **会社名**: {data_recommendation_item['company_name']}")
            st.write(f"👤 **名前**: {data_recommendation_item['full_name']}")

            recommendation_time = get_max_contact_time(data_owner)
            st.write(f"📅 **交換におすすめの時間**: {recommendation_time['hour']}:00")

            with st.expander(f"{data_recommendation_item['full_name']}さんの名刺交換情報"):
                st.write("時間帯ごとの名刺交換回数")
                plot_contact_history_by_time(data_owner)
            st.write("")

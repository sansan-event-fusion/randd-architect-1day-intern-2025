# external imports
import pandas as pd
import plotly.express as px
import streamlit as st

# internal imports
from app.crud import BusinessCardCRUD, ContactHistoryCRUD


def display_analytics_dashboard() -> None:
    """名刺交換効率化アナリティクスダッシュボード."""

    # サイドバーでデータ設定
    st.sidebar.subheader("📊 データ設定")
    contact_limit = st.sidebar.slider(
        "交換履歴取得数",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100,
        help="分析に使用する交換履歴の件数を設定",
    )

    card_limit = st.sidebar.slider(
        "名刺取得数", min_value=50, max_value=5000, value=500, step=50, help="分析に使用する名刺の件数を設定"
    )

    # データ取得
    contacts_crud = ContactHistoryCRUD()
    cards_crud = BusinessCardCRUD()

    # データロード
    with st.spinner(f"データを読み込み中... (交換履歴: {contact_limit:,}件, 名刺: {card_limit:,}件)"):
        all_contacts = contacts_crud.get_all_contacts(limit=contact_limit)
        all_cards = cards_crud.get_all_cards(limit=card_limit)

    if not all_contacts:
        st.warning("交換履歴データがありません")
        return

    # データを DataFrame に変換
    contacts_df = pd.DataFrame([contact.model_dump() for contact in all_contacts])
    cards_df = pd.DataFrame([card.model_dump() for card in all_cards])

    # サイドバーにデータ統計表示
    st.sidebar.subheader("📈 データ統計")
    st.sidebar.metric("実際の交換履歴数", f"{len(contacts_df):,}件")
    st.sidebar.metric("実際の名刺数", f"{len(cards_df):,}件")
    if len(contacts_df) > 0:
        unique_users = len(contacts_df["owner_user_id"].unique())
        unique_companies = len(contacts_df["owner_company_id"].unique())
        st.sidebar.metric("参加ユーザー数", f"{unique_users:,}人")
        st.sidebar.metric("参加企業数", f"{unique_companies:,}社")

    # datetime型に変換
    contacts_df["created_at"] = pd.to_datetime(contacts_df["created_at"])
    # 便利なカラムを追加
    contacts_df["contact_datetime"] = contacts_df["created_at"]
    contacts_df["target_user_id"] = contacts_df["user_id"]
    contacts_df["target_company_id"] = contacts_df["company_id"]

    # タブで分割
    tab1, tab2, tab3, tab4 = st.tabs(["🕐 時間帯分析", "🗺️ 地域分析", "🔗 類似度分析", "💡 最適化提案"])

    with tab1:
        display_time_analysis(contacts_df)

    with tab2:
        display_regional_analysis(contacts_df, cards_df)

    with tab3:
        from .similarity_network import display_similarity_analysis

        display_similarity_analysis(cards_crud, card_limit)

    with tab4:
        display_optimization_suggestions(contacts_df)


def display_time_analysis(contacts_df: pd.DataFrame) -> None:
    """時間帯・曜日別の交換トレンド分析."""
    st.subheader("🕐 時間帯・曜日別交換トレンド")

    # 時間帯別分析
    contacts_df["hour"] = contacts_df["contact_datetime"].dt.hour
    contacts_df["weekday"] = contacts_df["contact_datetime"].dt.day_name()
    contacts_df["date"] = contacts_df["contact_datetime"].dt.date

    col1, col2 = st.columns(2)

    with col1:
        # 時間帯別ヒストグラム
        hourly_counts = contacts_df["hour"].value_counts().sort_index()
        fig_hour = px.bar(
            x=hourly_counts.index,
            y=hourly_counts.values,
            title="時間帯別名刺交換回数",
            labels={"x": "時間", "y": "交換回数"},
        )
        fig_hour.update_layout(showlegend=False)
        st.plotly_chart(fig_hour, use_container_width=True)

    with col2:
        # 曜日別分析
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_counts = contacts_df["weekday"].value_counts().reindex(weekday_order)

        fig_weekday = px.bar(
            x=["月", "火", "水", "木", "金", "土", "日"],
            y=weekday_counts.values,
            title="曜日別名刺交換回数",
            labels={"x": "曜日", "y": "交換回数"},
        )
        fig_weekday.update_layout(showlegend=False)
        st.plotly_chart(fig_weekday, use_container_width=True)

    # ヒートマップ
    st.subheader("📅 曜日 - 時間帯ヒートマップ")
    heatmap_data = contacts_df.groupby(["weekday", "hour"]).size().unstack(fill_value=0)  # noqa: PD010
    heatmap_data = heatmap_data.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

    fig_heatmap = px.imshow(
        heatmap_data.values,
        x=list(range(24)),
        y=["月", "火", "水", "木", "金", "土", "日"],
        title="曜日 - 時間帯別交換頻度",
        labels={"x": "時間", "y": "曜日", "color": "交換回数"},
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)


def display_regional_analysis(contacts_df: pd.DataFrame, cards_df: pd.DataFrame) -> None:
    """地域別活動分析."""
    st.subheader("🗺️ 地域別活動分析")

    # 名刺データから地域情報を抽出
    cards_df["prefecture"] = cards_df["address"].str.extract(
        r"([\u4e00-\u9faf]{2,3}県|[\u4e00-\u9faf]{2,3}府|[\u4e00-\u9faf]{2,3}都|北海道)"
    )

    # owner_user_id をキーに地域情報をマージ
    contacts_with_region = contacts_df.merge(
        cards_df[["user_id", "prefecture"]].rename(
            columns={"user_id": "owner_user_id", "prefecture": "owner_prefecture"}
        ),
        on="owner_user_id",
        how="left",
    )

    col1, col2 = st.columns(2)

    with col1:
        # 地域別交換回数
        regional_counts = contacts_with_region["owner_prefecture"].value_counts().head(10)
        if not regional_counts.empty:
            fig_region = px.bar(
                x=regional_counts.values,
                y=regional_counts.index,
                orientation="h",
                title="地域別名刺交換回数 (Top 10)",
                labels={"x": "交換回数", "y": "都道府県"},
            )
            st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.info("地域データが不足しています")

    with col2:
        company_counts = contacts_with_region.groupby("owner_company_id").size().sort_values(ascending=False).head(10)

        # 会社IDから会社名を取得
        company_names = []
        for company_id in company_counts.index:
            company_info = cards_df[cards_df["company_id"] == company_id]
            if not company_info.empty:
                company_name = company_info.iloc[0]["company_name"]
                # 長すぎる場合は短縮
                if len(company_name) > 20:
                    company_name = company_name[:17] + "..."
                company_names.append(company_name)
            else:
                company_names.append(f"会社ID:{company_id}")

        fig_company = px.bar(
            x=company_counts.values,
            y=company_names,
            orientation="h",
            title="会社別交換回数 (Top 10)",
            labels={"x": "交換回数", "y": "会社"},
        )
        st.plotly_chart(fig_company, use_container_width=True)


def display_similarity_analysis(cards_crud: BusinessCardCRUD, card_limit: int) -> None:  # noqa: PLR0915, C901
    """類似度分析."""
    st.subheader("🔗 類似度分析")
    # 説明文を追加
    st.info("💡 各ユーザーに対して **上位10名** の類似ユーザーを分析します")

    # サンプルユーザー数の設定
    sample_limit = min(50, card_limit)  # 最大50人まで、card_limitを超えない

    # サンプルユーザーを取得
    sample_cards = cards_crud.get_all_cards(limit=sample_limit)
    if not sample_cards:
        st.warning("名刺データがありません")
        return

    # ユーザー選択
    user_options = {f"{card.full_name} ({card.company_name})": card.user_id for card in sample_cards}
    selected_user_display = st.selectbox("分析対象ユーザーを選択", list(user_options.keys()))
    selected_user_id = user_options[selected_user_display]

    # 類似ユーザーを取得
    with st.spinner("類似ユーザーを分析中..."):
        try:
            similar_users = cards_crud.get_similar_users(int(selected_user_id))

            if similar_users:
                # 類似度データを DataFrame に変換
                similarity_data = [
                    {
                        "名前": user.full_name,
                        "会社名": user.company_name,
                        "類似度": user.similarity,
                        "user_id": user.user_id,
                    }
                    for user in similar_users
                ]

                similarity_df = pd.DataFrame(similarity_data)

                col1, col2 = st.columns(2)

                with col1:
                    # 類似度分布ヒストグラム
                    fig_hist = px.histogram(
                        similarity_df,
                        x="類似度",
                        nbins=10,
                        title="類似度分布",
                        labels={"x": "類似度", "y": "ユーザー数"},
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)

                    # 統計情報
                    st.subheader("📊 類似度統計 (Top 10)")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("検出ユーザー数", f"{len(similarity_df)}人")
                    with col_b:
                        st.metric("最高類似度", f"{similarity_df['類似度'].max():.3f}")
                    with col_c:
                        # 上位3の平均
                        top3_avg = similarity_df.head(3)["類似度"].mean()
                        st.metric("上位3平均", f"{top3_avg:.3f}")

                with col2:
                    # 類似度ランキング 棒グラフ
                    top_similar = similarity_df.head(10)
                    fig_bar = px.bar(
                        top_similar,
                        x="類似度",
                        y="名前",
                        orientation="h",
                        title="類似度ランキング (Top 10)",
                        labels={"x": "類似度", "y": "ユーザー"},
                        color="類似度",
                        color_continuous_scale="viridis",
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                # 詳細テーブル
                st.subheader("📋 類似ユーザー詳細")
                # 類似度でソート
                similarity_df_sorted = similarity_df.sort_values("類似度", ascending=False)

                # 類似度カテゴリー分類(Top 10内での相対評価)
                def categorize_similarity(score):  # このデモデータだとめっちゃ高いのばっかだから全部`極めて高い`
                    if score >= 0.95:
                        return "🔥 極めて高い"
                    if score >= 0.9:
                        return "⭐ 高い"
                    if score >= 0.8:
                        return "✅ 中程度"
                    return "📊 標準"

                similarity_df_sorted["類似度レベル"] = similarity_df_sorted["類似度"].apply(categorize_similarity)

                # 表示用にuser_idを除外
                display_df = similarity_df_sorted[["名前", "会社名", "類似度", "類似度レベル"]].copy()
                display_df["類似度"] = display_df["類似度"].round(3)

                st.dataframe(display_df, use_container_width=True)

                # 会社別類似度分析
                st.subheader("🏢 会社別類似度分析")
                company_similarity = similarity_df.groupby("会社名")["類似度"].agg(["mean", "count"]).reset_index()
                company_similarity.columns = ["会社名", "平均類似度", "ユーザー数"]
                company_similarity = company_similarity.sort_values("平均類似度", ascending=False)

                if len(company_similarity) > 1:
                    fig_company = px.scatter(
                        company_similarity,
                        x="平均類似度",
                        y="ユーザー数",
                        hover_data=["会社名"],
                        title="会社別類似度vs人数",
                        labels={"x": "平均類似度", "y": "類似ユーザー数"},
                    )
                    st.plotly_chart(fig_company, use_container_width=True)
                else:
                    st.info("会社別分析には複数の会社のデータが必要です")

            else:
                st.info("類似ユーザーが見つかりませんでした")

        except Exception as e:  # noqa: BLE001
            st.error(f"類似度分析エラー: {e!s}")


def display_optimization_suggestions(contacts_df: pd.DataFrame) -> None:
    """最適化提案."""
    st.subheader("💡 最適化提案")

    # 時間帯分析
    contacts_df["hour"] = contacts_df["contact_datetime"].dt.hour
    peak_hours = contacts_df["hour"].value_counts().head(3)

    # 曜日分析
    contacts_df["weekday"] = contacts_df["contact_datetime"].dt.day_name()
    peak_days = contacts_df["weekday"].value_counts().head(3)

    col1, col2 = st.columns(2)

    with col1:
        st.info("⏰ **最適な交換時間帯**")
        for i, (hour, count) in enumerate(peak_hours.items(), 1):
            st.write(f"{i}. {hour}時台 ({count}回)")

        st.info("📅 **最適な曜日**")
        weekday_jp = {
            "Monday": "月曜日",
            "Tuesday": "火曜日",
            "Wednesday": "水曜日",
            "Thursday": "木曜日",
            "Friday": "金曜日",
            "Saturday": "土曜日",
            "Sunday": "日曜日",
        }
        for i, (day, count) in enumerate(peak_days.items(), 1):
            st.write(f"{i}. {weekday_jp.get(day, day)} ({count}回)")

    with col2:
        st.success("🎯 **アクションプラン**")
        st.write("• ピーク時間帯での積極的なネットワーキング")
        st.write("• 低活動時間帯での差別化戦略")
        st.write("• 継続関係構築のフォローアップ強化")
        st.write("• 地域特性を活かした展開")

        # データサマリー
        st.warning("📊 **データサマリー**")
        total_contacts = len(contacts_df)
        unique_companies = len(contacts_df["owner_company_id"].unique())
        unique_users = len(contacts_df["owner_user_id"].unique())

        st.write(f"• 総交換回数: {total_contacts:,}回")
        st.write(f"• 参加企業数: {unique_companies:,}社")
        st.write(f"• 参加ユーザー数: {unique_users:,}人")

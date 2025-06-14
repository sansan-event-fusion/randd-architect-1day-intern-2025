# external imports
import pandas as pd
import plotly.express as px
import streamlit as st

# internal imports
from app.crud import BusinessCardCRUD, ContactHistoryCRUD


def display_analytics_dashboard() -> None:
    """名刺交換効率化アナリティクスダッシュボード."""
    st.header("📊 名刺交換効率化アナリティクス")

    # データ取得
    contacts_crud = ContactHistoryCRUD()
    cards_crud = BusinessCardCRUD()

    # データロード
    with st.spinner("データを読み込み中..."):
        all_contacts = contacts_crud.get_all_contacts(limit=1000)
        all_cards = cards_crud.get_all_cards(limit=500)

    if not all_contacts:
        st.warning("交換履歴データがありません")
        return

    # データを DataFrame に変換
    contacts_df = pd.DataFrame([contact.model_dump() for contact in all_contacts])
    cards_df = pd.DataFrame([card.model_dump() for card in all_cards])

    # datetime型に変換
    contacts_df["created_at"] = pd.to_datetime(contacts_df["created_at"])
    # 便利なカラムを追加
    contacts_df["contact_datetime"] = contacts_df["created_at"]
    contacts_df["target_user_id"] = contacts_df["user_id"]
    contacts_df["target_company_id"] = contacts_df["company_id"]

    # タブで分割
    tab1, tab2, tab3 = st.tabs(["🕐 時間帯分析", "🗺️ 地域分析", "💡 最適化提案"])

    with tab1:
        display_time_analysis(contacts_df)

    with tab2:
        display_regional_analysis(contacts_df, cards_df)

    with tab3:
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

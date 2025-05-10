import streamlit as st
from business_card_recognition import process_business_card
from data_visualization import show_visualization


def main():
    st.title("R&D Architect Intern App")

    # サイドバーでメニューを選択
    menu = st.sidebar.selectbox("メニューを選択してください", ["名刺認識", "データ可視化"])

    if menu == "名刺認識":
        st.header("名刺認識")
        st.write("名刺の画像またはPDFをアップロードしてください。")

        uploaded_file = st.file_uploader("名刺をアップロード", type=["pdf", "png", "jpg", "jpeg"])

        if uploaded_file is not None:
            file_type = uploaded_file.type.split("/")[-1]
            if file_type == "pdf":
                file_type = "pdf"
            else:
                file_type = "image"

            # Process the uploaded file
            with st.spinner("名刺を処理中..."):
                file_bytes = uploaded_file.read()
                info = process_business_card(file_bytes, file_type)

            # Display results
            st.subheader("抽出結果")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**名前**")
                st.write(info["name"] if info["name"] else "認識できませんでした")

                st.markdown("**会社名**")
                st.write(info["company"] if info["company"] else "認識できませんでした")

                st.markdown("**メールアドレス**")
                st.write(info["email"] if info["email"] else "認識できませんでした")

            with col2:
                st.markdown("**住所**")
                st.write(info["address"] if info["address"] else "認識できませんでした")

                st.markdown("**電話番号**")
                st.write(info["phone"] if info["phone"] else "認識できませんでした")

    elif menu == "データ可視化":
        st.header("データ可視化")
        st.write("APIから取得したデータの可視化を表示します。")

        # データ可視化の表示
        show_visualization()


if __name__ == "__main__":
    main()

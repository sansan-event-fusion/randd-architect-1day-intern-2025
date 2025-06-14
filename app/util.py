import unicodedata


def normalize_text(text):
    """日本語テキストを正規化(全角・半角統一、ひらがな・カタカナ変換)"""
    # Unicode正規化
    text = unicodedata.normalize("NFKC", text)
    # 小文字に変換
    text = text.lower()
    return text


def contains_japanese_match(candidate, search_term):
    """日本語を考慮したマッチング"""
    candidate_norm = normalize_text(candidate)
    search_norm = normalize_text(search_term)

    # 基本的な部分一致
    if search_norm in candidate_norm:
        return True

    # ひらがな・カタカナの相互変換チェック
    # カタカナをひらがなに変換
    def kata_to_hira(text):
        return "".join([chr(ord(char) - 96) if "ァ" <= char <= "ヶ" else char for char in text])

    # ひらがなをカタカナに変換
    def hira_to_kata(text):
        return "".join([chr(ord(char) + 96) if "ぁ" <= char <= "ゖ" else char for char in text])

    candidate_hira = kata_to_hira(candidate_norm)
    candidate_kata = hira_to_kata(candidate_norm)
    search_hira = kata_to_hira(search_norm)
    search_kata = hira_to_kata(search_norm)

    # 各パターンでチェック
    return (
        search_norm in candidate_hira
        or search_norm in candidate_kata
        or search_hira in candidate_norm
        or search_kata in candidate_norm
    )

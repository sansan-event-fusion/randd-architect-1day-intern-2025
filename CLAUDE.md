# ビジネスカード接続関係可視化アプリ

## プロジェクト概要
会社名を選択して、その会社のビジネスカード交換関係をグラフで可視化するStreamlitアプリケーション。
カード所有者と接続先ユーザーの関係を有向グラフで表示する。

## 現在の仕様

### 主な機能
1. **会社選択・検索機能**
   - 全会社からの選択が可能
   - 会社名での部分一致検索
   - リアルタイム検索結果フィルタリング

2. **グラフ可視化**
   - 🔴 赤ノード: カード所有者 (owner_user_id)
   - 🔵 青ノード: 接続先ユーザー (user_id)
   - 有向グラフで接続関係を表示

3. **表示制御**
   - カード所有者の最大表示数設定 (1-50個)
   - 接続先ユーザーは次数2以上のもののみ表示
   - グラフの物理シミュレーション有効

4. **統計情報**
   - 選択した会社のカード数
   - 接続関係の総数
   - サイドバーでの統計表示

### データ形式

#### Cards Data Format
```python
cards = [
    {
        'user_id': '3479534060',
        'company_id': '1683446724',
        'full_name': '松田 太郎',
        'position': '次長',
        'company_name': '有限会社井上運輸',
        'address': '千葉県柏市柏3-7-5',
        'phone_number': '070-3121-9804'
    }
]
```

#### Contacts Data Format
```python
contacts = [
    {
        'owner_user_id': '3479534060',
        'owner_company_id': '1683446724',
        'user_id': '156983957',
        'company_id': '1548781344',
        'created_at': '2023-04-13T04:23:40Z'
    }
]
```

### グラフ接続関係
- `owner_user_id` (contacts) → `user_id` (cards): カード所有者の特定
- 有向エッジ: owner → target の接続関係を表現
- 次数フィルタリング: target_userが2回以上接続されている場合のみ表示

### 技術仕様
- **フレームワーク**: Streamlit
- **グラフライブラリ**: streamlit-agraph
- **API**: circuit-trial.stg.rd.ds.sansan.com
- **実行コマンド**: `streamlit run app/main.py`


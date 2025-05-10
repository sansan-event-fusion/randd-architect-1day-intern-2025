# R&D Architect 1day Internship

## 概要
知人経由でアクセスできる人を示してくれるアプリケーション

### 必要な機能
-【OK】 なんらかの形でユーザa(owner_user_id)を一人選ぶ
- aの保有する名刺ユーザ集合B = {b_i | a has b_i's card} を取得(長さ制限：10で，名刺を持っている数が多い順から選択)
- 各b_i in Bに対して，b_iの保有する名刺ユーザ集合C = {c_j | b_i has c_j's card} を取得
- aからのパスが多い順にCから選ぶ(長さ制限：20)
- パスの多さを可視化しつつ，つながりをグラフで表現

---

## Run on local

```bash
poetry install
poetry run streamlit run app/main.py
```

## Run on Docker

```bash
docker build . -f Dockerfile --target prod --tag app
docker run -it --read-only -p 8080:8080 app
```

## Test

```bash
poetry run pytest
```

## Run linter, formatter

```bash
poetry run ruff check .
poetry run ruff format .
```

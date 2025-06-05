# R&D 1day Internship

## ローカル実行

```bash
uv sync
uv run streamlit run app/main.py
```

## コンテナで実行
本番稼働と同等の環境で実行確認します。

```bash
docker build . -f Dockerfile --target prod --tag app
docker run -it --read-only -p 8080:8080 app
```

## Test
余裕があればテストも実行しましょう。
```bash
uv run pytest
```

## Run linter, formatter
push する前にローカルでコードのチェックをしましょう。
```bash
uv run ruff check .
uv run ruff format .
```

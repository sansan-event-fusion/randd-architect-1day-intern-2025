# R&D Architect 1day Internship

## Run on local

```bash
poetry install
poetry run streamlit run app/main.py
```

## Run on Docker

```bash
docker build . -f Dockerfile --target dev --tag app
docker run -it -p 8080:8080 -v $(pwd)/:/app/ app
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

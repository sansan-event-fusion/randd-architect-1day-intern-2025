# R&D 1day Internship

## Run on local

```bash
poetry install
poetry run streamlit run app/main.py
```

## Run on Docker

```bash
docker build . -f docker/Dockerfile --target prod --tag sansan-iday-intern-app
docker run -it --read-only -p 8080:8080 sansan-iday-intern-app
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

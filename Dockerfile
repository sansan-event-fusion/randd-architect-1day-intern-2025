ARG PYTHON_VERSION=3.10
ARG POETRY_VERSION=1.8.5
ARG PYSETUP_PATH="/opt/pysetup"
ARG DEBIAN_VERSION=bookworm

#############################################
# base ステージ
# ビルダーや開発環境の共通設定
#############################################
FROM python:${PYTHON_VERSION}-${DEBIAN_VERSION} AS base
ARG POETRY_VERSION
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100
ENV POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH=${POETRY_HOME}/bin:$PATH
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -

#############################################
# build 用ステージ
# プロジェクトのビルドをするためのイメージ
#############################################
FROM base AS build
ARG PYSETUP_PATH
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR ${PYSETUP_PATH}
COPY pyproject.toml poetry.lock* README.md ./
COPY app/ app/
RUN poetry install --only=main

#############################################
# production 用ステージ
# ビルドした依存関係やソースを build ステージからコピーする (poetry は含まない)
#############################################
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS prod
ARG PYSETUP_PATH
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR /app
COPY --from=build ${PYSETUP_PATH} /app
RUN sed -i 's|/opt/pysetup/.venv/bin/python|/app/.venv/bin/python|g' /app/.venv/bin/streamlit
RUN useradd -m appuser
USER appuser
CMD ["/app/.venv/bin/streamlit", "run", "app/main.py"]

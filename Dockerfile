ARG PYTHON_VERSION=3.10
ARG POETRY_VERSION=2.1.2
ARG PYSETUP_PATH="/opt/pysetup"
ARG DEBIAN_VERSION=bookworm

#############################################
# base ステージ
# ビルダーや開発環境の共通設定
#############################################
FROM python:${PYTHON_VERSION}-${DEBIAN_VERSION} AS base
ARG POETRY_VERSION
ARG PYSETUP_PATH
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100
ENV POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH=${POETRY_HOME}/bin:${PYSETUP_PATH}/.venv/bin:$PATH
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -

#############################################
# 開発用ステージ
# 開発環境を構築する
#############################################
FROM base AS dev
ARG PYSETUP_PATH
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN poetry install
CMD [ "poetry", "run", "streamlit", "run", "app/main.py" ]

#############################################
# build 用ステージ
# プロジェクトのビルドをする
#############################################
FROM base AS build
ARG PYSETUP_PATH
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR ${PYSETUP_PATH}
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only=main

#############################################
# production 用ステージ
# ビルドした依存関係やソースを build ステージからコピーする (poetry は含まない)
#############################################
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS prod
ARG PYSETUP_PATH
ENV PATH="${PYSETUP_PATH}/.venv/bin:$PATH"
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
COPY --from=build ${PYSETUP_PATH}/.venv/ ${PYSETUP_PATH}/.venv/
WORKDIR /app
COPY app/ app/
COPY .streamlit/ .streamlit/
USER 1000
EXPOSE 8080
CMD ["streamlit", "run", "app/main.py"]

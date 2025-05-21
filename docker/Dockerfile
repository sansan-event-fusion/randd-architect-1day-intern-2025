ARG PYTHON_VERSION=3.13
ARG PYSETUP_PATH=/opt/pysetup

ARG POETRY_VERSION=2.1.3
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
    PIP_DISABLE_PIP_VERSION_CHECK=on
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
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only=main

#############################################
# production 用ステージ
# ビルドした依存関係やソースを build ステージからコピーする
#############################################
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS prod
ARG PYSETUP_PATH
ENV PATH=${PYSETUP_PATH}/.venv/bin:$PATH \
    PYTHONPATH="src" \
    PYTHONUNBUFFERED=1
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR /app
COPY --from=build ${PYSETUP_PATH}/.venv/ ${PYSETUP_PATH}/.venv/
COPY app/ app/
COPY .streamlit/ .streamlit/
USER 1000
EXPOSE 8080
CMD ["streamlit", "run", "app/main.py"]

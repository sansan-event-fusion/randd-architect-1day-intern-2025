ARG PYSETUP_PATH=/opt/pysetup
ARG UV_VERSION=0.7.3
ARG DEBIAN_VERSION=12
ARG DEBIAN_VERSION_CODENAME=bookworm

#############################################
# base ステージ
# ビルダーや開発環境の共通設定
#############################################
FROM ghcr.io/astral-sh/uv:${UV_VERSION}-${DEBIAN_VERSION_CODENAME} AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

#############################################
# 開発用ステージ
# 開発環境を構築する
#############################################
FROM base AS dev
ARG PYSETUP_PATH
ENV UV_PROJECT_ENVIRONMENT=${PYSETUP_PATH}/.venv/
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --dev
CMD [ "uv", "run", "streamlit", "run", "app/main.py" ]

#############################################
# build 用ステージ
# プロジェクトのビルドをする
#############################################
FROM base AS build
ARG PYSETUP_PATH
ENV UV_PROJECT_ENVIRONMENT=${PYSETUP_PATH}/.venv/ \
    UV_PYTHON_INSTALL_DIR=${PYSETUP_PATH}/
WORKDIR ${PYSETUP_PATH}
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-cache-dir --no-dev \
    && rm -rf pyproject.toml uv.lock .python-version

#############################################
# production 用ステージ
# ビルドした依存関係やソースを build ステージからコピーする
#############################################
FROM debian:${DEBIAN_VERSION_CODENAME}-slim AS prod
ARG PYSETUP_PATH
ENV PATH=${PYSETUP_PATH}/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY --from=build ${PYSETUP_PATH}/ ${PYSETUP_PATH}/
COPY app/ app/
COPY .streamlit/ .streamlit/
EXPOSE 8080
WORKDIR /app/app
CMD ["streamlit", "run", "main.py"]

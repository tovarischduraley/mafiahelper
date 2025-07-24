FROM python:3.13-slim AS builder
ENV TZ="Europe/Moscow"
WORKDIR /app

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini entrypoint-bot.sh entrypoint-api.sh pyproject.toml .python-version uv.lock ./

RUN pip install --root-user-action ignore uv
RUN uv sync --no-dev --compile-bytecode
RUN chmod +x entrypoint-bot.sh
RUN chmod +x entrypoint-api.sh

FROM python:3.13-slim AS test
ENV TZ="Europe/Moscow"
WORKDIR /app

COPY src ./src
COPY tests ./tests
COPY pyproject.toml .python-version uv.lock ./

RUN pip install --root-user-action ignore uv
RUN uv sync --compile-bytecode

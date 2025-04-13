FROM python:3.13-alpine as builder
ENV TZ="Europe/Moscow"
ARG APP_DIR=/app
WORKDIR ${APP_DIR}

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini entrypoint-bot.sh entrypoint-api.sh pyproject.toml .python-version uv.lock ./

RUN pip install --root-user-action ignore uv
RUN uv sync --no-dev --compile-bytecode
RUN chmod +x entrypoint-bot.sh
RUN chmod +x entrypoint-api.sh

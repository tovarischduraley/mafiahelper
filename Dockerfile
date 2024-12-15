FROM python:3.13-alpine

ARG APP_DIR=/app
WORKDIR ${APP_DIR}

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini entrypoint.sh pyproject.toml .python-version uv.lock ./

RUN pip install --root-user-action ignore uv
RUN uv sync --no-dev --compile-bytecode

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

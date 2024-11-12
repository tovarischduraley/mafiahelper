FROM python:3.12-alpine

ARG APP_DIR=/app
WORKDIR ${APP_DIR}

COPY requirements.txt .
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

RUN pip install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]

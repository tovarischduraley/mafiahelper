FROM python:3.12-alpine

ARG APP_DIR=/app
WORKDIR ${APP_DIR}

COPY requirements.txt .
COPY src ./src
COPY alembic ./alembic

RUN pip install -r requirements.txt

CMD ["python3", "./main.py"]

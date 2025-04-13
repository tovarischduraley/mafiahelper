#!/bin/sh
uv run alembic upgrade head
cd src
uv run python3 main.py
#!/bin/sh
cd src
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
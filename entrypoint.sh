#!/bin/sh
alembic upgrade head
cd src
python3 main.py
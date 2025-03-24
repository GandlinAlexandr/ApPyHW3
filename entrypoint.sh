#!/bin/sh

echo "Running migrations..."
python -m alembic upgrade head

echo "Starting FastAPI app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
#!/bin/bash
# Azure App Service startup script for FastAPI

echo "Starting Recruiting Agent API..."

# Run migrations
python manage.py migrate --noinput

# Start Gunicorn with Uvicorn workers for FastAPI
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 api.main:app -k uvicorn.workers.UvicornWorker

#!/bin/bash
# Azure App Service startup script for FastAPI

echo "Starting Recruiting Agent API with FastAPI..."

# Change to the correct directory
cd /home/site/wwwroot

# Run migrations using renamed manage script
echo "Running Django migrations..."
python manage_django.py migrate --noinput || echo "Migrations failed or not needed"

# Start Gunicorn with Uvicorn workers for FastAPI
echo "Starting Gunicorn with Uvicorn workers..."
exec gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 --worker-class uvicorn.workers.UvicornWorker api.main:app

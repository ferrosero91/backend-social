#!/bin/bash

# Script de inicio para Azure App Service
# Este script se ejecuta automáticamente al desplegar

echo "=== Iniciando aplicación ==="

# Ejecutar migraciones de Django
echo "Ejecutando migraciones..."
python manage_django.py migrate --noinput

# Recolectar archivos estáticos (si es necesario)
# echo "Recolectando archivos estáticos..."
# python manage_django.py collectstatic --noinput

# Iniciar Gunicorn
echo "Iniciando servidor Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 4 recruiting_agent.wsgi:application

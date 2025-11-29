#!/bin/bash

# Script de pre-inicio para ejecutar migraciones de Django
echo "=== Ejecutando migraciones de Django ==="
python manage_django.py migrate --noinput

echo "=== Migraciones completadas ==="

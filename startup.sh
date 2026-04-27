#!/bin/bash
set -e

echo "=== VetClinic startup ==="
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-NOT SET}"
echo "PORT: ${PORT:-NOT SET}"
echo "DATABASE_URL: ${DATABASE_URL:-NO CONFIGURADO — usando SQLite fallback}"
echo "SECRET_KEY set:   $([ -n "$SECRET_KEY" ] && echo YES || echo 'NO — check Railway variables')"

echo ""
echo "--- Running migrations ---"
python manage.py migrate --noinput

echo ""
echo "--- Starting Gunicorn on 0.0.0.0:${PORT} ---"
exec gunicorn vetclinic.wsgi \
  --bind "0.0.0.0:${PORT}" \
  --workers 1 \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --error-logfile -

#!/bin/bash
set -e

echo "=== VetClinic startup ==="
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-NOT SET}"
echo "PORT: ${PORT:-NOT SET}"
echo "DATABASE_URL: ${DATABASE_URL:-NO CONFIGURADO}"
echo "SECRET_KEY set: $([ -n "$SECRET_KEY" ] && echo YES || echo 'NO — check Railway variables')"

# Abortar si DATABASE_URL apunta a SQLite en runtime (servicios no conectados en Railway)
if [[ "${DATABASE_URL:-}" == sqlite* ]] || [[ -z "${DATABASE_URL:-}" ]]; then
  echo ""
  echo "ERROR: DATABASE_URL no apunta a PostgreSQL."
  echo "En Railway: servicio vetclinic -> Variables -> agrega DATABASE_URL = \${{Postgres.DATABASE_URL}}"
  echo "Asegurate de que la linea entre vetclinic y Postgres sea SOLIDA (no punteada)."
  exit 1
fi

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

#!/bin/bash
set -e

echo "=== VetClinic startup ==="
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-NOT SET}"
echo "PORT: ${PORT:-NOT SET}"
echo "DATABASE: ${DATABASE_URL:-SQLite /tmp/vetclinic.db}"

echo ""
echo "--- Migrations ---"
python manage.py migrate --noinput

echo ""
echo "--- Groups & demo data ---"
python manage.py create_groups
python manage.py seed_demo

echo ""
echo "--- Auth check ---"
python - <<'EOF'
import django, os
django.setup()
from django.contrib.auth import authenticate
ok = authenticate(username="dra.garcia", password="Vet1234!")
if ok:
    print("  Auth OK — dra.garcia puede iniciar sesion")
else:
    print("  ERROR: dra.garcia NO puede autenticarse — revisar seed_demo")
    raise SystemExit(1)
EOF

echo ""
echo "--- Starting Gunicorn on 0.0.0.0:${PORT} ---"
exec gunicorn vetclinic.wsgi \
  --bind "0.0.0.0:${PORT}" \
  --workers 1 \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --error-logfile -

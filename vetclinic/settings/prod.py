import os
import environ
from .base import *  # noqa

env = environ.Env()

DEBUG = False

# ── Database (Railway inyecta DATABASE_URL automáticamente) ──────────────────
# El default SQLite solo se usa durante el build (collectstatic no necesita DB).
# En runtime Railway inyecta el DATABASE_URL real del servicio PostgreSQL.
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:////tmp/vetclinic_build.db")
}

# ── Hosts ────────────────────────────────────────────────────────────────────
# Railway inyecta RAILWAY_PUBLIC_DOMAIN con el dominio asignado al servicio.
# También se puede sobreescribir vía variable ALLOWED_HOSTS.
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)

# CSRF: Django 4.x exige origen explícito para HTTPS
CSRF_TRUSTED_ORIGINS = []
for _h in ALLOWED_HOSTS:
    if not _h.startswith(("localhost", "127.")):
        CSRF_TRUSTED_ORIGINS.append(f"https://{_h}")
if _railway_domain:
    _origin = f"https://{_railway_domain}"
    if _origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_origin)

# ── Archivos estáticos — WhiteNoise ──────────────────────────────────────────
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ── Seguridad HTTPS ──────────────────────────────────────────────────────────
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ── Email (hereda configuración de base.py, solo se redefine FROM) ───────────
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@vetclinic.com")

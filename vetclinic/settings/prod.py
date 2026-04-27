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

# Para demo: acepta cualquier host. En producción real reemplazar con el dominio exacto.
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# CSRF: incluye el dominio Railway y cualquier dominio definido en ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = []
if _railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_domain}")
for _h in env.list("ALLOWED_HOSTS", default=[]):
    if _h not in ("*",) and not _h.startswith(("localhost", "127.")):
        CSRF_TRUSTED_ORIGINS.append(f"https://{_h}")

# ── Archivos estáticos — WhiteNoise ──────────────────────────────────────────
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ── Seguridad HTTPS ──────────────────────────────────────────────────────────
# Railway termina SSL en su proxy y reenvía a Gunicorn como HTTP con este header.
# Sin esto Django entra en loop infinito de redirecciones HTTP→HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ── Email (hereda configuración de base.py, solo se redefine FROM) ───────────
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@vetclinic.com")

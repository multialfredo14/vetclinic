import os
import environ
from .base import *  # noqa

env = environ.Env()

DEBUG = False

# ── Database ─────────────────────────────────────────────────────────────────
# SQLite default solo activo durante el build (collectstatic no usa la BD).
# Railway inyecta el DATABASE_URL real del PostgreSQL en runtime.
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:////tmp/vetclinic_build.db")
}

# ── Hosts ─────────────────────────────────────────────────────────────────────
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

CSRF_TRUSTED_ORIGINS = []
if _railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_domain}")
for _h in env.list("ALLOWED_HOSTS", default=[]):
    if _h not in ("*",) and not _h.startswith(("localhost", "127.")):
        CSRF_TRUSTED_ORIGINS.append(f"https://{_h}")

# ── Archivos estáticos — WhiteNoise ───────────────────────────────────────────
# CompressedStaticFilesStorage: comprime con gzip/brotli pero NO requiere
# manifest estricto, evitando errores 500 si el hash difiere entre builds.
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
WHITENOISE_MANIFEST_STRICT = False

# ── Seguridad HTTPS ───────────────────────────────────────────────────────────
# Railway termina SSL en su proxy y reenvía a Gunicorn como HTTP plano.
# SECURE_PROXY_SSL_HEADER le dice a Django que confíe en el header del proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ── Logging — muestra errores en los logs de Railway ─────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# ── Email ─────────────────────────────────────────────────────────────────────
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@vetclinic.com")

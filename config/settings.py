from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SEGURANÇA / AMBIENTE
# =========================
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-troque-isso-em-producao"
)

DEBUG = os.environ.get("DEBUG", "True") == "True"

# No Render, você pode definir ALLOWED_HOSTS manualmente,
# mas já deixamos valores seguros para localhost e Render.
allowed_hosts_env = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".onrender.com",
]

if allowed_hosts_env:
    ALLOWED_HOSTS += [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]


# Render usa HTTPS em produção
render_external_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
CSRF_TRUSTED_ORIGINS = []

if render_external_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_external_host}")

csrf_env = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if csrf_env:
    CSRF_TRUSTED_ORIGINS += [url.strip() for url in csrf_env.split(",") if url.strip()]


# =========================
# APPS
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "usuarios",
    "dashboard",
    "grupos",
    "membros",
    "frequencias",
    "escolas",
    "relatorios",
]


# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# =========================
# TEMPLATES
# =========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# =========================
# DATABASE
# =========================
# Se DATABASE_URL existir, usa banco externo (PostgreSQL, por exemplo).
# Senão, usa SQLite local.
database_url = os.environ.get("DATABASE_URL")

if database_url:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            database_url,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =========================
# SENHA
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =========================
# INTERNACIONALIZAÇÃO
# =========================
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# =========================
# ARQUIVOS ESTÁTICOS / MEDIA
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================
# MODELO DE USUÁRIO
# =========================
AUTH_USER_MODEL = "usuarios.Usuario"


# =========================
# LOGIN / LOGOUT
# =========================
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "painel_redirect"
LOGOUT_REDIRECT_URL = "login"


# =========================
# DEFAULT
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# SEGURANÇA EM PRODUÇÃO
# =========================
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
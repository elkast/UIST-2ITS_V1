"""
UIST-2ITS - Configuration Django
Prêt pour déploiement sur Render + Neon PostgreSQL
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key-changez-en-production")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
NGROK_URL = os.getenv("NGROK_URL", "https://webbed-ward-subvertically.ngrok-free.dev")

# ALLOWED_HOSTS
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
if NGROK_URL:
    host = NGROK_URL.replace("https://", "")
    ALLOWED_HOSTS.append(host)

# CSRF pour formulaires POST / login / API
CSRF_TRUSTED_ORIGINS = [NGROK_URL]

# Si tu exposes une API pour front-end ou mobile
CORS_ALLOWED_ORIGINS = [NGROK_URL]

# Désactiver la redirection HTTPS pour le développement local
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
USE_X_FORWARDED_HOST = False

# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Tiers
    "widget_tweaks",
    "corsheaders",
    # Applications locales
    "accounts",
    "super_admin",
    "directeur",
    "gestion1",
    "gestion2",
    "gestion3",
    "communication",
    "etudiant",
    "enseignant",
    "parent",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.ForceHTTPMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Base de données - Force SQLite pour développement local
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 6},
    },
]

# Internationalisation
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Fichiers média (bulletins PDF, etc.)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = "accounts.Utilisateur"

# Redirection après connexion/déconnexion
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/login/"
LOGOUT_REDIRECT_URL = "/"

# Clé primaire par défaut
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS (pour API mobile)
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Paramètres académiques
ANNEE_ACADEMIQUE = os.getenv("ANNEE_ACADEMIQUE", "2025-2026")
SEUIL_ABSENCE_CRITIQUE = int(os.getenv("SEUIL_ABSENCE_CRITIQUE", "75"))

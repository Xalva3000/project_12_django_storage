"""
Django settings for storage project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from datetime import date
from pathlib import Path
import environ
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(" ")
INTERNAL_IPS = ["127.0.0.1"]
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS").split(" ")
# SITE_URL = 'storage-monitor.ru'

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "products.apps.ProductsConfig",
    "contractors.apps.ContractorsConfig",
    "contracts.apps.ContractsConfig",
    "storage_items.apps.StorageItemsConfig",
    "users.apps.UsersConfig",
    "debug_toolbar",
    "django_filters",
    'django.contrib.humanize',
    'crispy_forms',
    "crispy_bootstrap4",
    'whitenoise.runserver_nostatic',
    'easyaudit',
    'widget_tweaks',
    'django_celery_beat',
    'django_celery_results',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
]

ROOT_URLCONF = "storage.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / 'templates'
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "users.context_processors.get_menu",
                "users.context_processors.get_last_updates",
            ],
        },
    },
]

WSGI_APPLICATION = "storage.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "ATOMIC_REQUESTS": True,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static/"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = 'products:products'
LOGOUT_REDIRECT_URL = 'users:login'
LOGIN_URL = 'users:login'
PERMISSION_CODE = env('PERMISSION')
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.authentication.EmailAuthBackend',
]


# email settings
EMAIL_BACKEND = "users.backends.email_backend.EmailBackend"
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT_SSL") if EMAIL_USE_SSL else env("EMAIL_PORT_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")


DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER

# AUTH_USER_MODEL = 'users.User' # вместо auth.User
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# HTTPS settings
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
#
# # HSTS settings
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_PRELOAD = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# logging
PATH_TO_LOGS_NT = str(BASE_DIR) + r"\logs\\" + env("DJANGO_LOG_FILE") + f"{date.today()}.log"
PATH_TO_LOG_UBUNTU = str(BASE_DIR) + "/logs/" + env("DJANGO_LOG_FILE") + f"{date.today()}.log"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": PATH_TO_LOGS_NT if os.name == 'nt' else PATH_TO_LOG_UBUNTU,
            "level": env("DJANGO_LOG_LEVEL"),
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": env("DJANGO_LOG_LEVEL"),
            "formatter": "simple",
        },
    },
    "loggers": {
        "": {
            "level": env("DJANGO_LOG_LEVEL"),
            "handlers": ["file", "console"],
            "propagate": False,
        },
    },
    "formatters": {
        "simple": {
            "format": "{asctime}:{levelname} {message}",
            "style":  "{",
        },
        "verbose": {
            "format": "{asctime}:{levelname} = {name} {module}.py (line {lineno:d}). {message}",
            "style": "{",
        }
    }
}
# "redis://" + REDIS_HOST + ":" + REDIS_PORT + "/0"
# REDIS settings
USE_CELERY = int(env("USE_CELERY")) if env("USE_CELERY").isdigit() else 0
REDIS_HOST = "0.0.0.0"
REDIS_PORT = "6379"
CELERY_BROKER_URL = "redis://127.0.0.1:6379" if os.name == 'nt' else "redis://redis:6379/0"
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379" if os.name == 'nt' else "redis://redis:6379/0"
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


CELERY_BEAT_SCHEDULE = {
    'send_db_backup': {
        'task': 'send_db_file',
        'schedule': crontab(hour=3, minute=0),
    },
}
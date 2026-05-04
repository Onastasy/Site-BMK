from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-demo-key-change-me"
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
  "django.contrib.admin",
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.messages",
  "django.contrib.staticfiles",
  "core",
  "news",
  "messaging",
  "accounts",
]

MIDDLEWARE = [
  "django.middleware.security.SecurityMiddleware",
  "django.contrib.sessions.middleware.SessionMiddleware",
  "django.middleware.common.CommonMiddleware",
  "django.middleware.csrf.CsrfViewMiddleware",
  "django.contrib.auth.middleware.AuthenticationMiddleware",
  "django.contrib.messages.middleware.MessageMiddleware",
  "django.middleware.clickjacking.XFrameOptionsMiddleware",
  #"core.middleware.Redirect404Middleware",#
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [{
  "BACKEND": "django.template.backends.django.DjangoTemplates",
  "DIRS": [BASE_DIR / "templates"],
  "APP_DIRS": True,
  "OPTIONS": {
    "context_processors": [
      "django.template.context_processors.request",
      "django.contrib.auth.context_processors.auth",
      "django.template.context_processors.debug",
      "django.template.context_processors.i18n",
      "django.template.context_processors.media",
      "django.template.context_processors.static",
      "django.template.context_processors.tz",
      "django.contrib.messages.context_processors.messages",
      "core.context_processors.site_settings",
      "core.context_processors.breadcrumbs",
    ],
  },
}]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
  {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
  {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
  {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
  {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "profile"
LOGOUT_REDIRECT_URL = "home"

# Настройки для продакшена (Timeweb Cloud)
import os

# Определяем, запущены ли мы на сервере
IS_PRODUCTION = os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings'

if IS_PRODUCTION:
    DEBUG = False
    ALLOWED_HOSTS = [
        'onastasy-site-bmk-91bb.twc1.net',
        'www.onastasy-site-bmk-91bb.twc1.net',
        'localhost',
        '127.0.0.1',
    ]
    CSRF_TRUSTED_ORIGINS = [
        'https://onastasy-site-bmk-91bb.twc1.net',
        'http://onastasy-site-bmk-91bb.twc1.net',
    ]
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    DEBUG = True
    ALLOWED_HOSTS = ['*']

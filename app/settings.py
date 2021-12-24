"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import psycopg2.extensions
import sentry_sdk

# if "/app" in os.environ["HOME"]:
#     import django_heroku

#     django_heroku.settings(locals())


from sentry_sdk.integrations.django import DjangoIntegration
from pathlib import Path
from dotenv import load_dotenv, find_dotenv  # type: ignore

load_dotenv(find_dotenv())


DB_NAME = os.getenv("DB_NAME")
DB_PASSWD = os.getenv("DB_PASSWD")
DB_USER = os.getenv("DB_USER")
HOST = os.getenv("HEROKU_HOST")
DJANGO_SECRET_KEY = os.getenv("SECRET_KEY")

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), integrations=[DjangoIntegration()])

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-397%e+$*49v2nkbs+=zlh2=_5=6aqb8ub+u8eybigo&^7y^ab7",
)
# SECURITY WARNING: don't run with debug turned on in production!
if os.environ.get("ENV") == "PRODUCTION":
    DEBUG = False
    ALLOWED_HOSTS = ["jlord-nursag-p13.herokuapp.com"]
else:
    DEBUG = True
    ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "nursapps.agenda",
    "nursapps.nursauth",
    "nursapps.cabinet",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

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

WSGI_APPLICATION = "app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWD,
        "PORT": "5432",
        "TEST": {
            "NAME": "agenda_test_database",
        },
        "OPTIONS": {
            "isolation_level": psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


AUTHENTICATION_BACKENDS = [
    "nursapps.nursauth.authenticate.EmailAuth",
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "fr-FR"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # prod
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user
AUTH_USER_MODEL = "nursauth.User"

# Redirect to profile URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = "registration/profile.html"

LOGIN_URL = "/auth/accounts/login"

# django_heroku.settings(locals(), test_runner=False)
if "/app" in os.environ["HOME"]:
    import django_heroku

    django_heroku.settings(locals())

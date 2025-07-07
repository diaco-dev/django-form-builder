import os
from datetime import timedelta
from logging import debug
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials


# Load environment variables
load_dotenv()
# Secret keys
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables.")

SECRET_KEY_API = os.getenv("SECRET_KEY_API", "fallback-secret-key")
if not SECRET_KEY_API:
    raise ValueError("SECRET_KEY_API is not set in the environment variables.")


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret-key")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is not set in the environment variables.")


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
#log
from .logging import LOGGING
# Debug mode
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_yasg',
    'django_celery_beat',
    'corsheaders',
    'import_export',
    'auditlog',
    'core',
    'forms',
]

MIDDLEWARE = [
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.logging.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT"),
        'CONN_MAX_AGE': 60,
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=int(os.getenv("ACCESS_TOKEN_LIFETIME", 1))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME", 7))),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("JWT_SIGNING_KEY"),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny'],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_RENDERER_CLASSES': [
        'core.exceptions.CustomJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # anonouse user
        'user': '1000/hour',  # ath user
    },
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}


# Internationalization
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", 'en-us')
TIME_ZONE = os.getenv("TIME_ZONE", 'Asia/Tehran')
USE_I18N = True
USE_TZ = True

# Static and Media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'core.CustomUser'

#redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL"),
        "TIMEOUT": 10 * 60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Celery
CELERY_BROKER_URL = os.getenv("CELERY_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_URL")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = 'Asia/Tehran'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'


#----production
ENVIRONMENT = os.getenv("ENVIRONMENT")


if ENVIRONMENT == "production":
    print(ENVIRONMENT)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    debug = False
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", default='').split(",")
    ALLOWED_EXPORT_IPS = os.environ.get("ALLOWED_EXPORT_HOSTS", default='').split(",")
    CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", default='').split(",")
    ALLOWED_USER = os.environ.get("ALLOWED_USER", default='')

    SECRET_KEY_API = os.getenv("SECRET_KEY_API",default='')

    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ALLOWED_ORIGINS = [
        "https://test.com",
    ]


else:  # development
    print(ENVIRONMENT)
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    ALLOWED_EXPORT_IPS = os.environ.get("ALLOWED_EXPORT_HOSTS", default='').split(",")
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", default='').split(",")
    ALLOWED_USER = os.environ.get("ALLOWED_USER", default='')
    SECRET_KEY_API = os.getenv("SECRET_KEY_API", "fallback-secret-key")
    CORS_ORIGIN_ALLOW_ALL = True
    CSRF_TRUSTED_ORIGINS = [
        "https://test.com",
        "http://localhost",
        "http://127.0.0.1"
    ]
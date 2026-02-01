from .base import *

DEBUG = True

SECRET_KEY = 'django-insecure-l_!4sv+5z%qhzn+1p0%vx98j&efjw^^9yx#ln$@s(4swj=zv_#'

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'arabica_db',
        'USER': 'arabica_user',
        'PASSWORD': 'secure-password',
        'HOST': 'db',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

# Полностью переопределяем CSRF_TRUSTED_ORIGINS для production
CSRF_TRUSTED_ORIGINS = [
    "http://77.95.206.95:8001",
    "http://77.95.206.95",
    "http://62.72.33.230:8001",
    "http://62.72.33.230",
    "http://13.49.241.188",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:3000",
    "http://localhost:5173",
]
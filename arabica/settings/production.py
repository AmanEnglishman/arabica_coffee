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
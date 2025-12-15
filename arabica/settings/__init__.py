import os
from decouple import config

# Читаем DJANGO_ENV из .env файла (по умолчанию 'local')
env = config('DJANGO_ENV', default='local')

# Подключаем соответствующий файл настроек
if env == 'production':
    from .production import *
else:
    from .local import *
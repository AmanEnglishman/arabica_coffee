import os
from pathlib import Path
from decouple import config

# Определяем путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Читаем DJANGO_ENV из .env файла (по умолчанию 'local')
# Явно указываем путь к .env файлу в корне проекта
env = config('DJANGO_ENV', default='local')

# Подключаем соответствующий файл настроек
if env == 'production':
    from .production import *
else:
    from .local import *
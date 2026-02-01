import os
from pathlib import Path
from decouple import config, Config, RepositoryEnv

# Определяем путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Сначала проверяем переменную окружения напрямую (приоритет выше)
env = os.environ.get('DJANGO_ENV', None)

# Если переменная окружения не установлена, ищем .env файл
if env is None:
    # Ищем .env файл в нескольких возможных местах
    # 1. В корне проекта (BASE_DIR)
    # 2. В /src (если проект монтируется в Docker)
    # 3. В текущей рабочей директории
    possible_env_paths = [
        BASE_DIR / '.env',
        Path('/src') / '.env',
        Path('.') / '.env',
    ]

    env = 'local'  # значение по умолчанию
    for env_file in possible_env_paths:
        if env_file.exists():
            try:
                env_config = Config(RepositoryEnv(str(env_file)))
                env = env_config('DJANGO_ENV', default='local')
                break
            except Exception:
                continue

    # Если .env не найден ни в одном месте, пробуем стандартный способ
    if env == 'local':
        try:
            env = config('DJANGO_ENV', default='local')
        except Exception:
            pass

# Подключаем соответствующий файл настроек
if env == 'production':
    from .production import *
else:
    from .local import *
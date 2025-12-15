import random
import string
from datetime import datetime, timedelta
from django.core.cache import cache  # Для хранения кода на время


# Примерная реализация отправки SMS (можно использовать Twilio или любой другой сервис)
def send_sms(phone_number, message):
    # Это просто заглушка для отправки SMS
    print(f"Отправлено сообщение на номер {phone_number}: {message}")


# Генерация 6-значного кода и сохранение его в кеш
def generate_and_send_code(phone_number):
    # Генерация случайного 6-значного кода
    code = ''.join(random.choices(string.digits, k=6))

    # Отправка кода на телефон (можно интегрировать с SMS-платформой)
    message = f"Ваш код подтверждения: {code}"
    send_sms(phone_number, message)

    # Сохраняем код в кеш, например на 10 минут
    cache.set(f"verification_code_{phone_number}", code, timeout=600)

    return code


# Проверка правильности кода
def verify_code(phone_number, code):
    # Проверяем код в кеше
    cached_code = cache.get(f"verification_code_{phone_number}")

    if cached_code is None:
        return False  # Код истек или не был отправлен

    # Сравниваем с введенным кодом
    return cached_code == code

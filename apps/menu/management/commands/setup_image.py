"""
Django management command для настройки изображения larry.jpg.

Использование:
    python manage.py setup_image
"""
import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Копирует larry.jpg в media/products/ если он находится в корне проекта'

    def handle(self, *args, **options):
        # Путь к файлу в корне проекта
        root_file = Path(settings.BASE_DIR) / 'larry.jpg'
        
        # Путь к директории media/products
        media_products_dir = Path(settings.MEDIA_ROOT) / 'products'
        media_file = media_products_dir / 'larry.jpg'
        
        # Создаем директорию если её нет
        media_products_dir.mkdir(parents=True, exist_ok=True)
        
        # Копируем файл если он существует в корне
        if root_file.exists():
            shutil.copy2(root_file, media_file)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Файл скопирован из {root_file} в {media_file}'
                )
            )
        elif media_file.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Файл уже существует: {media_file}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠ Файл larry.jpg не найден ни в корне проекта, ни в {media_file}'
                )
            )
            self.stdout.write(
                f'Пожалуйста, скопируйте файл larry.jpg в {media_products_dir}'
            )

"""
Django management command для обновления изображений всех продуктов.

Использование:
    python manage.py update_product_images
    python manage.py update_product_images --image products/larry.jpg
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.menu.models import Product


class Command(BaseCommand):
    help = 'Обновляет изображения для всех продуктов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--image',
            type=str,
            default='products/larry.jpg',
            help='Путь к изображению (по умолчанию: products/larry.jpg)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        image_path = options.get('image', 'products/larry.jpg')
        
        products = Product.objects.all()
        total = products.count()
        updated = 0
        
        self.stdout.write(f"Обновление изображений для {total} продуктов...")
        self.stdout.write(f"Используется изображение: {image_path}")
        
        for product in products:
            product.image = image_path
            product.save()
            updated += 1
            self.stdout.write(f"  ✓ Обновлен продукт: {product.title}")
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Обновлено продуктов: {updated} из {total}"))
        self.stdout.write("="*50)

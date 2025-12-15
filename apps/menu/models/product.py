from django.db import models

from apps.menu.models.category import Subcategory


class Product(models.Model):
    title = models.CharField(
        'Название',
        max_length=100, )
    price = models.PositiveIntegerField(
        'Цена',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='products/',
        blank=True,
        null=True
    )
    bonus_percent = models.FloatField(
        'Проценты для бонуса',
        default=5.0
    )
    description = models.TextField(
        'Описание',
    )
    subcategory = models.ForeignKey(
        verbose_name='Субкатегория',
        to=Subcategory,
        related_name='products',
        on_delete=models.CASCADE
    )
    has_options = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

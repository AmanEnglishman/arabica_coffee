from django.db import models

class Category(models.Model):
    """
    Основная категория: 'Напитки', 'Еда'
    """
    title = models.CharField(
        verbose_name='Название',
        max_length=100,
    )

    def __str__(self):
        return self.title

class Subcategory(models.Model):
    """
    Подкатегория: 'Кофе', 'Чай', 'Ice кофе', и т.д.
    """
    title = models.CharField(
        verbose_name='Название',
        max_length=100,)
    category = models.ForeignKey(
        verbose_name='Название',
        to=Category,
        related_name='subcategories',
        on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category.title} - {self.title}"

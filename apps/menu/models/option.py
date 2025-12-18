from django.db import models

from apps.menu.models import Product


class OptionType(models.Model):
    """Тип опции"""

    title = models.CharField("Тип опции", max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тип опции"
        verbose_name_plural = "Тип опции"


class OptionValue(models.Model):
    """Значение опции"""

    type = models.ForeignKey(
        OptionType,
        verbose_name="Тип опции",
        related_name="values",
        on_delete=models.CASCADE,
    )
    value = models.CharField("Значение", max_length=100)
    additional_cost = models.PositiveIntegerField(
        "Дополнительная стоимость",
        default=0,
        help_text="Сколько добавляется к базовой цене товара при выборе этой опции",
    )

    def __str__(self):
        return f"{self.type.title}: {self.value}"

    class Meta:
        verbose_name = "Значение опции"
        verbose_name_plural = "Значение опции"


class ProductOptionType(models.Model):
    """Опции конкретно к продукту"""

    product = models.ForeignKey(
        Product,
        related_name="option_types",
        on_delete=models.CASCADE,
    )
    option_type = models.ForeignKey(
        OptionType,
        on_delete=models.CASCADE,
        related_name="product_links",
    )

    class Meta:
        unique_together = ("product", "option_type")
        verbose_name = "Опции конкретно к продукту"
        verbose_name_plural = "Опции конкретно к продукту"

    def __str__(self):
        return f"{self.product.title} - {self.option_type.title}"

from django.db import models
from django.contrib.auth import get_user_model
from apps.menu.models.product import Product

User = get_user_model()


class Order(models.Model):
    ORDER_STATUS = [
        ("accepted", "Ваш заказ принят"),
        ("ready", "Заказ готов"),
        ("on_the_way", "Курьер в пути"),
        ("delivered", "Заказ доставлен"),
    ]

    DELIVERY_TYPE_CHOICES = [
        ("delivery", "Доставка"),
        ("pickup", "Самовывоз"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default="accepted")
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPE_CHOICES)
    address = models.TextField(blank=True, null=True)  # Только для доставки
    delivery_time = models.TimeField(blank=True, null=True)  # Время доставки
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Итоговая цена
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} ({self.user.phone_number})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Продукт
    quantity = models.IntegerField(default=1)
    product_options = models.JSONField(default=dict, blank=True)  # Информация о выбранных опциях
    final_price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена за всю позицию (кол-во * цена)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} ({self.order.id})"

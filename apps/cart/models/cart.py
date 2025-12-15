from django.db import models
from apps.users.models.user import User
from apps.menu.models.product import Product
from apps.menu.models.option import OptionValue


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Корзина пользователя {self.user.first_name} - {self.user.phone_number}"

    def get_total_price(self):
        """Возвращает полную стоимость всех товаров в корзине."""
        return sum(item.get_total_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)  # Комментарии к товару

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    def get_total_price(self):
        """Возвращает общую стоимость данной позиции в корзине."""
        base_price = self.product.price

        # Суммируем стоимость всех опций
        additional_price = sum(option.get_additional_price() for option in self.options.all())
        return (base_price + additional_price) * self.quantity


class CartItemOption(models.Model):
    """Связь между CartItem и выбранными опциями."""
    cart_item = models.ForeignKey(CartItem, related_name="options", on_delete=models.CASCADE)
    option_value = models.ForeignKey(OptionValue, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cart_item.product.title} - {self.option_value}"

    def get_additional_price(self):
        # Учитывайте правила ценообразования, если некоторые опции увеличивают стоимость
        # Например, у вас может быть поле в модели OptionValue `additional_cost`
        return getattr(self.option_value, "additional_cost", 0)

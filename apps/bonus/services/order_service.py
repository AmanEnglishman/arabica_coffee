from apps.cart.models import Cart
from apps.menu.models.product import Product

class OrderService:
    """Сервис для обработки заказов и бонусной системы."""

    def handle_order(self, user):
        """
        Обработать заказ: начислить бонусные баллы и обновить программу кофе.
        Передаётся user (модель текущего пользователя).
        """
        cart = Cart.objects.get(user=user)

        total_loyalty_points = 0
        for item in cart.items.all():  # cart.items привязаны через foreign key
            product = item.product  # Продукт в корзине

            # Начисляем бонусы
            total_loyalty_points += (product.price * product.bonus_percent) / 100

        # Обновляем лояльность пользователя
        user.loyalty_points += int(total_loyalty_points)  # Округляем баллы
        user.save()

        # Очищаем корзину после оформления заказа
        cart.items.all().delete()
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.cart.models import Cart, CartItem
from apps.cart.api.serializers.cart import (
    CartSerializer,
    CartItemSerializer,
    CartItemOptionSerializer,
    OptionValueSerializer,

)
from apps.cart.models.cart import CartItemOption
from apps.menu.models import OptionValue
from apps.menu.models.product import Product

from django.core.cache import cache


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получить корзину текущего пользователя."""
        user_id = request.user.id  # Уникальный идентификатор пользователя
        cache_key = f"user_cart_{user_id}"  # Уникальный ключ кэша
        cache_time = 60 * 5  # Время жизни кэша (5 минут)

        # Проверяем, есть ли данные в кэше
        cart_data = cache.get(cache_key)
        if cart_data:
            return Response(cart_data, status=status.HTTP_200_OK)

        # Если данных в кэше нет, получить корзину из базы
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)

        # Сохраняем результат в кэше и возвращаем клиенту
        cache.set(cache_key, serializer.data, cache_time)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Добавить товар в корзину, включая опции."""
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)
        options = request.data.get("options", [])  # Список IDs OptionValue
        comment = request.data.get("comment", "")

        if not product_id:
            return Response({"error": "Не указан ID продукта."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
            cart, _ = Cart.objects.get_or_create(user=request.user)

            # Создаем позицию в корзине
            cart_item = CartItem.objects.create(
                cart=cart, product=product, quantity=quantity, comment=comment
            )

            # Добавляем опции
            for option_id in options:
                option_value = OptionValue.objects.get(id=option_id)
                CartItemOption.objects.create(cart_item=cart_item, option_value=option_value)

            # Очистка кэша для актуализации данных
            cache.delete(f"user_cart_{request.user.id}")

            return Response({"message": "Товар успешно добавлен в корзину!"}, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({"error": "Продукт с указанным ID не найден."}, status=status.HTTP_404_NOT_FOUND)
        except OptionValue.DoesNotExist:
            return Response({"error": "Одна или несколько указанных опций не найдены."}, status=status.HTTP_404_NOT_FOUND)

class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """Обновить количество и комментарий для позиции в корзине."""
        try:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item = get_object_or_404(CartItem, id=pk, cart=cart)

            quantity = request.data.get("quantity", cart_item.quantity)
            comment = request.data.get("comment", cart_item.comment)

            if quantity < 1:
                return Response(
                    {"error": "Количество товара не может быть меньше одного."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Обновляем данные
            cart_item.quantity = quantity
            cart_item.comment = comment
            cart_item.save()

            # Очистка кэша
            cache.delete(f"user_cart_{request.user.id}")

            return Response({"message": "Позиция успешно обновлена."}, status=status.HTTP_200_OK)

        except CartItem.DoesNotExist:
            return Response({"error": "Позиция в корзине не найдена."}, status=status.HTTP_404_NOT_FOUND)


class DeleteCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        """Удалить товар из корзины."""
        try:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item = get_object_or_404(CartItem, id=pk, cart=cart)

            # Удаляем позицию
            cart_item.delete()

            # Очистка кэша
            cache.delete(f"user_cart_{request.user.id}")

            return Response({"message": "Позиция успешно удалена."}, status=status.HTTP_204_NO_CONTENT)

        except CartItem.DoesNotExist:
            return Response({"error": "Позиция в корзине не найдена."}, status=status.HTTP_404_NOT_FOUND)
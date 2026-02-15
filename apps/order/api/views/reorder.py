from django.core.cache import cache
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.models import Cart, CartItem, CartItemOption
from apps.menu.models import OptionValue
from apps.order.models.code import Order
from apps.cart.api.serializers.cart import CartSerializer


@extend_schema(
    summary="Повторить заказ - добавить товары из заказа в корзину",
    tags=["Order"],
    responses={
        200: OpenApiResponse(
            description="Товары из заказа успешно добавлены в корзину",
            response=CartSerializer
        ),
        403: OpenApiResponse(description="Нет прав доступа"),
        404: OpenApiResponse(description="Заказ не найден"),
    }
)
class ReorderView(APIView):
    """
    API endpoint для повторного заказа.
    
    Добавляет все товары из указанного заказа в корзину пользователя.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        """
        Повторяет заказ, добавляя все товары из заказа в корзину.
        
        Args:
            order_id: ID заказа для повторения
        """
        # Получаем заказ (только заказы текущего пользователя)
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Получаем или создаем корзину пользователя
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        added_items = []
        errors = []
        
        # Добавляем товары из заказа в корзину
        for order_item in order.items.all():
            try:
                # Проверяем, существует ли продукт и активен ли он
                if not order_item.product.is_active:
                    errors.append(f"Продукт '{order_item.product.title}' больше не доступен")
                    continue
                
                # Извлекаем опции из product_options JSON
                option_ids = []
                if order_item.product_options and 'options' in order_item.product_options:
                    for opt in order_item.product_options['options']:
                        if isinstance(opt, dict) and 'id' in opt:
                            option_ids.append(opt['id'])
                
                # Создаем позицию в корзине
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=order_item.product,
                    quantity=order_item.quantity,
                    comment=""
                )
                
                # Добавляем опции, если они были в заказе
                for option_id in option_ids:
                    try:
                        option_value = OptionValue.objects.get(id=option_id)
                        CartItemOption.objects.create(
                            cart_item=cart_item,
                            option_value=option_value
                        )
                    except OptionValue.DoesNotExist:
                        # Опция больше не существует, пропускаем
                        pass
                
                added_items.append({
                    "product": order_item.product.title,
                    "quantity": order_item.quantity
                })
                
            except Exception as e:
                errors.append(f"Ошибка при добавлении '{order_item.product.title}': {str(e)}")
        
        # Очищаем кэш корзины
        cache.delete(f"user_cart_{request.user.id}")
        
        # Получаем обновленную корзину
        cart.refresh_from_db()
        cart_serializer = CartSerializer(cart)
        
        response_data = {
            "message": "Товары из заказа успешно добавлены в корзину",
            "cart": cart_serializer.data,
            "added_items": added_items
        }
        
        if errors:
            response_data["warnings"] = errors
        
        return Response(response_data, status=status.HTTP_200_OK)

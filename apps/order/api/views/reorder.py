from decimal import Decimal

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.api.serializers.cart import CartSerializer
from apps.cart.models import Cart, CartItem, CartItemOption
from apps.menu.models import OptionValue
from apps.order.models.code import Order


@extend_schema(
    summary="Повторить заказ",
    tags=["Order"],
    responses={
        200: OpenApiResponse(description="Товары добавлены в корзину"),
        404: OpenApiResponse(description="Заказ не найден"),
    },
    description=(
        "Добавляет все активные товары из заказа в текущую корзину. "
        "Недоступные товары пропускаются с предупреждением. "
        "Если цена товара изменилась — возвращается предупреждение."
    ),
)
class ReorderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        added   = []
        warnings = []

        for order_item in order.items.select_related("product").prefetch_related("product__options").all():
            product = order_item.product

            if not product.is_active:
                warnings.append(f"«{product.title}» больше недоступен — пропущен.")
                continue

            # Проверяем изменение цены
            original_unit_price = (
                Decimal(str(order_item.final_price)) / order_item.quantity
                if order_item.quantity else Decimal("0")
            )
            if product.price != original_unit_price:
                warnings.append(
                    f"«{product.title}»: цена изменилась с {original_unit_price:.2f} на {product.price:.2f} сом."
                )

            # Восстанавливаем опции
            option_ids = [
                opt["id"]
                for opt in (order_item.product_options.get("options") or [])
                if isinstance(opt, dict) and "id" in opt
            ]
            valid_options = list(
                OptionValue.objects.filter(
                    id__in=option_ids,
                    type__product_links__product=product,
                ).distinct()
            ) if option_ids else []

            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=order_item.quantity,
                comment=order_item.product_options.get("comment", ""),
            )
            for opt in valid_options:
                CartItemOption.objects.create(cart_item=cart_item, option_value=opt)

            added.append({"product": product.title, "quantity": order_item.quantity})

        cache.delete(f"user_cart_{request.user.id}")

        response = {
            "message": "Товары добавлены в корзину.",
            "cart":    CartSerializer(cart).data,
            "added":   added,
        }
        if warnings:
            response["warnings"] = warnings

        return Response(response, status=status.HTTP_200_OK)

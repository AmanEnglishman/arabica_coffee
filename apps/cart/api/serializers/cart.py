from rest_framework import serializers
from apps.cart.models import Cart, CartItem, CartItemOption
from apps.menu.models.option import OptionValue


class AddCartItemRequestSerializer(serializers.Serializer):
    """Payload for adding item to cart."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    options = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True, default=list
    )
    comment = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )


class UpdateCartItemRequestSerializer(serializers.Serializer):
    """Payload for updating cart item."""

    quantity = serializers.IntegerField(min_value=1, required=False)
    comment = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )


class OptionValueSerializer(serializers.ModelSerializer):
    """Сериализация значений опций."""
    class Meta:
        model = OptionValue
        fields = ["id", "type", "value"]


class CartItemOptionSerializer(serializers.ModelSerializer):
    """Сериализация опций для позиции в корзине."""
    option_value = OptionValueSerializer()

    class Meta:
        model = CartItemOption
        fields = ["id", "option_value"]


class CartItemSerializer(serializers.ModelSerializer):
    """Сериализация элемента корзины с опциями."""
    options = CartItemOptionSerializer(source="options.all", many=True, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "comment", "options", "get_total_price"]


class CartSerializer(serializers.ModelSerializer):
    """Сериализация корзины."""
    items = CartItemSerializer(source="items.all", many=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "get_total_price"]
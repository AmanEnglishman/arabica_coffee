from rest_framework import serializers
from apps.cart.models import Cart, CartItem, CartItemOption
from apps.menu.models.option import OptionValue


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
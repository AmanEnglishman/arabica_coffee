from rest_framework import serializers


class AdditionalItemSerializer(serializers.Serializer):
    """Сериализатор для дополнительного товара при повторном заказе."""
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(min_value=1, default=1, required=False)
    options = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=500
    )


class ReorderSerializer(serializers.Serializer):
    """
    Сериализатор для повторного заказа.
    Позволяет добавить дополнительные товары к повторному заказу.
    """
    additional_items = AdditionalItemSerializer(
        many=True,
        required=False,
        allow_empty=True,
        help_text="Список дополнительных товаров для добавления в корзину"
    )

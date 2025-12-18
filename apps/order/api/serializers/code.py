from rest_framework import serializers
from apps.order.models.code import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "quantity",
            "product_options",
            "final_price",
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "delivery_type",
            "address",
            "delivery_time",
            "total_price",
            "created_at",
            "items",
        )

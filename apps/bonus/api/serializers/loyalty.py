from rest_framework import serializers


class AddLoyaltyPointsResponseSerializer(serializers.Serializer):
    message              = serializers.CharField()
    total_loyalty_points = serializers.IntegerField()


class AddCoffeeCupResponseSerializer(serializers.Serializer):
    message             = serializers.CharField()
    current_coffee_cups = serializers.IntegerField()


class SpendLoyaltyPointsSerializer(serializers.Serializer):
    points = serializers.IntegerField(
        min_value=1,
        help_text="Количество баллов для списания (1 балл = 1 сом).",
    )


class SpendLoyaltyPointsResponseSerializer(serializers.Serializer):
    message           = serializers.CharField()
    spent_points      = serializers.IntegerField()
    remaining_points  = serializers.IntegerField()


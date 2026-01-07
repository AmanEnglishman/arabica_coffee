from rest_framework import serializers

class AddLoyaltyPointsResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    total_loyalty_points = serializers.IntegerField()

class AddCoffeeCupResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    current_coffee_cups = serializers.IntegerField()


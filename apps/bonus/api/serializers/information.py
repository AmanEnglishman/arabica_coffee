from rest_framework import serializers

from apps.users.models import User


class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('loyalty_points', 'coffee_cups')
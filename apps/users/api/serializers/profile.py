# Сериализатор для профиля
from rest_framework import serializers

from apps.users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'gender', 'birth_date', 'avatar')

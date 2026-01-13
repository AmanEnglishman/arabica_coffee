from rest_framework import serializers
from apps.promotions.models import Promotion


class PromotionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ["id", "title", "image", "short_description", "published_at"]


class PromotionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "image",
            "short_description",
            "content",
            "published_at",
            "created_at",
        ]
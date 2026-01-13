from rest_framework import serializers
from apps.news.models import News


class NewsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["id", "title", "image", "short_description", "published_at"]


class NewsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "image",
            "short_description",
            "content",
            "published_at",
            "created_at",
        ]
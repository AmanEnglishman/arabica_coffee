from rest_framework import serializers
from apps.promotions.models import Promotion


class PromotionListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Promotion
        fields = ["id", "title", "image", "short_description", "published_at"]
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class PromotionDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
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
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
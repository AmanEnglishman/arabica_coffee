from rest_framework import serializers

from apps.menu.models import Product
from apps.menu.models.option import OptionType, OptionValue, ProductOptionType


class OptionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionValue
        fields = ("id", "value", "additional_cost")


class OptionTypeSerializer(serializers.ModelSerializer):
    values = OptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = OptionType
        fields = ("id", "title", "values")


class ProductOptionTypeSerializer(serializers.ModelSerializer):
    option_type = OptionTypeSerializer(read_only=True)

    class Meta:
        model = ProductOptionType
        fields = ("id", "option_type")


class ProductSerializer(serializers.ModelSerializer):
    option_types = ProductOptionTypeSerializer(
        many=True,
        read_only=True,
    )
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "price",
            "image",
            "description",
            "has_options",
            "option_types",
        )
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductSearchSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ("id", "title", "price", "image")
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
from rest_framework import serializers
from apps.menu.models import Category, Subcategory, Product
from apps.menu.models.option import OptionType, OptionValue, ProductOptionType


class OptionValueImportSerializer(serializers.Serializer):
    """Сериализатор для импорта значений опций"""
    value = serializers.CharField(max_length=100)
    additional_cost = serializers.IntegerField(default=0, min_value=0)


class OptionTypeImportSerializer(serializers.Serializer):
    """Сериализатор для импорта типов опций"""
    title = serializers.CharField(max_length=100)
    values = OptionValueImportSerializer(many=True)


class ProductImportSerializer(serializers.Serializer):
    """Сериализатор для импорта продуктов"""
    title = serializers.CharField(max_length=100)
    price = serializers.IntegerField(min_value=0)
    description = serializers.CharField()
    bonus_percent = serializers.FloatField(default=5.0, min_value=0)
    has_options = serializers.BooleanField(default=False)
    option_type_titles = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="Список названий типов опций, которые должны быть связаны с продуктом"
    )
    image = serializers.CharField(required=False, allow_blank=True)


class SubcategoryImportSerializer(serializers.Serializer):
    """Сериализатор для импорта подкатегорий"""
    title = serializers.CharField(max_length=100)
    products = ProductImportSerializer(many=True)


class CategoryImportSerializer(serializers.Serializer):
    """Сериализатор для импорта категорий"""
    title = serializers.CharField(max_length=100)
    subcategories = SubcategoryImportSerializer(many=True)


class BulkImportSerializer(serializers.Serializer):
    """Сериализатор для массового импорта"""
    categories = CategoryImportSerializer(many=True)
    option_types = OptionTypeImportSerializer(many=True, required=False)

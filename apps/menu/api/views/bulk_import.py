from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.db import transaction

from apps.menu.models import Category, Subcategory, Product
from apps.menu.models.option import OptionType, OptionValue, ProductOptionType
from apps.menu.api.serializers.bulk_import import BulkImportSerializer


@extend_schema(
    summary="Массовый импорт продуктов с категориями и опциями",
    tags=["Menu"],
    request=BulkImportSerializer,
    responses={
        201: OpenApiResponse(
            description="Продукты успешно импортированы",
            response={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "created": {
                        "type": "object",
                        "properties": {
                            "categories": {"type": "integer"},
                            "subcategories": {"type": "integer"},
                            "products": {"type": "integer"},
                            "option_types": {"type": "integer"},
                            "option_values": {"type": "integer"},
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description="Ошибка валидации данных"),
    }
)
class BulkImportView(APIView):
    """
    API endpoint для массового импорта продуктов, категорий и опций.
    
    Формат данных:
    {
        "categories": [
            {
                "title": "Напитки",
                "subcategories": [
                    {
                        "title": "Кофе",
                        "products": [
                            {
                                "title": "Эспрессо",
                                "price": 120,
                                "description": "Крепкий кофе",
                                "bonus_percent": 5.0,
                                "has_options": true,
                                "option_type_titles": ["Объем", "Вид молока"]
                            }
                        ]
                    }
                ]
            }
        ],
        "option_types": [
            {
                "title": "Объем",
                "values": [
                    {"value": "200 мл", "additional_cost": 0},
                    {"value": "300 мл", "additional_cost": 20}
                ]
            }
        ]
    }
    """
    permission_classes = [IsAdminUser]

    @transaction.atomic
    def post(self, request):
        serializer = BulkImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_counts = {
            "categories": 0,
            "subcategories": 0,
            "products": 0,
            "option_types": 0,
            "option_values": 0,
        }

        # Создаем типы опций и их значения
        option_types_map = {}
        if "option_types" in serializer.validated_data:
            for opt_type_data in serializer.validated_data["option_types"]:
                option_type, created = OptionType.objects.get_or_create(
                    title=opt_type_data["title"]
                )
                if created:
                    created_counts["option_types"] += 1
                option_types_map[option_type.title] = option_type

                # Создаем значения опций
                for value_data in opt_type_data["values"]:
                    option_value, created = OptionValue.objects.get_or_create(
                        type=option_type,
                        value=value_data["value"],
                        defaults={"additional_cost": value_data.get("additional_cost", 0)}
                    )
                    if created:
                        created_counts["option_values"] += 1

        # Создаем категории, подкатегории и продукты
        for category_data in serializer.validated_data["categories"]:
            category, created = Category.objects.get_or_create(
                title=category_data["title"]
            )
            if created:
                created_counts["categories"] += 1

            for subcategory_data in category_data["subcategories"]:
                subcategory, created = Subcategory.objects.get_or_create(
                    title=subcategory_data["title"],
                    category=category
                )
                if created:
                    created_counts["subcategories"] += 1

                for product_data in subcategory_data["products"]:
                    product, created = Product.objects.get_or_create(
                        title=product_data["title"],
                        subcategory=subcategory,
                        defaults={
                            "price": product_data["price"],
                            "description": product_data["description"],
                            "bonus_percent": product_data.get("bonus_percent", 5.0),
                            "has_options": product_data.get("has_options", False),
                            "is_active": True,
                        }
                    )
                    if created:
                        created_counts["products"] += 1
                    else:
                        # Обновляем существующий продукт
                        product.price = product_data["price"]
                        product.description = product_data["description"]
                        product.bonus_percent = product_data.get("bonus_percent", 5.0)
                        product.has_options = product_data.get("has_options", False)
                        product.save()

                    # Связываем опции с продуктом, если указаны
                    if product_data.get("has_options") and product_data.get("option_type_titles"):
                        for option_type_title in product_data["option_type_titles"]:
                            if option_type_title in option_types_map:
                                ProductOptionType.objects.get_or_create(
                                    product=product,
                                    option_type=option_types_map[option_type_title]
                                )

        return Response(
            {
                "message": "Продукты успешно импортированы",
                "created": created_counts
            },
            status=status.HTTP_201_CREATED
        )

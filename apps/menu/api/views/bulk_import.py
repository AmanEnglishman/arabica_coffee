from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.menu.api.serializers.bulk_import import BulkImportSerializer
from apps.menu.models import Category, Subcategory, Product
from apps.menu.models.option import OptionType, OptionValue, ProductOptionType


@extend_schema(
    summary="Массовый импорт меню",
    tags=["Menu"],
    request=BulkImportSerializer,
    responses={
        200: OpenApiResponse(description="Результаты импорта с подробной статистикой"),
        400: OpenApiResponse(description="Ошибка структуры данных"),
    },
    description=(
        "Импортирует категории, подкатегории, продукты и опции. "
        "Каждая позиция обрабатывается независимо — при ошибке в одной строке "
        "остальные сохраняются. Ответ содержит счётчики и список ошибок."
    ),
)
class BulkImportView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = BulkImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        counts = {
            "categories": 0, "subcategories": 0,
            "products": 0, "option_types": 0, "option_values": 0,
        }
        errors = []

        # ── Option types ───────────────────────────────────────
        option_types_map: dict[str, OptionType] = {}
        for opt_type_data in data.get("option_types", []):
            try:
                with transaction.atomic():
                    opt_type, created = OptionType.objects.get_or_create(
                        title=opt_type_data["title"]
                    )
                    if created:
                        counts["option_types"] += 1
                    option_types_map[opt_type.title] = opt_type

                    for val_data in opt_type_data.get("values", []):
                        _, val_created = OptionValue.objects.get_or_create(
                            type=opt_type,
                            value=val_data["value"],
                            defaults={"additional_cost": val_data.get("additional_cost", 0)},
                        )
                        if val_created:
                            counts["option_values"] += 1
            except Exception as exc:
                errors.append({
                    "type": "option_type",
                    "title": opt_type_data.get("title", "?"),
                    "error": str(exc),
                })

        # ── Categories / subcategories / products ──────────────
        for cat_data in data.get("categories", []):
            cat_title = cat_data.get("title", "?")
            try:
                with transaction.atomic():
                    category, created = Category.objects.get_or_create(title=cat_title)
                    if created:
                        counts["categories"] += 1
            except Exception as exc:
                errors.append({"type": "category", "title": cat_title, "error": str(exc)})
                continue

            for sub_data in cat_data.get("subcategories", []):
                sub_title = sub_data.get("title", "?")
                try:
                    with transaction.atomic():
                        subcategory, created = Subcategory.objects.get_or_create(
                            title=sub_title, category=category
                        )
                        if created:
                            counts["subcategories"] += 1
                except Exception as exc:
                    errors.append({
                        "type": "subcategory", "title": sub_title,
                        "category": cat_title, "error": str(exc),
                    })
                    continue

                for prod_data in sub_data.get("products", []):
                    prod_title = prod_data.get("title", "?")
                    try:
                        with transaction.atomic():
                            product, created = Product.objects.get_or_create(
                                title=prod_title,
                                subcategory=subcategory,
                                defaults={
                                    "price":        prod_data["price"],
                                    "description":  prod_data.get("description", ""),
                                    "bonus_percent": prod_data.get("bonus_percent", 5.0),
                                    "has_options":  prod_data.get("has_options", False),
                                    "is_active":    True,
                                },
                            )
                            if created:
                                counts["products"] += 1
                            else:
                                # Обновляем поля существующего продукта
                                product.price        = prod_data["price"]
                                product.description  = prod_data.get("description", product.description)
                                product.bonus_percent = prod_data.get("bonus_percent", product.bonus_percent)
                                product.has_options  = prod_data.get("has_options", product.has_options)
                                product.save(update_fields=[
                                    "price", "description", "bonus_percent", "has_options"
                                ])

                            # Привязываем опции
                            if product.has_options:
                                for opt_title in prod_data.get("option_type_titles", []):
                                    if opt_title in option_types_map:
                                        ProductOptionType.objects.get_or_create(
                                            product=product,
                                            option_type=option_types_map[opt_title],
                                        )
                                    else:
                                        errors.append({
                                            "type": "product_option",
                                            "product": prod_title,
                                            "error": f"Тип опции «{opt_title}» не найден в option_types.",
                                        })
                    except Exception as exc:
                        errors.append({
                            "type": "product", "title": prod_title,
                            "subcategory": sub_title, "error": str(exc),
                        })

        response_status = status.HTTP_200_OK if errors else status.HTTP_201_CREATED
        return Response(
            {
                "message": "Импорт завершён." if not errors else "Импорт завершён с ошибками.",
                "created": counts,
                "errors":  errors,
                "errors_count": len(errors),
            },
            status=response_status,
        )

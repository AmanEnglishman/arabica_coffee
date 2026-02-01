"""
Скрипт для импорта продуктов через Django shell.

Использование:
    python manage.py shell
    >>> exec(open('apps/menu/fixtures/import_products_script.py').read())
    
Или напрямую:
    python manage.py import_products
"""

from django.db import transaction
from apps.menu.models import Category, Subcategory, Product
from apps.menu.models.option import OptionType, OptionValue, ProductOptionType

# Данные для импорта
PRODUCTS_DATA = {
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
                            "has_options": True,
                            "option_type_titles": ["Объем", "Вид молока", "Уровень сладости"]
                        },
                        {
                            "title": "Американо",
                            "price": 150,
                            "description": "Кофе с водой",
                            "bonus_percent": 5.0,
                            "has_options": True,
                            "option_type_titles": ["Объем", "Вид молока", "Уровень сладости"]
                        },
                        {
                            "title": "Капучино",
                            "price": 180,
                            "description": "Кофе с молоком",
                            "bonus_percent": 5.0,
                            "has_options": True,
                            "option_type_titles": ["Объем", "Вид молока", "Уровень сладости"]
                        },
                        {
                            "title": "Латте",
                            "price": 200,
                            "description": "Кофе с большим количеством молока",
                            "bonus_percent": 5.0,
                            "has_options": True,
                            "option_type_titles": ["Объем", "Вид молока", "Уровень сладости"]
                        },
                        {
                            "title": "Мокка",
                            "price": 220,
                            "description": "Кофе с шоколадом",
                            "bonus_percent": 5.0,
                            "has_options": True,
                            "option_type_titles": ["Объем", "Вид молока", "Уровень сладости"]
                        },
                    ]
                },
                {
                    "title": "Холодное",
                    "products": [
                        {
                            "title": "Мохито",
                            "price": 250,
                            "description": "Освежающий напиток с мятой",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Лимонад",
                            "price": 180,
                            "description": "Лимонный напиток",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Фраппе",
                            "price": 220,
                            "description": "Холодный кофе",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Милкшейк",
                            "price": 200,
                            "description": "Молочный коктейль",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                    ]
                }
            ]
        },
        {
            "title": "Еда",
            "subcategories": [
                {
                    "title": "Выпечка",
                    "products": [
                        {
                            "title": "Круассан",
                            "price": 150,
                            "description": "Слоёная выпечка",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Пончик",
                            "price": 120,
                            "description": "Сладкая выпечка",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Маффин",
                            "price": 130,
                            "description": "Шоколадный маффин",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Пирог с яблоками",
                            "price": 200,
                            "description": "Домашний пирог",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Хачапури",
                            "price": 250,
                            "description": "Сырная выпечка",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                    ]
                },
                {
                    "title": "Завтрак",
                    "products": [
                        {
                            "title": "Омлет",
                            "price": 180,
                            "description": "Яичный омлет",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Блины",
                            "price": 150,
                            "description": "Блины с медом",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Каша овсяная",
                            "price": 120,
                            "description": "Овсянка на молоке",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Тост с авокадо",
                            "price": 200,
                            "description": "Хлеб, авокадо",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
                        {
                            "title": "Йогурт с фруктами",
                            "price": 170,
                            "description": "Йогурт и фрукты",
                            "bonus_percent": 5.0,
                            "has_options": False
                        },
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
                {"value": "300 мл", "additional_cost": 20},
                {"value": "400 мл", "additional_cost": 40}
            ]
        },
        {
            "title": "Вид молока",
            "values": [
                {"value": "Обычное", "additional_cost": 0},
                {"value": "Безлактозное", "additional_cost": 30},
                {"value": "Соевое", "additional_cost": 25},
                {"value": "Миндальное", "additional_cost": 35}
            ]
        },
        {
            "title": "Уровень сладости",
            "values": [
                {"value": "Без сахара", "additional_cost": 0},
                {"value": "Мало сахара", "additional_cost": 0},
                {"value": "Нормально", "additional_cost": 0},
                {"value": "Сладко", "additional_cost": 0}
            ]
        }
    ]
}


@transaction.atomic
def import_products():
    """Импортирует продукты, категории и опции"""
    created_counts = {
        "categories": 0,
        "subcategories": 0,
        "products": 0,
        "option_types": 0,
        "option_values": 0,
    }

    # Создаем типы опций и их значения
    option_types_map = {}
    if "option_types" in PRODUCTS_DATA:
        print("Создание типов опций...")
        for opt_type_data in PRODUCTS_DATA["option_types"]:
            option_type, created = OptionType.objects.get_or_create(
                title=opt_type_data["title"]
            )
            if created:
                created_counts["option_types"] += 1
                print(f"  ✓ Создан тип опции: {option_type.title}")
            else:
                print(f"  - Тип опции уже существует: {option_type.title}")
            
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
    print("\nСоздание категорий и продуктов...")
    for category_data in PRODUCTS_DATA["categories"]:
        category, created = Category.objects.get_or_create(
            title=category_data["title"]
        )
        if created:
            created_counts["categories"] += 1
            print(f"\n✓ Создана категория: {category.title}")
        else:
            print(f"\n- Категория уже существует: {category.title}")

        for subcategory_data in category_data["subcategories"]:
            subcategory, created = Subcategory.objects.get_or_create(
                title=subcategory_data["title"],
                category=category
            )
            if created:
                created_counts["subcategories"] += 1
                print(f"  ✓ Создана подкатегория: {subcategory.title}")
            else:
                print(f"  - Подкатегория уже существует: {subcategory.title}")

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
                        "image": "products/larry.jpg",  # Используем larry.jpg для всех продуктов
                    }
                )
                # Обновляем изображение для существующих продуктов тоже
                if not created:
                    product.price = product_data["price"]
                    product.description = product_data["description"]
                    product.bonus_percent = product_data.get("bonus_percent", 5.0)
                    product.has_options = product_data.get("has_options", False)
                    product.image = "products/larry.jpg"
                    product.save()
                    print(f"    - Обновлен продукт: {product.title} ({product.price} сом)")
                else:
                    created_counts["products"] += 1
                    print(f"    ✓ Создан продукт: {product.title} ({product.price} сом)")

                # Связываем опции с продуктом, если указаны
                if product_data.get("has_options") and product_data.get("option_type_titles"):
                    for option_type_title in product_data["option_type_titles"]:
                        if option_type_title in option_types_map:
                            ProductOptionType.objects.get_or_create(
                                product=product,
                                option_type=option_types_map[option_type_title]
                            )

    # Выводим итоги
    print("\n" + "="*50)
    print("Импорт завершен!")
    print("="*50)
    print(f"Создано категорий: {created_counts['categories']}")
    print(f"Создано подкатегорий: {created_counts['subcategories']}")
    print(f"Создано продуктов: {created_counts['products']}")
    print(f"Создано типов опций: {created_counts['option_types']}")
    print(f"Создано значений опций: {created_counts['option_values']}")


# Запускаем импорт
if __name__ == "__main__" or __name__ == "__builtin__":
    import_products()

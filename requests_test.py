
from apps.menu.models import Category, Subcategory, Product, OptionType, OptionValue, ProductOptionType

# 1. Категории и подкатегории
categories_data = [
    ("Напитки", ["Кофе", "Холодное"]),
    ("Еда", ["Выпечка", "Завтрак"]),
]

categories = {}
subcategories = {}

for cat_title, subcats in categories_data:
    category, _ = Category.objects.get_or_create(title=cat_title)
    categories[cat_title] = category

    for subcat_title in subcats:
        subcategory, _ = Subcategory.objects.get_or_create(
            title=subcat_title,
            category=category
        )
        subcategories[subcat_title] = subcategory

# 2. Продукты
products_data = {
    "Кофе": [
        ("Эспрессо", 120, "Крепкий кофе", "products/espresso.jpg", True),
        ("Американо", 150, "Кофе с водой", "products/americano.jpg", True),
        ("Капучино", 180, "Кофе с молоком", "products/cappuccino.jpg", True),
        ("Латте", 200, "Кофе с большим количеством молока", "products/latte.jpg", True),
        ("Мокка", 220, "Кофе с шоколадом", "products/mocha.jpg", True),
    ],
    "Холодное": [
        ("Мохито", 250, "Освежающий напиток с мятой", "products/mojito.jpg", False),
        ("Лимонад", 180, "Лимонный напиток", "products/lemonade.jpg", False),
        ("Фраппе", 220, "Холодный кофе", "products/frappe.jpg", False),
        ("Милкшейк", 200, "Молочный коктейль", "products/milkshake.jpg", False),
        ("Смузи", 230, "Фруктовый напиток", "products/smoothie.jpg", False),
    ],
    "Выпечка": [
        ("Круассан", 150, "Слоёная выпечка", "products/croissant.jpg", False),
        ("Пончик", 120, "Сладкая выпечка", "products/donut.jpg", False),
        ("Маффин", 130, "Шоколадный маффин", "products/muffin.jpg", False),
        ("Пирог с яблоками", 200, "Домашний пирог", "products/apple_pie.jpg", False),
        ("Хачапури", 250, "Сырная выпечка", "products/khachapuri.jpg", False),
    ],
    "Завтрак": [
        ("Омлет", 180, "Яичный омлет", "products/omelette.jpg", False),
        ("Блины", 150, "Блины с медом", "products/pancakes.jpg", False),
        ("Каша овсяная", 120, "Овсянка на молоке", "products/oatmeal.jpg", False),
        ("Тост с авокадо", 200, "Хлеб, авокадо", "products/avocado_toast.jpg", False),
        ("Йогурт с фруктами", 170, "Йогурт и фрукты", "products/yogurt.jpg", False),
    ],
}

for subcat_title, products in products_data.items():
    subcategory = subcategories[subcat_title]
    for title, price, desc, img, has_opts in products:
        Product.objects.get_or_create(
            title=title,
            price=price,
            description=desc,
            image=img,
            subcategory=subcategory,
            has_options=has_opts,
            is_active=True
        )

# 3. Опции только для кофе
coffee_products = subcategories["Кофе"].products.all()

option_types_data = {
    "Объем": ["200 мл", "300 мл", "400 мл"],
    "Вид молока": ["Обычное", "Безлактозное", "Соевое", "Миндальное"],
    "Уровень сладости": ["Без сахара", "Мало сахара", "Нормально", "Сладко"],
}

for opt_type_title, values in option_types_data.items():
    option_type, _ = OptionType.objects.get_or_create(title=opt_type_title)

    for val in values:
        OptionValue.objects.get_or_create(type=option_type, value=val)

    for product in coffee_products:
        ProductOptionType.objects.get_or_create(
            product=product,
            option_type=option_type
        )

print("✅ Данные успешно добавлены!")

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.cart.models import Cart, CartItem, CartItemOption
from apps.menu.models import Product, OptionValue


User = get_user_model()
from apps.menu.models import Subcategory, Category

class TestCartAPI(APITestCase):
    def setUp(self):
        """Настройка данных для тестов."""
        # Создаем тестового пользователя
        self.user = User.objects.create_user(phone_number="+996123123123", password="testpassword")
        self.client.login(phone_number="+996123123123", password="testpassword")

        # Создаем тестовую категорию и подкатегорию
        self.category = Category.objects.create(title="Напитки")
        self.subcategory = Subcategory.objects.create(title="Горячие напитки", category=self.category)

        # Создаем тестовые данные: продукт, опции, корзину
        self.product = Product.objects.create(title="Кофе", price=100, subcategory=self.subcategory)
        self.option1 = OptionValue.objects.create(type="Объем", value="0.4 литра", additional_cost=50)
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)

    def test_get_cart(self):
        """Тест: Проверка получения корзины."""
        response = self.client.get("/cart/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("items", response.data)
        self.assertEqual(len(response.data["items"]), 1)

    def test_add_item_to_cart(self):
        """Тест: Проверка добавления товара в корзину."""
        payload = {
            "product_id": self.product.id,
            "quantity": 2,
            "options": [self.option1.id],
        }
        response = self.client.post("/cart/item/", data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
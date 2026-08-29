from rest_framework import status
from rest_framework.test import APITestCase

from apps.menu.models import Category, Subcategory, Product
from apps.order.models import Cafe
from apps.order.models.code import Order, OrderItem
from apps.users.models.user import User


class OrderListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+996700000003", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.cafe = Cafe.objects.create(name="Test Cafe", is_active=True)

        category = Category.objects.create(title="Напитки")
        subcategory = Subcategory.objects.create(title="Кофе", category=category)
        self.espresso = Product.objects.create(
            title="Эспрессо",
            price=120,
            description="Крепкий кофе",
            subcategory=subcategory,
        )
        self.latte = Product.objects.create(
            title="Латте",
            price=200,
            description="Кофе с молоком",
            subcategory=subcategory,
        )

        self.order = Order.objects.create(
            user=self.user,
            cafe=self.cafe,
            status="delivered",
            delivery_type="pickup",
            total_price=520,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.espresso,
            quantity=1,
            product_options={"options": [], "comment": ""},
            final_price=120,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.latte,
            quantity=2,
            product_options={"options": [], "comment": "Без сахара"},
            final_price=400,
        )

    def test_order_history_includes_products(self):
        response = self.client.get("/api/v1/orders/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = response.data["results"][0]
        self.assertEqual(order_data["id"], self.order.id)
        self.assertEqual(len(order_data["items"]), 2)

        titles = {item["product"]["title"] for item in order_data["items"]}
        self.assertEqual(titles, {"Эспрессо", "Латте"})

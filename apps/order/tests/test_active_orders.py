from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.order.models.code import Order, Cafe
from apps.users.models.user import User


class ActiveOrderListViewTests(APITestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            phone_number="+996700000001",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        # Создаем кафе
        self.cafe = Cafe.objects.create(
            name="Test Cafe",
            is_active=True
        )

        # Создаем заказы с разными статусами
        self.order_accepted = Order.objects.create(
            user=self.user,
            cafe=self.cafe,
            status="accepted",
            delivery_type="pickup",
            total_price=100
        )
        self.order_ready = Order.objects.create(
            user=self.user,
            cafe=self.cafe,
            status="ready",
            delivery_type="delivery",
            address="Test address",
            total_price=200
        )
        self.order_on_the_way = Order.objects.create(
            user=self.user,
            cafe=self.cafe,
            status="on_the_way",
            delivery_type="delivery",
            address="Test address",
            total_price=300
        )
        self.order_delivered = Order.objects.create(
            user=self.user,
            cafe=self.cafe,
            status="delivered",
            delivery_type="pickup",
            total_price=400
        )

        # Создаем заказ другого пользователя (не должен показываться)
        self.other_user = User.objects.create_user(
            phone_number="+996700000002",
            password="testpass123"
        )
        self.other_order_accepted = Order.objects.create(
            user=self.other_user,
            cafe=self.cafe,
            status="accepted",
            delivery_type="pickup",
            total_price=500
        )

    def test_active_orders_requires_authentication(self):
        """Тест: неаутентифицированный пользователь не имеет доступа"""
        self.client.logout()
        url = reverse("active-orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_active_orders_returns_only_active_statuses(self):
        """Тест: возвращаются только заказы со статусами accepted, ready, on_the_way"""
        url = reverse("active-orders")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что в ответе только активные заказы текущего пользователя
        order_ids = [order["id"] for order in response.data["results"]]
        self.assertIn(self.order_accepted.id, order_ids)
        self.assertIn(self.order_ready.id, order_ids)
        self.assertIn(self.order_on_the_way.id, order_ids)
        
        # Проверяем, что доставленный заказ не входит
        self.assertNotIn(self.order_delivered.id, order_ids)
        
        # Проверяем, что заказ другого пользователя не входит
        self.assertNotIn(self.other_order_accepted.id, order_ids)

    def test_active_orders_ordering(self):
        """Тест: заказы отсортированы по убыванию даты создания"""
        url = reverse("active-orders")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        order_ids = [order["id"] for order in response.data["results"]]
        # Самый новый должен быть первым (on_the_way создан последним в setUp)
        self.assertEqual(order_ids[0], self.order_on_the_way.id)
        self.assertEqual(order_ids[1], self.order_ready.id)
        self.assertEqual(order_ids[2], self.order_accepted.id)

    def test_active_orders_pagination(self):
        """Тест: пагинация работает корректно"""
        # Создаем дополнительные активные заказы для теста пагинации
        for i in range(5):
            Order.objects.create(
                user=self.user,
                cafe=self.cafe,
                status="accepted",
                delivery_type="pickup",
                total_price=100 + i
            )

        url = reverse("active-orders")
        response = self.client.get(url, {"page": 1, "page_size": 3})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["count"], 8)  # 3 из setUp + 5 новых

    def test_active_orders_empty_when_no_active_orders(self):
        """Тест: пустой список когда нет активных заказов"""
        # Удаляем все активные заказы пользователя
        Order.objects.filter(
            user=self.user,
            status__in=["accepted", "ready", "on_the_way"]
        ).delete()

        url = reverse("active-orders")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_active_orders_serializer_fields(self):
        """Тест: проверяем, что все необходимые поля присутствуют в ответе"""
        url = reverse("active-orders")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)
        
        order_data = response.data["results"][0]
        expected_fields = [
            "id", "status", "delivery_type", "address", 
            "delivery_time", "total_price", "created_at", "items"
        ]
        for field in expected_fields:
            self.assertIn(field, order_data)
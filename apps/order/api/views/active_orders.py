from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.api.pagination import OrderPageNumberPagination
from apps.order.api.serializers.code import OrderSerializer
from apps.order.models.code import Order
from arabica.api_utils import api_error


class ActiveOrderListView(APIView):
    """
    Список активных заказов текущего пользователя.
    Активные заказы - это заказы со статусами: accepted, ready, on_the_way
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Список активных заказов пользователя",
        tags=["Order"],
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Номер страницы",
                required=False,
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Количество элементов на странице (макс. 100)",
                required=False,
            ),
        ],
        responses={
            200: OrderSerializer(many=True),
            400: OpenApiResponse(description="Неверный запрос"),
        }
    )
    def get(self, request):
        # Получаем активные статусы
        active_statuses = ["accepted", "ready", "on_the_way"]
        
        # Фильтруем заказы пользователя по активным статусам
        orders = Order.objects.filter(
            user=request.user,
            status__in=active_statuses
        ).order_by("-created_at")
        
        paginator = OrderPageNumberPagination()
        page = paginator.paginate_queryset(orders, request, view=self)
        serializer = OrderSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
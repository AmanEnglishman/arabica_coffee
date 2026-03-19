from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.api.pagination import OrderPageNumberPagination
from apps.order.api.permissions import IsCourier
from apps.order.api.serializers.code import CourierOrderSerializer
from apps.order.models import Order
from arabica.api_utils import api_error


class CourierOrderListView(APIView):
    """
    Кабинет курьера: видит только свои "on_the_way" заказы.
    """

    permission_classes = [IsAuthenticated, IsCourier]

    @extend_schema(
        summary="Список заказов курьера",
        tags=["Courier"],
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="По умолчанию on_the_way",
            ),
        ],
        responses={200: CourierOrderSerializer(many=True)},
    )
    def get(self, request):
        desired_status = request.query_params.get("status") or "on_the_way"
        allowed = {s[0] for s in Order.ORDER_STATUS}
        if desired_status not in allowed:
            return api_error(
                code="invalid_status",
                message="Неверный статус.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        orders_qs = (
            Order.objects.filter(courier=request.user, status=desired_status)
            .order_by("-created_at")
        )

        paginator = OrderPageNumberPagination()
        page = paginator.paginate_queryset(orders_qs, request, view=self)
        serializer = CourierOrderSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CourierDeliverView(APIView):
    """
    on_the_way -> delivered (курьер подтверждает доставку)
    """

    permission_classes = [IsAuthenticated, IsCourier]

    @extend_schema(
        summary="Доставлено: on_the_way -> delivered",
        tags=["Courier"],
        responses={200: CourierOrderSerializer},
        request=None,
    )
    def post(self, request, order_id: int):
        order = get_object_or_404(
            Order, id=order_id, courier=request.user
        )

        if order.status != "on_the_way":
            return api_error(
                code="invalid_transition",
                message="Заказ не в статусе on_the_way.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if order.delivery_type != "delivery":
            return api_error(
                code="invalid_transition",
                message="deliver доступен только для delivery.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            order.status = "delivered"
            order.delivered_at = timezone.now()
            order.save(update_fields=["status", "delivered_at"])

        serializer = CourierOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


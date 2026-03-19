from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.api.pagination import OrderPageNumberPagination
from apps.order.api.permissions import IsCafeStaff
from apps.order.api.serializers.code import CafeOrderSerializer
from apps.order.models import CafeMembership, Order
from arabica.api_utils import api_error


class AssignCourierSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField()


class CafeOrderListView(APIView):
    """
    Кабинет кафе: видит заказы только своего филиала.
    """

    permission_classes = [IsAuthenticated, IsCafeStaff]

    @extend_schema(
        summary="Список заказов кафе",
        tags=["Cafe"],
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
                description="Фильтр по статусу (accepted/ready/on_the_way/delivered)",
            ),
        ],
        responses={200: CafeOrderSerializer(many=True)},
    )
    def get(self, request):
        membership = request.user.cafe_membership
        orders_qs = Order.objects.filter(cafe=membership.cafe).order_by("-created_at")

        status_filter = request.query_params.get("status")
        if status_filter:
            allowed = {s[0] for s in Order.ORDER_STATUS}
            if status_filter not in allowed:
                return api_error(
                    code="invalid_status",
                    message="Неверный статус.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            orders_qs = orders_qs.filter(status=status_filter)

        paginator = OrderPageNumberPagination()
        page = paginator.paginate_queryset(orders_qs, request, view=self)
        serializer = CafeOrderSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CafeMarkReadyView(APIView):
    """
    accepted -> ready (кафе готовит заказ)
    """

    permission_classes = [IsAuthenticated, IsCafeStaff]

    @extend_schema(
        summary="Заказ готов: accepted -> ready",
        tags=["Cafe"],
        responses={200: CafeOrderSerializer},
        request=None,
    )
    def post(self, request, order_id: int):
        membership = request.user.cafe_membership
        order = get_object_or_404(Order, id=order_id, cafe=membership.cafe)

        if order.status != "accepted":
            return api_error(
                code="invalid_transition",
                message="Нельзя перевести заказ в ready из текущего статуса.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            order.status = "ready"
            order.ready_at = timezone.now()
            order.save(update_fields=["status", "ready_at"])

        serializer = CafeOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CafeAssignCourierView(APIView):
    """
    ready -> on_the_way (кафе назначает курьера)
    """

    permission_classes = [IsAuthenticated, IsCafeStaff]

    @extend_schema(
        summary="Назначить курьера: ready -> on_the_way",
        tags=["Cafe"],
        request=AssignCourierSerializer,
        responses={200: CafeOrderSerializer},
    )
    def post(self, request, order_id: int):
        membership = request.user.cafe_membership
        order = get_object_or_404(Order, id=order_id, cafe=membership.cafe)

        serializer = AssignCourierSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        courier_id = serializer.validated_data["courier_id"]

        if order.status != "ready" or order.delivery_type != "delivery":
            return api_error(
                code="invalid_transition",
                message="Нельзя назначить курьера на текущем этапе.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        courier_membership = get_object_or_404(
            CafeMembership,
            user_id=courier_id,
            role=CafeMembership.Role.COURIER,
            cafe_id=order.cafe_id,
        )

        with transaction.atomic():
            order.courier = courier_membership.user
            order.status = "on_the_way"
            order.on_the_way_at = timezone.now()
            order.save(update_fields=["courier", "status", "on_the_way_at"])

        serializer = CafeOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CafeMarkDeliveredView(APIView):
    """
    ready -> delivered (кафе выдает самовывоз)
    """

    permission_classes = [IsAuthenticated, IsCafeStaff]

    @extend_schema(
        summary="Выдано самовывоз: ready -> delivered",
        tags=["Cafe"],
        responses={200: CafeOrderSerializer},
        request=None,
    )
    def post(self, request, order_id: int):
        membership = request.user.cafe_membership
        order = get_object_or_404(Order, id=order_id, cafe=membership.cafe)

        if order.status != "ready" or order.delivery_type != "pickup":
            return api_error(
                code="invalid_transition",
                message="Нельзя перевести заказ в delivered для pickup из текущего этапа.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            order.status = "delivered"
            order.delivered_at = timezone.now()
            order.save(update_fields=["status", "delivered_at"])

        serializer = CafeOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


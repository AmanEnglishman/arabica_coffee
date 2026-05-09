from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bonus.api.serializers.loyalty import (
    SpendLoyaltyPointsResponseSerializer,
    SpendLoyaltyPointsSerializer,
)
from arabica.api_utils import api_error

User = get_user_model()


@extend_schema(
    summary="Списать бонусные баллы",
    tags=["Bonus"],
    request=SpendLoyaltyPointsSerializer,
    responses={
        200: SpendLoyaltyPointsResponseSerializer,
        400: OpenApiResponse(description="Недостаточно баллов или неверные данные"),
    },
    description=(
        "Клиент списывает свои бонусные баллы. "
        "1 балл = 1 сом скидки. "
        "Для применения скидки при создании заказа используйте поле "
        "`use_bonus_points` в POST /api/v1/orders/create/."
    ),
    examples=[
        OpenApiExample(
            "Списать 200 баллов",
            value={"points": 200},
            request_only=True,
        ),
        OpenApiExample(
            "Успешный ответ",
            value={
                "message": "Списано 200 баллов.",
                "spent_points": 200,
                "remaining_points": 350,
            },
            response_only=True,
        ),
    ],
)
class SpendLoyaltyPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SpendLoyaltyPointsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        points = serializer.validated_data["points"]

        with transaction.atomic():
            user = User.objects.select_for_update().get(id=request.user.id)
            if user.loyalty_points < points:
                return api_error(
                    code="insufficient_points",
                    message=(
                        f"Недостаточно баллов. "
                        f"Доступно: {user.loyalty_points}, запрошено: {points}."
                    ),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            user.loyalty_points -= points
            user.save(update_fields=["loyalty_points"])

        return Response(
            SpendLoyaltyPointsResponseSerializer({
                "message":          f"Списано {points} баллов.",
                "spent_points":     points,
                "remaining_points": user.loyalty_points,
            }).data
        )

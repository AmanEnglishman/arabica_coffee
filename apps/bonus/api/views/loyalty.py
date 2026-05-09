from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bonus.api.serializers import AddCoffeeCupSerializer, AddLoyaltyPointsSerializer
from apps.bonus.api.serializers.loyalty import (
    AddLoyaltyPointsResponseSerializer,
    AddCoffeeCupResponseSerializer,
)
from apps.users.models import User
from arabica.api_utils import api_error


@extend_schema(
    summary="Начислить бонусные баллы клиенту",
    tags=["Courier"],
    request=AddLoyaltyPointsSerializer,
    responses={
        200: AddLoyaltyPointsResponseSerializer,
        400: OpenApiResponse(description="Неверные данные"),
        403: OpenApiResponse(description="Доступ только для курьеров"),
        404: OpenApiResponse(description="Пользователь не найден"),
    },
    examples=[
        OpenApiExample(
            "Начислить 100 баллов",
            value={"user_id": 5, "points": 100},
            request_only=True,
        )
    ],
)
class AddLoyaltyPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_courier:
            return api_error(code="forbidden", message="Нет прав доступа.", status_code=403)

        serializer = AddLoyaltyPointsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        points  = int(serializer.validated_data["points"])

        with transaction.atomic():
            user = User.objects.select_for_update().get(id=user_id)
            user.loyalty_points += points
            user.save(update_fields=["loyalty_points"])

        name = f"{user.first_name} {user.last_name}".strip() or user.phone_number
        return Response(
            AddLoyaltyPointsResponseSerializer({
                "message": f"{points} баллов начислено пользователю {name}.",
                "total_loyalty_points": user.loyalty_points,
            }).data
        )


@extend_schema(
    summary="Добавить чашку кофе клиенту",
    tags=["Courier"],
    request=AddCoffeeCupSerializer,
    responses={
        200: AddCoffeeCupResponseSerializer,
        403: OpenApiResponse(description="Доступ только для курьеров"),
        404: OpenApiResponse(description="Пользователь не найден"),
    },
    description=(
        "Добавляет 1 чашку кофе клиенту. "
        "После 6 чашек счётчик сбрасывается и клиент получает бесплатную чашку."
    ),
)
class AddCoffeeCupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_courier:
            return api_error(code="forbidden", message="Нет прав доступа.", status_code=403)

        serializer = AddCoffeeCupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data["user_id"]

        with transaction.atomic():
            user = User.objects.select_for_update().get(id=user_id)
            user.coffee_cups += 1
            if user.coffee_cups >= 6:
                user.coffee_cups = 0
                message = "Пользователь получил бесплатную чашку кофе! 🎉"
            else:
                message = f"Чашка кофе добавлена. До бесплатной — {6 - user.coffee_cups}."
            user.save(update_fields=["coffee_cups"])

        return Response(
            AddCoffeeCupResponseSerializer({
                "message": message,
                "current_coffee_cups": user.coffee_cups,
            }).data
        )

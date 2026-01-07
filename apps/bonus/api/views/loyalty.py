from drf_spectacular.utils import extend_schema
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bonus.api.serializers import AddCoffeeCupSerializer, AddLoyaltyPointsSerializer
from apps.users.models import User

@extend_schema(
    summary='Добавление бонусных баллов',
    tags=["Courier"],
    request=AddLoyaltyPointsSerializer,
)
class AddLoyaltyPointsView(APIView):
    """
    Курьер начисляет бонусные баллы пользователю.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_courier:
            return Response({"error": "Нет прав доступа."}, status=403)

        serializer = AddLoyaltyPointsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data["user_id"]
        points = serializer.validated_data["points"]

        user = get_object_or_404(User, id=user_id)
        user.loyalty_points += int(points)
        user.save()

        return Response({
            "message": f"{points} баллов начислено пользователю {user.first_name} {user.last_name}.",
            "total_loyalty_points": user.loyalty_points
        })

@extend_schema(
    summary='Добавление чашек кофе',
    tags=["Courier"],
    request=AddCoffeeCupSerializer,
)
class AddCoffeeCupView(APIView):
    """
    Курьер добавляет чашку кофе пользователю.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_courier:
            return Response({"error": "Нет прав доступа."}, status=403)

        serializer = AddCoffeeCupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data["user_id"]

        user = get_object_or_404(User, id=user_id)
        user.coffee_cups += 1

        if user.coffee_cups == 6:
            user.coffee_cups = 0
            message = "Пользователь получил бесплатную чашку кофе!"
        else:
            message = f"Чашка кофе добавлена. До бесплатной — {6 - user.coffee_cups}."

        user.save()

        return Response({
            "message": message,
            "current_coffee_cups": user.coffee_cups
        })
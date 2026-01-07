from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.bonus.api.serializers import ScanQRCodeSerializer
from apps.users.models import User

@extend_schema(
    summary="Сканирование qr-code для курьера",
    tags=["Courier"],
    request=ScanQRCodeSerializer,
)
class ScanQRCodeView(APIView):
    """
    Курьер сканирует QR-код.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_courier:
            return Response({"error": "Нет прав доступа."}, status=403)

        serializer = ScanQRCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qr_code_data = serializer.validated_data["qr_code_data"]

        user = get_object_or_404(User, qr_code=qr_code_data)

        return Response({
            "user_id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "loyalty_points": user.loyalty_points,
            "coffee_cups": user.coffee_cups
        })
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.users.models import User

@extend_schema(summary="Сканирование qr-code для курьера", tags=["Courier"])
class ScanQRCodeView(APIView):
    """
    Курьер сканирует QR-код.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_courier:
            return Response({"error": "Нет прав доступа."}, status=403)

        qr_code_data = request.data.get("qr_code_data")
        if not qr_code_data:
            return Response({"error": "QR-код не передан."}, status=400)

        user = get_object_or_404(User, qr_code=qr_code_data)

        return Response({
            "user_id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "loyalty_points": user.loyalty_points,
            "coffee_cups": user.coffee_cups
        })
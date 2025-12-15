from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.api.serializers import SendCodeSerializer

User = get_user_model()


@extend_schema(
    summary="Send code to phone number",
    tags=["Authentication"],
)
class SendCodeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SendCodeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data["phone_number"]

        # Создаем пользователя или ищем существующего
        user, created = User.objects.get_or_create(phone_number=phone_number)

        # Генерируем код (пока заглушка)
        code = "111111"

        # Сохраняем код в Redis с TTL = 120 секунд
        cache.set(f"verify_code:{phone_number}", code, timeout=120)

        return Response(
            {
                "success": True,
                "message": "Код отправлен (пока заглушка, всегда 111111)",
                "is_new_user": created,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Verify code for phone number",
    tags=["Authentication"],
)
class VerifyCodeView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        code = request.data.get("code")

        if not phone_number or not code:
            return Response(
                {"success": False, "message": "Номер телефона и код обязательны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Достаём код из Redis
        stored_code = cache.get(f"verify_code:{phone_number}")

        if not stored_code or stored_code != code:
            return Response(
                {"success": False, "message": "Неверный или просроченный код"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Генерация токенов
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Код больше не нужен → удаляем из Redis
        cache.delete(f"verify_code:{phone_number}")

        return Response(
            {
                "success": True,
                "message": "Код успешно подтвержден",
                "access": str(access),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

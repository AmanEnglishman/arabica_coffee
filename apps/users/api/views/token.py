from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,)

from ..serializers.token import (CustomTokenObtainPairSerializer,
                                 CustomTokenRefreshSerializer,)

@extend_schema(summary="Check JWT token status", tags=["Tokens"])
class CheckTokenStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response(
                    {"status": "error", "message": "Token is missing"}, status=400
                )

            token = auth_header.split(" ")[1]

            AccessToken(token)

            return Response(
                {"status": "valid", "message": "Token is valid"}, status=200
            )
        except (TokenError, InvalidToken):
            return Response(
                {"status": "invalid", "message": "Invalid or expired token"}, status=401
            )


@extend_schema(summary="Obtain JWT token pair", tags=["Tokens"])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(summary="Refresh JWT token pair", tags=["Tokens"])
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

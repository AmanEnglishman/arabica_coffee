from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bonus.api.serializers.information import InformationSerializer

@extend_schema(
    summary="Информация о бонусах и чашках кофе",
    tags=["Bonus"],
    responses={
        200: OpenApiResponse(
            description="Информация о бонусах и чашках кофе текущего пользователя",
            response=InformationSerializer
        ),
        403: OpenApiResponse(description="Нет прав доступа"),
    }
)
class InformationAboutBonusList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = InformationSerializer(request.user)
        return Response(serializer.data)

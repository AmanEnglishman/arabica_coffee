from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bonus.api.serializers.information import InformationSerializer


@extend_schema(summary="Информация о бонусах и чашках кофе", tags=["Bonus"])
class InformationAboutBonusList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = InformationSerializer(request.user)
        return Response(serializer.data)

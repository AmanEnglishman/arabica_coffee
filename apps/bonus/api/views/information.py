from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.bonus.api.serializers.information import InformationSerializer
from rest_framework.views import APIView

from apps.users.models import User

@extend_schema(summary="Информация о бонусе и чашки кофе", tags=["Bonus"])
class InformationAboutBonusList(APIView):
    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        serializer = InformationSerializer(user)
        return Response(serializer.data)

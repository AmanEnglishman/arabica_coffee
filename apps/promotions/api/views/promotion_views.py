from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.promotions.models import Promotion
from apps.promotions.api.serializers import PromotionListSerializer, PromotionDetailSerializer
from apps.promotions.api.pagination import PromotionPageNumberPagination


class PromotionListView(ListAPIView):
    queryset = Promotion.objects.filter(is_active=True).order_by("-published_at")
    serializer_class = PromotionListSerializer
    permission_classes = [AllowAny]
    pagination_class = PromotionPageNumberPagination

    @extend_schema(
        tags=["Promotions"],
        summary="Получить список акций",
        description="Возвращает список активных акций и скидок, отсортированных по дате публикации (от новых к старым).",
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Номер страницы",
                required=False,
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Количество элементов на странице",
                required=False,
            ),
        ],
        responses={200: PromotionListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PromotionDetailView(RetrieveAPIView):
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    @extend_schema(
        tags=["Promotions"],
        summary="Получить детальную информацию об акции",
        description="Возвращает полную информацию о конкретной акции по её ID.",
        responses={
            200: PromotionDetailSerializer,
            404: {"description": "Акция не найдена"},
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
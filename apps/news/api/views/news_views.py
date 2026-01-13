from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.news.models import News
from apps.news.api.serializers import NewsListSerializer, NewsDetailSerializer
from apps.news.api.pagination import NewsPageNumberPagination


class NewsListView(ListAPIView):
    queryset = News.objects.filter(is_active=True).order_by("-published_at")
    serializer_class = NewsListSerializer
    permission_classes = [AllowAny]
    pagination_class = NewsPageNumberPagination

    @extend_schema(
        tags=["News"],
        summary="Получить список новостей",
        description="Возвращает список активных новостей, отсортированных по дате публикации (от новых к старым).",
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
        responses={200: NewsListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NewsDetailView(RetrieveAPIView):
    queryset = News.objects.filter(is_active=True)
    serializer_class = NewsDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    @extend_schema(
        tags=["News"],
        summary="Получить детальную информацию о новости",
        description="Возвращает полную информацию о конкретной новости по её ID.",
        responses={
            200: NewsDetailSerializer,
            404: {"description": "Новость не найдена"},
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
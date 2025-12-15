from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.menu.api.serializers import CategorySerializer, ProductSerializer, ProductSearchSerializers
from apps.menu.models import Category, Product

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@extend_schema(summary="Основной каталог меню", tags=["Menu"])
@method_decorator(cache_page(60 * 15), name='dispatch')  # Кэш на 15 минут
class MenuAPIView(generics.ListAPIView):
    queryset = Category.objects.prefetch_related('subcategories__products')
    serializer_class = CategorySerializer


@extend_schema(summary="Детальный просмотр продукта по id", tags=["Menu"])
@method_decorator(cache_page(60 * 5), name='dispatch')  # Кэш на 5 минут
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.only('id', 'title', 'image', 'price')
    serializer_class = ProductSerializer
    lookup_field = 'pk'


@extend_schema(summary="Поиск продуктов по названию (регистронезависимый)", tags=["Menu"])
@method_decorator(cache_page(60 * 10), name='dispatch')  # Кэш на 10 минут
class ProductSearchAPIView(generics.ListAPIView):
    serializer_class = ProductSearchSerializers

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        if search_query:
            return Product.objects.filter(title__icontains=search_query)
        return Product.objects.all()
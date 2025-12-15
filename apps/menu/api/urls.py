from django.urls import path
from .views import ProductDetailAPIView, ProductSearchAPIView, MenuAPIView

urlpatterns = [
    path('', MenuAPIView.as_view(), name='menu'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('search/', ProductSearchAPIView.as_view(), name='product-search')
]
